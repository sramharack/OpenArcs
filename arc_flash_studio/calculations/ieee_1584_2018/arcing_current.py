"""
IEEE 1584-2018 Arcing Current Calculations
==========================================

Implements:
- Equation (1): Intermediate arcing current at 600V, 2700V, 14300V
- Equation (2): Arcing current variation factor
- Equations (16)-(18): Interpolation for MV systems (600V < Voc <= 15kV)
- Equation (25): Final arcing current for LV systems (Voc <= 600V)

Reference: IEEE 1584-2018, Sections 4.4, 4.5, 4.9, 4.10
"""

import math
from dataclasses import dataclass
from typing import Tuple

from .constants import ElectrodeConfig
from .tables import get_arcing_current_coefficients, get_variation_coefficients


@dataclass
class ArcingCurrentResult:
    """Results from arcing current calculations."""
    iarc_600: float       # Intermediate arcing current at 600V (kA)
    iarc_2700: float      # Intermediate arcing current at 2700V (kA)
    iarc_14300: float     # Intermediate arcing current at 14300V (kA)
    iarc: float           # Final arcing current (kA)
    iarc_min: float       # Reduced arcing current (kA)
    variation_factor: float  # VarCf from Equation (2)


def equation_1_intermediate_arcing_current(
    ibf_ka: float,
    gap_mm: float,
    config: ElectrodeConfig,
    voltage_ref: int
) -> float:
    """
    Calculate intermediate arcing current at reference voltage.
    
    IEEE 1584-2018 Equation (1):
        Iarc = 10^(k1 + k2*lg(Ibf) + k3*lg(G)) × 
               [k4*Ibf^6 + k5*Ibf^5 + k6*Ibf^4 + k7*Ibf^3 + k8*Ibf^2 + k9*Ibf + k10]
    
    Args:
        ibf_ka: Bolted fault current (kA)
        gap_mm: Gap between electrodes (mm)
        config: Electrode configuration
        voltage_ref: Reference voltage (600, 2700, or 14300)
    
    Returns:
        Intermediate arcing current (kA)
    """
    k = get_arcing_current_coefficients(config, voltage_ref)
    
    # Logarithmic part: 10^(k1 + k2*lg(Ibf) + k3*lg(G))
    log_exponent = k["k1"] + k["k2"] * math.log10(ibf_ka) + k["k3"] * math.log10(gap_mm)
    log_part = 10 ** log_exponent
    
    # Polynomial part: k4*Ibf^6 + k5*Ibf^5 + ... + k10
    # NOTE: Powers are 6, 5, 4, 3, 2, 1, 0 (k10 is constant term)
    poly_part = (
        k["k4"] * ibf_ka**6 +
        k["k5"] * ibf_ka**5 +
        k["k6"] * ibf_ka**4 +
        k["k7"] * ibf_ka**3 +
        k["k8"] * ibf_ka**2 +
        k["k9"] * ibf_ka +
        k["k10"]
    )
    
    iarc = log_part * poly_part
    return iarc


def equation_2_variation_factor(voc_kv: float, config: ElectrodeConfig) -> float:
    """
    Calculate arcing current variation factor.
    
    IEEE 1584-2018 Equation (2):
        VarCf = k1*Voc^6 + k2*Voc^5 + k3*Voc^4 + k4*Voc^3 + k5*Voc^2 + k6*Voc + k7
    
    Args:
        voc_kv: Open circuit voltage (kV)
        config: Electrode configuration
    
    Returns:
        Variation correction factor (dimensionless)
    """
    k = get_variation_coefficients(config)
    
    varcf = (
        k["k1"] * voc_kv**6 +
        k["k2"] * voc_kv**5 +
        k["k3"] * voc_kv**4 +
        k["k4"] * voc_kv**3 +
        k["k5"] * voc_kv**2 +
        k["k6"] * voc_kv +
        k["k7"]
    )
    return varcf


def equation_2_reduced_current(iarc_ka: float, varcf: float) -> float:
    """
    Calculate reduced arcing current.
    
    IEEE 1584-2018 Equation (2):
        Iarc_min = Iarc × (1 - 0.5 × VarCf)
    
    Args:
        iarc_ka: Arcing current (kA)
        varcf: Variation correction factor
    
    Returns:
        Reduced arcing current (kA)
    """
    return iarc_ka * (1 - 0.5 * varcf)


