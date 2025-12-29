"""
IEEE 1584-2018 Default Parameters
=================================

This module contains default parameter values from IEEE 1584-2018.

These defaults are used when the user does not specify explicit values
for gap distance, working distance, or enclosure dimensions.

References:
    - IEEE 1584-2018, Table 3: Working distances
    - IEEE 1584-2018, Table 8: Typical gaps by equipment class
    - IEEE 1584-2018, Table 9: Typical enclosure sizes

Traceability:
    - REQ-ARC-DATA-1: Default gap distances from Table 8
    - REQ-ARC-DATA-2: Default working distances from Table 3
    - REQ-ARC-DATA-3: Default enclosure sizes from Table 9
"""

from arc_flash_studio.components.enums import EquipmentType, VoltageLevel


# =============================================================================
# Default Gap Distances (mm)
# =============================================================================
# Source: IEEE 1584-2018 Table 8
# Key: (EquipmentType, VoltageLevel) -> gap_mm

DEFAULT_GAPS_MM: dict[tuple[EquipmentType, VoltageLevel], float] = {
    # Switchgear
    (EquipmentType.SWITCHGEAR, VoltageLevel.LV): 32.0,    # 15 kV class LV
    (EquipmentType.SWITCHGEAR, VoltageLevel.MV): 104.0,   # 5 kV class typical
    
    # Motor Control Center
    (EquipmentType.MCC, VoltageLevel.LV): 25.0,
    
    # Panelboard
    (EquipmentType.PANELBOARD, VoltageLevel.LV): 25.0,
    
    # Cable Junction Box
    (EquipmentType.CABLE_JUNCTION, VoltageLevel.LV): 13.0,
    
    # Open Air
    (EquipmentType.OPEN_AIR, VoltageLevel.LV): 32.0,
    (EquipmentType.OPEN_AIR, VoltageLevel.MV): 104.0,
    
    # Other/Generic (conservative defaults)
    (EquipmentType.OTHER, VoltageLevel.LV): 32.0,
    (EquipmentType.OTHER, VoltageLevel.MV): 104.0,
}

# Fallback if specific combination not found
DEFAULT_GAP_MM_FALLBACK: float = 32.0


# =============================================================================
# Default Working Distances (mm)
# =============================================================================
# Source: IEEE 1584-2018 Table 3
# Key: EquipmentType -> working_distance_mm

DEFAULT_WORKING_DISTANCE_MM: dict[EquipmentType, float] = {
    EquipmentType.SWITCHGEAR: 610.0,       # 24 inches (typical for MV)
    EquipmentType.MCC: 455.0,              # 18 inches
    EquipmentType.PANELBOARD: 455.0,       # 18 inches
    EquipmentType.CABLE_JUNCTION: 455.0,   # 18 inches
    EquipmentType.OPEN_AIR: 455.0,         # 18 inches (default)
    EquipmentType.OTHER: 455.0,            # 18 inches (conservative)
}

# Fallback working distance
DEFAULT_WORKING_DISTANCE_MM_FALLBACK: float = 455.0


# =============================================================================
# Default Enclosure Sizes (mm)
# =============================================================================
# Source: IEEE 1584-2018 Table 9
# Key: EquipmentType -> (height_mm, width_mm, depth_mm)

DEFAULT_ENCLOSURE_SIZES_MM: dict[EquipmentType, tuple[float, float, float]] = {
    # Switchgear: 36" cube typical for MV
    EquipmentType.SWITCHGEAR: (914.0, 914.0, 914.0),
    
    # MCC: 26" cube typical
    EquipmentType.MCC: (660.0, 660.0, 660.0),
    
    # Panelboard: 20"x20"x10" typical
    EquipmentType.PANELBOARD: (508.0, 508.0, 254.0),
    
    # Cable Junction: 12"x12"x8" typical
    EquipmentType.CABLE_JUNCTION: (305.0, 305.0, 203.0),
    
    # Other/Generic: 20" cube default
    EquipmentType.OTHER: (508.0, 508.0, 508.0),
}

# Fallback enclosure size
DEFAULT_ENCLOSURE_SIZE_MM_FALLBACK: tuple[float, float, float] = (508.0, 508.0, 508.0)


# =============================================================================
# Helper Functions
# =============================================================================

def get_default_gap_mm(equipment_type: EquipmentType, voltage_level: VoltageLevel) -> float:
    """
    Get default gap distance for equipment type and voltage level.
    
    Args:
        equipment_type: Type of equipment
        voltage_level: Voltage classification (LV, MV, HV)
    
    Returns:
        Gap distance in millimeters
    
    Reference:
        IEEE 1584-2018 Table 8
    """
    key = (equipment_type, voltage_level)
    return DEFAULT_GAPS_MM.get(key, DEFAULT_GAP_MM_FALLBACK)


def get_default_working_distance_mm(equipment_type: EquipmentType) -> float:
    """
    Get default working distance for equipment type.
    
    Args:
        equipment_type: Type of equipment
    
    Returns:
        Working distance in millimeters
    
    Reference:
        IEEE 1584-2018 Table 3
    """
    return DEFAULT_WORKING_DISTANCE_MM.get(
        equipment_type, 
        DEFAULT_WORKING_DISTANCE_MM_FALLBACK
    )


def get_default_enclosure_size_mm(
    equipment_type: EquipmentType
) -> tuple[float, float, float]:
    """
    Get default enclosure dimensions for equipment type.
    
    Args:
        equipment_type: Type of equipment
    
    Returns:
        Tuple of (height_mm, width_mm, depth_mm)
    
    Reference:
        IEEE 1584-2018 Table 9
    """
    return DEFAULT_ENCLOSURE_SIZES_MM.get(
        equipment_type,
        DEFAULT_ENCLOSURE_SIZE_MM_FALLBACK
    )