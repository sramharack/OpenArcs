"""
Arc Flash Studio Components Package
===================================

This package contains all component models for building electrical networks.

Component Categories:
    Enums: VoltageLevel, ElectrodeConfig, EquipmentType
    Enclosure: EnclosureInfo
    Base: NetworkNode (abstract base)
    
    Equipment Types (all become buses in PandaPower):
        - Bus: Generic electrical bus
        - Switchgear: LV/MV switchgear
        - Panelboard: Distribution panel
        - MCC: Motor control center
        - CableJunction: Junction box
        - OpenAir: Outdoor equipment
    
    Sources:
        - UtilitySource: Grid connection
    
    Branches:
        - Transformer: Two-winding transformer
        - Cable: Power cable or busway
    
    Helpers:
        - create_cable(): Create cable from NEC Table 9 lookup
        - CABLE_DATA: NEC Table 9 conductor data

Usage:
    >>> from arc_flash_studio.components import (
    ...     Switchgear, UtilitySource, Transformer, Cable
    ... )
    >>> swgr = Switchgear(id="SWGR", name="Main", voltage_kv=0.48)
"""

# Enums
from arc_flash_studio.components.enums import (
    VoltageLevel,
    ElectrodeConfig,
    EquipmentType,
)

# Supporting classes
from arc_flash_studio.components.enclosure import EnclosureInfo
from arc_flash_studio.components.base import NetworkNode

# Equipment types (network nodes)
from arc_flash_studio.components.bus import Bus
from arc_flash_studio.components.switchgear import Switchgear
from arc_flash_studio.components.panelboard import Panelboard
from arc_flash_studio.components.mcc import MCC
from arc_flash_studio.components.cable_junction import CableJunction
from arc_flash_studio.components.open_air import OpenAir

# Sources
from arc_flash_studio.components.utility_source import UtilitySource

# Branches
from arc_flash_studio.components.transformer import Transformer
from arc_flash_studio.components.cable import Cable, create_cable, CABLE_DATA

# Defaults (for advanced use)
from arc_flash_studio.components.defaults import (
    DEFAULT_GAPS_MM,
    DEFAULT_WORKING_DISTANCE_MM,
    DEFAULT_ENCLOSURE_SIZES_MM,
    get_default_gap_mm,
    get_default_working_distance_mm,
    get_default_enclosure_size_mm,
)

__all__ = [
    # Enums
    "VoltageLevel",
    "ElectrodeConfig",
    "EquipmentType",
    # Supporting classes
    "EnclosureInfo",
    "NetworkNode",
    # Equipment types
    "Bus",
    "Switchgear",
    "Panelboard",
    "MCC",
    "CableJunction",
    "OpenAir",
    # Sources
    "UtilitySource",
    # Branches
    "Transformer",
    "Cable",
    "create_cable",
    "CABLE_DATA",
    # Defaults
    "DEFAULT_GAPS_MM",
    "DEFAULT_WORKING_DISTANCE_MM",
    "DEFAULT_ENCLOSURE_SIZES_MM",
    "get_default_gap_mm",
    "get_default_working_distance_mm",
    "get_default_enclosure_size_mm",
]