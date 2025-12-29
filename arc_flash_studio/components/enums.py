"""
Enumeration Types for Arc Flash Studio
======================================

This module defines all enumeration types used throughout the library.

References:
    - IEEE 1584-2018, Section 3.1: Definitions
    - IEEE 1584-2018, Section 4.2: Electrode configurations
    - IEEE 1584-2018, Table 8: Equipment classes

Traceability:
    - REQ-ARC-VAL-33: Electrode configuration validation
"""

from enum import Enum


class VoltageLevel(str, Enum):
    """
    Voltage level classification per IEEE 1584-2018.
    
    IEEE 1584-2018 applies to systems from 208V to 15kV.
    This classification helps determine default parameters.
    
    Attributes:
        LV: Low Voltage (≤ 1000 V)
        MV: Medium Voltage (> 1000 V to 35 kV)
        HV: High Voltage (> 35 kV) - outside IEEE 1584-2018 scope
    """
    LV = "LV"
    MV = "MV"
    HV = "HV"


class ElectrodeConfig(str, Enum):
    """
    Electrode configurations per IEEE 1584-2018 Section 4.2.
    
    The electrode configuration describes the physical arrangement
    of conductors and affects how arc energy is directed.
    
    Attributes:
        VCB:  Vertical Conductors in Box (most common)
        VCBB: Vertical Conductors in Box with insulating Barrier
        HCB:  Horizontal Conductors in Box
        VOA:  Vertical conductors in Open Air
        HOA:  Horizontal conductors in Open Air
    
    Reference:
        IEEE 1584-2018, Figures G.1 through G.5
    """
    VCB = "VCB"
    VCBB = "VCBB"
    HCB = "HCB"
    VOA = "VOA"
    HOA = "HOA"


class EquipmentType(str, Enum):
    """
    Equipment types for arc flash parameter defaults.
    
    Different equipment types have different typical gaps,
    working distances, and enclosure sizes per IEEE 1584-2018.
    
    Attributes:
        OPEN_AIR: Outdoor equipment, no enclosure
        SWITCHGEAR: Low or medium voltage switchgear
        MCC: Motor Control Center
        PANELBOARD: Distribution panelboard
        CABLE_JUNCTION: Cable junction or splice box
        OTHER: Generic equipment (uses conservative defaults)
    
    Reference:
        IEEE 1584-2018, Table 8: Typical equipment parameters
    """
    OPEN_AIR = "open_air"
    SWITCHGEAR = "switchgear"
    MCC = "mcc"
    PANELBOARD = "panelboard"
    CABLE_JUNCTION = "cable_junction"
    OTHER = "other"