def equation_25_lv_arcing_current(
    iarc_600: float,
    ibf_ka: float,
    voc_kv: float
) -> float:
    """
    Calculate final arcing current for LV systems (Voc <= 600V).
    
    IEEE 1584-2018 Equation (25):
        Iarc = Iarc_600 / sqrt(1 + ((Voc/0.6)^2 - 1) × (Iarc_600/Ibf)^2)
    
    This equation adjusts the 600V reference arcing current for the actual voltage.
    
    Args:
        iarc_600: Intermediate arcing current at 600V (kA)
        ibf_ka: Bolted fault current (kA)
        voc_kv: Open circuit voltage (kV)
    
    Returns:
        Final arcing current (kA)
    """
    # Voltage ratio squared: (Voc/0.6)^2
    voltage_ratio_sq = (voc_kv / 0.6) ** 2
    
    # Current ratio squared: (Iarc_600/Ibf)^2
    current_ratio_sq = (iarc_600 / ibf_ka) ** 2
    
    # Denominator: sqrt(1 + ((Voc/0.6)^2 - 1) × (Iarc_600/Ibf)^2)
    denominator = math.sqrt(1 + (voltage_ratio_sq - 1) * current_ratio_sq)
    
    iarc = iarc_600 / denominator
    return iarc


def equations_16_17_18_mv_interpolation(
    iarc_600: float,
    iarc_2700: float,
    iarc_14300: float,
    voc_kv: float
) -> float:
    """
    Interpolate final arcing current for MV systems (600V < Voc <= 15kV).
    
    IEEE 1584-2018 Equations (16), (17), (18):
        Iarc_1 = (Iarc_2700 - Iarc_600)/2.1 × (Voc - 2.7) + Iarc_2700     (16)
        Iarc_2 = (Iarc_14300 - Iarc_2700)/11.6 × (Voc - 14.3) + Iarc_14300 (17)
        Iarc_3 = (Iarc_1×(2.7-Voc) + Iarc_2×(Voc-0.6)) / 2.1              (18)
    
    When 0.6 < Voc <= 2.7: Final Iarc = Iarc_3
    When Voc > 2.7: Final Iarc = Iarc_2
    
    Args:
        iarc_600: Intermediate arcing current at 600V (kA)
        iarc_2700: Intermediate arcing current at 2700V (kA)
        iarc_14300: Intermediate arcing current at 14300V (kA)
        voc_kv: Open circuit voltage (kV)
    
    Returns:
        Final interpolated arcing current (kA)
    """
    # Equation (16): interpolation between 600V and 2700V
    iarc_1 = ((iarc_2700 - iarc_600) / 2.1) * (voc_kv - 2.7) + iarc_2700
    
    # Equation (17): interpolation between 2700V and 14300V
    iarc_2 = ((iarc_14300 - iarc_2700) / 11.6) * (voc_kv - 14.3) + iarc_14300
    
    # Equation (18): weighted interpolation for 600V < Voc <= 2700V
    iarc_3 = (iarc_1 * (2.7 - voc_kv) + iarc_2 * (voc_kv - 0.6)) / 2.1
    
    # Select final value based on voltage
    if voc_kv <= 2.7:
        return iarc_3
    else:
        return iarc_2


def calculate_arcing_current(
    ibf_ka: float,
    voc_kv: float,
    gap_mm: float,
    config: ElectrodeConfig
) -> ArcingCurrentResult:
    """
    Calculate all arcing current values.
    
    This is the main entry point for arcing current calculations.
    
    Args:
        ibf_ka: Bolted fault current (kA)
        voc_kv: Open circuit voltage (kV)
        gap_mm: Gap between electrodes (mm)
        config: Electrode configuration
    
    Returns:
        ArcingCurrentResult with all intermediate and final values
    """
    # Step 1: Calculate intermediate arcing currents at reference voltages
    iarc_600 = equation_1_intermediate_arcing_current(ibf_ka, gap_mm, config, 600)
    iarc_2700 = equation_1_intermediate_arcing_current(ibf_ka, gap_mm, config, 2700)
    iarc_14300 = equation_1_intermediate_arcing_current(ibf_ka, gap_mm, config, 14300)
    
    # Step 2: Calculate final arcing current based on voltage class
    if voc_kv <= 0.6:
        # LV: Use Equation (25)
        iarc = equation_25_lv_arcing_current(iarc_600, ibf_ka, voc_kv)
    else:
        # MV: Use Equations (16)-(18) interpolation
        iarc = equations_16_17_18_mv_interpolation(
            iarc_600, iarc_2700, iarc_14300, voc_kv
        )
    
    # Step 3: Calculate variation factor and reduced current
    varcf = equation_2_variation_factor(voc_kv, config)
    iarc_min = equation_2_reduced_current(iarc, varcf)
    
    return ArcingCurrentResult(
        iarc_600=iarc_600,
        iarc_2700=iarc_2700,
        iarc_14300=iarc_14300,
        iarc=iarc,
        iarc_min=iarc_min,
        variation_factor=varcf
    )