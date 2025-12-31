"""
IEEE 1584-2018 Arc Flash Boundary Calculations
===============================================

Implements:
- Equations (7)-(9): Intermediate AFB at 600V, 2700V, 14300V
- Equation (10): AFB for LV systems (Voc <= 600V)
- Equations (22)-(24): Interpolation for MV systems (600V < Voc <= 15kV)

The arc flash boundary is the distance at which incident energy equals
5.0 J/cm² (1.2 cal/cm²).

Reference: IEEE 1584-2018, Sections 4.7, 4.9
"""

import math
from typing import Tuple

from .constants import ElectrodeConfig, AFB_THRESHOLD_J_CM2, INCHES_TO_MM
from .tables import get_energy_coefficients


def _build_afb_numerator(
    iarc_ref_ka: float,
    iarc_final_ka: float,
    ibf_ka: float,
    gap_mm: float,
    arc_duration_ms: float,
    correction_factor: float,
    config: ElectrodeConfig,
    voltage_ref: int
) -> float:
    """
    Build the numerator for the AFB equation.
    
    The AFB equation is derived from the energy equation by solving for D
    when E = threshold (5.0 J/cm²).
    
    numerator = k1 + k2*lg(G) + k3*lg(Iarc_ref) + f(Ibf) + 
                k11*lg(Ibf) + k13*lg(Iarc_final) + lg(1/CF) - lg(threshold_factor)
    
    Args:
        iarc_ref_ka: Reference arcing current for k3 term (kA)
        iarc_final_ka: Final arcing current for k13 term (kA)
        ibf_ka: Bolted fault current (kA)
        gap_mm: Gap between electrodes (mm)
        arc_duration_ms: Arc duration (ms)
        correction_factor: Enclosure size CF
        config: Electrode configuration
        voltage_ref: Reference voltage (600, 2700, or 14300)
    
    Returns:
        Numerator value
    """
    k = get_energy_coefficients(config, voltage_ref)
    
    numerator = k["k1"]
    numerator += k["k2"] * math.log10(gap_mm)
    numerator += k["k3"] * math.log10(iarc_ref_ka)
    
    # Polynomial f(Ibf)
    # TODO: Verify polynomial structure matches incident_energy.py
    f_ibf = (
        k["k4"] * ibf_ka**7 +
        k["k5"] * ibf_ka**6 +
        k["k6"] * ibf_ka**5 +
        k["k7"] * ibf_ka**4 +
        k["k8"] * ibf_ka**3 +
        k["k9"] * ibf_ka**2 +
        k["k10"] * ibf_ka
    )
    numerator += f_ibf
    
    numerator += k["k11"] * math.log10(ibf_ka)
    numerator += k["k13"] * math.log10(iarc_final_ka)
    
    # lg(1/CF)
    if correction_factor > 0:
        numerator += math.log10(1.0 / correction_factor)
    
    # Threshold factor: lg(threshold / ((12.552/50) * T))
    # From E = (12.552/50) * T * 10^exp, solving for D at E = threshold
    # threshold = (12.552/50) * T * 10^(numerator + k12*lg(D))
    # 10^(numerator + k12*lg(D)) = threshold / ((12.552/50) * T)
    # numerator + k12*lg(D) = lg(threshold / ((12.552/50) * T))
    # k12*lg(D) = lg(threshold / ((12.552/50) * T)) - numerator
    # lg(D) = (lg(threshold / ((12.552/50) * T)) - numerator) / k12
    # 
    # Rearranging: lg(D) = (numerator - lg(threshold_factor)) / (-k12)
    # where threshold_factor = (12.552/50) * T / threshold
    threshold_factor = (12.552 / 50.0) * arc_duration_ms / AFB_THRESHOLD_J_CM2
    numerator -= math.log10(threshold_factor)
    
    return numerator


def equations_7_8_9_intermediate_afb(
    iarc_ref_ka: float,
    iarc_final_ka: float,
    ibf_ka: float,
    gap_mm: float,
    arc_duration_ms: float,
    correction_factor: float,
    config: ElectrodeConfig,
    voltage_ref: int
) -> float:
    """
    Calculate intermediate arc flash boundary at reference voltage.
    
    IEEE 1584-2018 Equations (7), (8), (9):
        AFB = 10^(numerator / (-k12))
    
    Args:
        iarc_ref_ka: Reference arcing current for k3 term (kA)
        iarc_final_ka: Final arcing current for k13 term (kA)
        ibf_ka: Bolted fault current (kA)
        gap_mm: Gap between electrodes (mm)
        arc_duration_ms: Arc duration (ms)
        correction_factor: Enclosure size CF
        config: Electrode configuration
        voltage_ref: Reference voltage (600, 2700, or 14300)
    
    Returns:
        Arc flash boundary (mm)
    """
    k = get_energy_coefficients(config, voltage_ref)
    
    numerator = _build_afb_numerator(
        iarc_ref_ka, iarc_final_ka, ibf_ka, gap_mm, arc_duration_ms,
        correction_factor, config, voltage_ref
    )
    
    # AFB = 10^(numerator / (-k12))
    if abs(k["k12"]) < 1e-10:
        return 0.0  # Avoid division by zero
    
    afb = 10 ** (numerator / (-k["k12"]))
    return afb


