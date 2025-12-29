"""
Arc Flash Studio
================

IEEE 1584-2018 compliant arc flash calculation library.

This library provides:
    1. Component models with Pydantic validation
    2. PandaPower-backed short-circuit calculations (IEC 60909)
    3. IEEE 1584-2018 arc flash calculations (TODO)

Quick Start:
    >>> from arc_flash_studio import Network, Switchgear, UtilitySource, Transformer
    >>> 
    >>> net = Network(name="My Plant")
    >>> net.add_bus(Switchgear(id="SWGR", name="Main Switchgear", voltage_kv=0.48))
    >>> net.add_utility(UtilitySource(id="U1", name="Grid", bus_id="SWGR",
    ...     short_circuit_mva=500, x_r_ratio=15))
    >>> 
    >>> results = net.calculate_short_circuit()
    >>> print(f"Fault current: {results['SWGR'].ikss_ka:.2f} kA")

Components:
    Equipment Types (all become buses in PandaPower):
        - Bus: Generic electrical bus
        - Switchgear: LV or MV switchgear
        - Panelboard: Distribution panel
        - MCC: Motor control center
        - CableJunction: Junction box
        - OpenAir: Outdoor equipment
    
    Sources:
        - UtilitySource: Grid connection
    
    Branches:
        - Transformer: Two-winding transformer
        - Cable: Power cable or busway

Network:
    - Network: Builds and analyzes electrical networks
    - ShortCircuitResult: Results from short-circuit calculation
"""

# Components - import from components package
from arc_flash_studio.components import (
    # Enums
    VoltageLevel,
    ElectrodeConfig,
    EquipmentType,
    # Supporting classes
    EnclosureInfo,
    NetworkNode,
    # Equipment types (nodes/buses)
    Bus,
    Switchgear,
    Panelboard,
    MCC,
    CableJunction,
    OpenAir,
    # Sources
    UtilitySource,
    # Branches
    Transformer,
    Cable,
    create_cable,
    CABLE_DATA,
)

# Network
from arc_flash_studio.network import (
    Network,
    ShortCircuitResult,
)

__version__ = "0.2.0"

__all__ = [
    # Enums
    "VoltageLevel",
    "ElectrodeConfig",
    "EquipmentType",
    # Equipment types
    "NetworkNode",
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
    # Helpers
    "EnclosureInfo",
    "create_cable",
    "CABLE_DATA",
    # Network
    "Network",
    "ShortCircuitResult",
]