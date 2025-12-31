"""
IEEE 1584-2018 Arc Flash Calculation Engine
==========================================

A modular implementation of IEEE 1584-2018 arc flash calculations.

Modules:
    constants - Enumerations, reference voltages, validity ranges
    tables - Coefficient tables 1-7 from the standard
    arcing_current - Equations 1, 2, 16-18, 25
    enclosure - Equations 11-15, Table 6-7
    incident_energy - Equations 3-6, 19-21
    arc_flash_boundary - Equations 7-10, 22-24
    calculator - Main orchestration

Usage:
    from arc_flash_studio.ieee1584 import calculate_arc_flash, ElectrodeConfig
    
    result = calculate_arc_flash(
        ibf_ka=30.0,
        voc_kv=13.8,
        gap_mm=152.0,
        working_distance_mm=914.4,
        arc_duration_ms=100.0,
        height_mm=660.4,
        width_mm=660.4,
        depth_mm=660.4,
        config=ElectrodeConfig.VCB
    )

TODO:
    - Validate all coefficient tables against IEEE 1584-2018
    - Verify polynomial structure in incident energy equations
    - Add input validation per Section 4.2
    - Add PPE category determination per NFPA 70E

Reference:
    IEEE 1584-2018, "IEEE Guide for Performing Arc-Flash Hazard Calculations"
"""

# Constants and enums
from .constants import (
    ElectrodeConfig,
    VoltageClass,
    V_REF_600,
    V_REF_2700,
    V_REF_14300,
    MM_TO_INCHES,
    INCHES_TO_MM,
    JOULES_PER_CAL,
    AFB_THRESHOLD_J_CM2,
    AFB_THRESHOLD_CAL_CM2,
)

# Coefficient tables
from .tables import (
    get_arcing_current_coefficients,
    get_variation_coefficients,
    get_energy_coefficients,
    get_enclosure_coefficients,
)

# Arcing current calculations
from .arcing_current import (
    equation_1_intermediate_arcing_current,
    equation_2_variation_factor,
    equation_2_reduced_current,
    equation_25_lv_arcing_current,
    equations_16_17_18_mv_interpolation,
    calculate_arcing_current,
    ArcingCurrentResult,
)

# Enclosure correction
from .enclosure import (
    is_shallow_enclosure,
    equation_13_equivalent_enclosure_size,
    equation_14_typical_correction_factor,
    equation_15_shallow_correction_factor,
    calculate_correction_factor,
)

# Incident energy
from .incident_energy import (
    equations_3_4_5_intermediate_energy,
    equation_6_lv_energy,
    equations_19_20_21_mv_interpolation,
    calculate_incident_energy,
)

# Arc flash boundary
from .arc_flash_boundary import (
    equations_7_8_9_intermediate_afb,
    equation_10_lv_afb,
    equations_22_23_24_mv_interpolation,
    calculate_arc_flash_boundary,
)

# Main calculator
from .calculator import (
    calculate_arc_flash,
    ArcFlashResult,
)


__all__ = [
    # Constants
    "ElectrodeConfig",
    "VoltageClass",
    "V_REF_600",
    "V_REF_2700",
    "V_REF_14300",
    "MM_TO_INCHES",
    "INCHES_TO_MM",
    "JOULES_PER_CAL",
    "AFB_THRESHOLD_J_CM2",
    "AFB_THRESHOLD_CAL_CM2",
    # Tables
    "get_arcing_current_coefficients",
    "get_variation_coefficients",
    "get_energy_coefficients",
    "get_enclosure_coefficients",
    # Arcing current
    "equation_1_intermediate_arcing_current",
    "equation_2_variation_factor",
    "equation_2_reduced_current",
    "equation_25_lv_arcing_current",
    "equations_16_17_18_mv_interpolation",
    "calculate_arcing_current",
    "ArcingCurrentResult",
    # Enclosure
    "is_shallow_enclosure",
    "equation_13_equivalent_enclosure_size",
    "equation_14_typical_correction_factor",
    "equation_15_shallow_correction_factor",
    "calculate_correction_factor",
    # Incident energy
    "equations_3_4_5_intermediate_energy",
    "equation_6_lv_energy",
    "equations_19_20_21_mv_interpolation",
    "calculate_incident_energy",
    # Arc flash boundary
    "equations_7_8_9_intermediate_afb",
    "equation_10_lv_afb",
    "equations_22_23_24_mv_interpolation",
    "calculate_arc_flash_boundary",
    # Calculator
    "calculate_arc_flash",
    "ArcFlashResult",
]