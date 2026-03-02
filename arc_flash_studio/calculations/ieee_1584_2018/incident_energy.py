"""
IEEE 1584-2018 Incident Energy Calculations
============================================

Implements:
- Equations (3)-(5): Intermediate incident energy at 600V, 2700V, 14300V
- Equation (6): Incident energy for LV systems (Voc <= 600V)
- Equations (19)-(21): Interpolation for MV systems (600V < Voc <= 15kV)

IMPORTANT: The incident energy equation has the form:
    E = (12.552/50) × T × 10^(exponent)

Where exponent = k1 + k2*lg(G) + k3*lg(Iarc_ref) + f(Ibf) + k11*lg(Ibf) + 
                 k12*lg(D) + k13*lg(Iarc_final) + lg(1/CF)

And f(Ibf) is a polynomial: k4*Ibf^7 + k5*Ibf^6 + k6*Ibf^5 + k7*Ibf^4 + 
                            k8*Ibf^3 + k9*Ibf^2 + k10*Ibf

TODO: Verify the exact equation structure against IEEE 1584-2018.
      The polynomial powers and whether k10 multiplies Ibf needs validation.

Reference: IEEE 1584-2018, Sections 4.6, 4.9
"""

import math
from typing import Tuple

from .constants import ElectrodeConfig, JOULES_PER_CAL
from .tables import get_energy_coefficients


def _build_energy_exponent(
    iarc_ref_ka: float,
    iarc_final_ka: float,
    ibf_ka: float,
    gap_mm: float,
    distance_mm: float,
    correction_factor: float,
    config: ElectrodeConfig,
    voltage_ref: int
) -> float:
    """
    Build the exponent for the incident energy equation.
    
    exponent = k1 + k2*lg(G) + k3*lg(Iarc_ref) + f(Ibf) + 
               k11*lg(Ibf) + k12*lg(D) + k13*lg(Iarc_final) + lg(1/CF)
    
    Where f(Ibf) = k4*Ibf^7 + k5*Ibf^6 + k6*Ibf^5 + k7*Ibf^4 + 
                   k8*Ibf^3 + k9*Ibf^2 + k10*Ibf
    
    Args:
        iarc_ref_ka: Reference arcing current for k3 term (kA)
        iarc_final_ka: Final arcing current for k13 term (kA)
        ibf_ka: Bolted fault current (kA)
        gap_mm: Gap between electrodes (mm)
        distance_mm: Working distance (mm)
        correction_factor: Enclosure size CF
        config: Electrode configuration
        voltage_ref: Reference voltage (600, 2700, or 14300)
    
    Returns:
        Exponent value
    """
    k = get_energy_coefficients(config, voltage_ref)
    
    exponent = k["k1"]
    exponent += k["k2"] * math.log10(gap_mm)
    
    # Polynomial f(Ibf)
    # TODO: Verify polynomial structure - powers 7,6,5,4,3,2,1 vs 6,5,4,3,2,1,0
    f_ibf = (
        k["k3"] * math.log10(iarc_ref_ka) +
        k["k4"] * ibf_ka**7 +
        k["k5"] * ibf_ka**6 +
        k["k6"] * ibf_ka**5 +
        k["k7"] * ibf_ka**4 +
        k["k8"] * ibf_ka**3 +
        k["k9"] * ibf_ka**2 +
        k["k10"] * ibf_ka
    )
    exponent += f_ibf
    
    exponent += k["k11"] * math.log10(ibf_ka)
    exponent += k["k12"] * math.log10(distance_mm)
    exponent += k["k13"] * math.log10(iarc_final_ka)
    
    # lg(1/CF)
    if correction_factor > 0:
        exponent += math.log10(1.0 / correction_factor)
    
    return exponent


def equations_3_4_5_intermediate_energy(
    iarc_ref_ka: float,
    iarc_final_ka: float,
    ibf_ka: float,
    gap_mm: float,
    distance_mm: float,
    arc_duration_ms: float,
    correction_factor: float,
    config: ElectrodeConfig,
    voltage_ref: int
) -> float:
    """
    Calculate intermediate incident energy at reference voltage.
    
    IEEE 1584-2018 Equations (3), (4), (5):
        E = (12.552/50) × T × 10^(exponent)
    
    Args:
        iarc_ref_ka: Reference arcing current for k3 term (kA)
        iarc_final_ka: Final arcing current for k13 term (kA)
        ibf_ka: Bolted fault current (kA)
        gap_mm: Gap between electrodes (mm)
        distance_mm: Working distance (mm)
        arc_duration_ms: Arc duration (ms)
        correction_factor: Enclosure size CF
        config: Electrode configuration
        voltage_ref: Reference voltage (600, 2700, or 14300)
    
    Returns:
        Incident energy (J/cm²)
    """
    exponent = _build_energy_exponent(
        iarc_ref_ka, iarc_final_ka, ibf_ka, gap_mm, distance_mm,
        correction_factor, config, voltage_ref
    )
    
    energy = (12.552 / 50.0) * arc_duration_ms * (10 ** exponent)
    return energy


