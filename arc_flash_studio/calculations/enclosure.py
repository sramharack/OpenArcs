"""
IEEE 1584-2018 Enclosure Size Correction Factor
================================================

Implements:
- Section 4.8.2: Shallow vs Typical enclosure determination
- Section 4.8.3: Equivalent height/width calculation (Table 6)
- Equation (13): Equivalent Enclosure Size (EES)
- Equations (14)-(15): Correction factor calculation

Note: EES is calculated in INCHES per IEEE 1584-2018.

Reference: IEEE 1584-2018, Section 4.8
"""

import math
from typing import Tuple

from .constants import ElectrodeConfig, MM_TO_INCHES
from .tables import get_enclosure_coefficients


def is_shallow_enclosure(
    height_mm: float,
    width_mm: float,
    depth_mm: float,
    voc_kv: float
) -> bool:
    """
    Determine if enclosure is shallow per IEEE 1584-2018 Section 4.8.2.
    
    An enclosure is SHALLOW when ALL conditions are met:
        a) System voltage < 600V (0.6 kV)
        b) Both height AND width < 508mm (20 inches)
        c) Depth <= 203.2mm (8 inches)
    
    Otherwise, the enclosure is TYPICAL.
    
    Args:
        height_mm: Internal enclosure height (mm)
        width_mm: Internal enclosure width (mm)
        depth_mm: Internal enclosure depth (mm)
        voc_kv: Open circuit voltage (kV)
    
    Returns:
        True if shallow enclosure, False if typical
    """
    # Condition a: Voc < 600V
    if voc_kv >= 0.6:
        return False
    
    # Condition b: Both height AND width < 508mm
    if height_mm >= 508.0 or width_mm >= 508.0:
        return False
    
    # Condition c: Depth <= 203.2mm
    if depth_mm > 203.2:
        return False
    
    return True


def _get_table_6_constants(config: ElectrodeConfig) -> Tuple[float, float]:
    """
    Get constants A and B from Table 6 for equivalent dimension calculation.
    
    Args:
        config: Electrode configuration
    
    Returns:
        Tuple of (A, B) constants
    """
    if config == ElectrodeConfig.VCB:
        return 4.0, 20.0
    elif config == ElectrodeConfig.VCBB:
        return 10.0, 24.0
    elif config == ElectrodeConfig.HCB:
        return 10.0, 22.0
    else:  # VOA, HOA - not applicable but return defaults
        return 4.0, 20.0


def _calculate_equivalent_dimension(
    dimension_mm: float,
    voc_kv: float,
    config: ElectrodeConfig,
    is_shallow: bool,
    is_width: bool
) -> float:
    """
    Calculate equivalent dimension per Table 6.
    
    IEEE 1584-2018 Section 4.8.3, Table 6:
    - Dimensions capped at 1244.6mm (49 inches)
    - For < 508mm: Use 20" for typical, actual for shallow
    - For 508-660.4mm: Use actual dimension
    - For > 660.4mm: Apply Equations (11) or (12)
    
    Equations (11) and (12):
        Width1 = 660.4 + (Width - 660.4) × ((Voc + A)/B)^(1/25.4)
        Height1 = 660.4 + (Height - 660.4) × ((Voc + A)/B)^(1/25.4)
    
    Note: For VCB height > 660.4mm, use actual dimension.
    
    Args:
        dimension_mm: Actual dimension (mm)
        voc_kv: Open circuit voltage (kV)
        config: Electrode configuration
        is_shallow: Whether enclosure is shallow
        is_width: True for width, False for height
    
    Returns:
        Equivalent dimension in INCHES
    """
    # Cap at maximum of 1244.6mm (49 inches)
    dimension_mm = min(dimension_mm, 1244.6)
    
    A, B = _get_table_6_constants(config)
    
    # Range 1: < 508mm (20 inches)
    if dimension_mm < 508.0:
        if is_shallow:
            return dimension_mm * MM_TO_INCHES
        else:
            return 20.0  # Use 20 inches for typical enclosures
    
    # Range 2: 508mm to 660.4mm (20-26 inches)
    elif dimension_mm <= 660.4:
        return dimension_mm * MM_TO_INCHES
    
    # Range 3: > 660.4mm (> 26 inches)
    else:
        # For VCB height: use actual dimension
        if not is_width and config == ElectrodeConfig.VCB:
            return dimension_mm * MM_TO_INCHES
        else:
            # Apply Equation (11) or (12)
            # Dimension1 = 660.4 + (Dimension - 660.4) × ((Voc + A)/B)^(1/25.4)
            exponent = 1.0 / 25.4
            factor = ((voc_kv + A) / B) ** exponent
            result_mm = 660.4 + (dimension_mm - 660.4) * factor
            return result_mm * MM_TO_INCHES