def equation_10_lv_afb(
    iarc_600_ka: float,
    iarc_final_ka: float,
    ibf_ka: float,
    gap_mm: float,
    arc_duration_ms: float,
    correction_factor: float,
    config: ElectrodeConfig
) -> float:
    """
    Calculate arc flash boundary for LV systems (Voc <= 600V).
    
    IEEE 1584-2018 Equation (10):
        Uses Table 3 coefficients with:
        - k3 term uses Iarc_600
        - k13 term uses final Iarc (from Equation 25)
    
    Args:
        iarc_600_ka: Intermediate arcing current at 600V (kA)
        iarc_final_ka: Final arcing current from Equation 25 (kA)
        ibf_ka: Bolted fault current (kA)
        gap_mm: Gap between electrodes (mm)
        arc_duration_ms: Arc duration (ms)
        correction_factor: Enclosure size CF
        config: Electrode configuration
    
    Returns:
        Arc flash boundary (mm)
    """
    return equations_7_8_9_intermediate_afb(
        iarc_ref_ka=iarc_600_ka,
        iarc_final_ka=iarc_final_ka,
        ibf_ka=ibf_ka,
        gap_mm=gap_mm,
        arc_duration_ms=arc_duration_ms,
        correction_factor=correction_factor,
        config=config,
        voltage_ref=600
    )


def equations_22_23_24_mv_interpolation(
    afb_600: float,
    afb_2700: float,
    afb_14300: float,
    voc_kv: float
) -> float:
    """
    Interpolate arc flash boundary for MV systems (600V < Voc <= 15kV).
    
    IEEE 1584-2018 Equations (22), (23), (24):
        AFB1 = (AFB2700 - AFB600)/2.1 × (Voc - 2.7) + AFB2700        (22)
        AFB2 = (AFB14300 - AFB2700)/11.6 × (Voc - 14.3) + AFB14300   (23)
        AFB3 = (AFB1×(2.7-Voc) + AFB2×(Voc-0.6)) / 2.1               (24)
    
    When 0.6 < Voc <= 2.7: Final AFB = AFB3
    When Voc > 2.7: Final AFB = AFB2
    
    Args:
        afb_600: Arc flash boundary at 600V (mm)
        afb_2700: Arc flash boundary at 2700V (mm)
        afb_14300: Arc flash boundary at 14300V (mm)
        voc_kv: Open circuit voltage (kV)
    
    Returns:
        Final interpolated arc flash boundary (mm)
    """
    # Equation (22)
    afb_1 = ((afb_2700 - afb_600) / 2.1) * (voc_kv - 2.7) + afb_2700
    
    # Equation (23)
    afb_2 = ((afb_14300 - afb_2700) / 11.6) * (voc_kv - 14.3) + afb_14300
    
    # Equation (24)
    afb_3 = (afb_1 * (2.7 - voc_kv) + afb_2 * (voc_kv - 0.6)) / 2.1
    
    if voc_kv <= 2.7:
        return afb_3
    else:
        return afb_2


def calculate_arc_flash_boundary(
    iarc_600_ka: float,
    iarc_2700_ka: float,
    iarc_14300_ka: float,
    iarc_final_ka: float,
    ibf_ka: float,
    voc_kv: float,
    gap_mm: float,
    arc_duration_ms: float,
    correction_factor: float,
    config: ElectrodeConfig
) -> Tuple[float, float]:
    """
    Calculate arc flash boundary.
    
    This is the main entry point for AFB calculations.
    
    Args:
        iarc_600_ka: Intermediate arcing current at 600V (kA)
        iarc_2700_ka: Intermediate arcing current at 2700V (kA)
        iarc_14300_ka: Intermediate arcing current at 14300V (kA)
        iarc_final_ka: Final arcing current (kA)
        ibf_ka: Bolted fault current (kA)
        voc_kv: Open circuit voltage (kV)
        gap_mm: Gap between electrodes (mm)
        arc_duration_ms: Arc duration (ms)
        correction_factor: Enclosure size CF
        config: Electrode configuration
    
    Returns:
        Tuple of (afb_mm, afb_inches)
    """
    if voc_kv <= 0.6:
        # LV: Use Equation (10)
        afb_mm = equation_10_lv_afb(
            iarc_600_ka, iarc_final_ka, ibf_ka, gap_mm,
            arc_duration_ms, correction_factor, config
        )
    else:
        # MV: Calculate at all three voltages and interpolate
        afb_600 = equations_7_8_9_intermediate_afb(
            iarc_600_ka, iarc_600_ka, ibf_ka, gap_mm,
            arc_duration_ms, correction_factor, config, 600
        )
        afb_2700 = equations_7_8_9_intermediate_afb(
            iarc_2700_ka, iarc_2700_ka, ibf_ka, gap_mm,
            arc_duration_ms, correction_factor, config, 2700
        )
        afb_14300 = equations_7_8_9_intermediate_afb(
            iarc_14300_ka, iarc_14300_ka, ibf_ka, gap_mm,
            arc_duration_ms, correction_factor, config, 14300
        )
        afb_mm = equations_22_23_24_mv_interpolation(afb_600, afb_2700, afb_14300, voc_kv)
    
    afb_inches = afb_mm / INCHES_TO_MM
    return afb_mm, afb_inches