def equation_6_lv_energy(
    iarc_600_ka: float,
    iarc_final_ka: float,
    ibf_ka: float,
    gap_mm: float,
    distance_mm: float,
    arc_duration_ms: float,
    correction_factor: float,
    config: ElectrodeConfig
) -> float:
    """
    Calculate incident energy for LV systems (Voc <= 600V).
    
    IEEE 1584-2018 Equation (6):
        Uses Table 3 coefficients with:
        - k3 term uses Iarc_600
        - k13 term uses final Iarc (from Equation 25)
    
    Args:
        iarc_600_ka: Intermediate arcing current at 600V (kA)
        iarc_final_ka: Final arcing current from Equation 25 (kA)
        ibf_ka: Bolted fault current (kA)
        gap_mm: Gap between electrodes (mm)
        distance_mm: Working distance (mm)
        arc_duration_ms: Arc duration (ms)
        correction_factor: Enclosure size CF
        config: Electrode configuration
    
    Returns:
        Incident energy (J/cm²)
    """
    return equations_3_4_5_intermediate_energy(
        iarc_ref_ka=iarc_600_ka,
        iarc_final_ka=iarc_final_ka,
        ibf_ka=ibf_ka,
        gap_mm=gap_mm,
        distance_mm=distance_mm,
        arc_duration_ms=arc_duration_ms,
        correction_factor=correction_factor,
        config=config,
        voltage_ref=600
    )


def equations_19_20_21_mv_interpolation(
    e_600: float,
    e_2700: float,
    e_14300: float,
    voc_kv: float
) -> float:
    """
    Interpolate incident energy for MV systems (600V < Voc <= 15kV).
    
    IEEE 1584-2018 Equations (19), (20), (21):
        E1 = (E2700 - E600)/2.1 × (Voc - 2.7) + E2700          (19)
        E2 = (E14300 - E2700)/11.6 × (Voc - 14.3) + E14300     (20)
        E3 = (E1×(2.7-Voc) + E2×(Voc-0.6)) / 2.1               (21)
    
    When 0.6 < Voc <= 2.7: Final E = E3
    When Voc > 2.7: Final E = E2
    
    Args:
        e_600: Incident energy at 600V (J/cm²)
        e_2700: Incident energy at 2700V (J/cm²)
        e_14300: Incident energy at 14300V (J/cm²)
        voc_kv: Open circuit voltage (kV)
    
    Returns:
        Final interpolated incident energy (J/cm²)
    """
    # Equation (19)
    e_1 = ((e_2700 - e_600) / 2.1) * (voc_kv - 2.7) + e_2700
    
    # Equation (20)
    e_2 = ((e_14300 - e_2700) / 11.6) * (voc_kv - 14.3) + e_14300
    
    # Equation (21)
    e_3 = (e_1 * (2.7 - voc_kv) + e_2 * (voc_kv - 0.6)) / 2.1
    
    if voc_kv <= 2.7:
        return e_3
    else:
        return e_2


def calculate_incident_energy(
    iarc_600_ka: float,
    iarc_2700_ka: float,
    iarc_14300_ka: float,
    iarc_final_ka: float,
    ibf_ka: float,
    voc_kv: float,
    gap_mm: float,
    distance_mm: float,
    arc_duration_ms: float,
    correction_factor: float,
    config: ElectrodeConfig
) -> Tuple[float, float]:
    """
    Calculate incident energy.
    
    This is the main entry point for incident energy calculations.
    
    Args:
        iarc_600_ka: Intermediate arcing current at 600V (kA)
        iarc_2700_ka: Intermediate arcing current at 2700V (kA)
        iarc_14300_ka: Intermediate arcing current at 14300V (kA)
        iarc_final_ka: Final arcing current (kA)
        ibf_ka: Bolted fault current (kA)
        voc_kv: Open circuit voltage (kV)
        gap_mm: Gap between electrodes (mm)
        distance_mm: Working distance (mm)
        arc_duration_ms: Arc duration (ms)
        correction_factor: Enclosure size CF
        config: Electrode configuration
    
    Returns:
        Tuple of (energy_j_cm2, energy_cal_cm2)
    """
    if voc_kv <= 0.6:
        # LV: Use Equation (6)
        energy_j = equation_6_lv_energy(
            iarc_600_ka, iarc_final_ka, ibf_ka, gap_mm, distance_mm,
            arc_duration_ms, correction_factor, config
        )
    else:
        # MV: Calculate at all three voltages and interpolate
        e_600 = equations_3_4_5_intermediate_energy(
            iarc_600_ka, iarc_600_ka, ibf_ka, gap_mm, distance_mm,
            arc_duration_ms, correction_factor, config, 600
        )
        e_2700 = equations_3_4_5_intermediate_energy(
            iarc_2700_ka, iarc_2700_ka, ibf_ka, gap_mm, distance_mm,
            arc_duration_ms, correction_factor, config, 2700
        )
        e_14300 = equations_3_4_5_intermediate_energy(
            iarc_14300_ka, iarc_14300_ka, ibf_ka, gap_mm, distance_mm,
            arc_duration_ms, correction_factor, config, 14300
        )
        energy_j = equations_19_20_21_mv_interpolation(e_600, e_2700, e_14300, voc_kv)
    
    energy_cal = energy_j / JOULES_PER_CAL
    return energy_j, energy_cal