def equation_13_equivalent_enclosure_size(
    height_mm: float,
    width_mm: float,
    voc_kv: float,
    config: ElectrodeConfig,
    is_shallow: bool
) -> float:
    """
    Calculate Equivalent Enclosure Size (EES).
    
    IEEE 1584-2018 Equation (13):
        EES = (Height1 + Width1) / 2
    
    Where Height1 and Width1 are the equivalent dimensions in INCHES.
    
    Args:
        height_mm: Internal enclosure height (mm)
        width_mm: Internal enclosure width (mm)
        voc_kv: Open circuit voltage (kV)
        config: Electrode configuration
        is_shallow: Whether enclosure is shallow
    
    Returns:
        Equivalent enclosure size (EES) in INCHES
    """
    # Open-air configurations have no enclosure
    if config in (ElectrodeConfig.VOA, ElectrodeConfig.HOA):
        return 0.0
    
    height_in = _calculate_equivalent_dimension(
        height_mm, voc_kv, config, is_shallow, is_width=False
    )
    width_in = _calculate_equivalent_dimension(
        width_mm, voc_kv, config, is_shallow, is_width=True
    )
    
    ees = (height_in + width_in) / 2.0
    
    # Per Section 4.8.4: minimum EES is 20 for typical enclosures
    if not is_shallow and ees < 20.0:
        ees = 20.0
    
    return ees


def equation_14_typical_correction_factor(
    ees_inches: float,
    config: ElectrodeConfig
) -> float:
    """
    Calculate correction factor for typical enclosures.
    
    IEEE 1584-2018 Equation (14):
        CF = b1 × EES² + b2 × EES + b3
    
    Args:
        ees_inches: Equivalent enclosure size (inches)
        config: Electrode configuration
    
    Returns:
        Correction factor (dimensionless)
    """
    coef = get_enclosure_coefficients(config, is_shallow=False)
    cf = coef["b1"] * ees_inches**2 + coef["b2"] * ees_inches + coef["b3"]
    return cf


def equation_15_shallow_correction_factor(
    ees_inches: float,
    config: ElectrodeConfig
) -> float:
    """
    Calculate correction factor for shallow enclosures.
    
    IEEE 1584-2018 Equation (15):
        CF = 1 / (b1 × EES² + b2 × EES + b3)
    
    Note: Uses DIFFERENT coefficients from Table 7 (shallow row).
    
    Args:
        ees_inches: Equivalent enclosure size (inches)
        config: Electrode configuration
    
    Returns:
        Correction factor (dimensionless)
    """
    coef = get_enclosure_coefficients(config, is_shallow=True)
    denominator = coef["b1"] * ees_inches**2 + coef["b2"] * ees_inches + coef["b3"]
    
    if abs(denominator) < 1e-10:
        return 1.0  # Avoid division by zero
    
    cf = 1.0 / denominator
    return cf


def calculate_correction_factor(
    height_mm: float,
    width_mm: float,
    depth_mm: float,
    voc_kv: float,
    config: ElectrodeConfig
) -> Tuple[float, float, bool]:
    """
    Calculate enclosure size correction factor.
    
    This is the main entry point for enclosure correction calculations.
    
    Args:
        height_mm: Internal enclosure height (mm)
        width_mm: Internal enclosure width (mm)
        depth_mm: Internal enclosure depth (mm)
        voc_kv: Open circuit voltage (kV)
        config: Electrode configuration
    
    Returns:
        Tuple of (correction_factor, ees_inches, is_shallow)
    """
    # Open-air: CF = 1
    if config in (ElectrodeConfig.VOA, ElectrodeConfig.HOA):
        return 1.0, 0.0, False
    
    # Determine enclosure type
    shallow = is_shallow_enclosure(height_mm, width_mm, depth_mm, voc_kv)
    
    # Calculate EES
    ees = equation_13_equivalent_enclosure_size(
        height_mm, width_mm, voc_kv, config, shallow
    )
    
    # Calculate CF using appropriate equation
    if shallow:
        cf = equation_15_shallow_correction_factor(ees, config)
    else:
        cf = equation_14_typical_correction_factor(ees, config)
    
    return cf, ees, shallow