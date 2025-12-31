"""
IEEE 1584-2018 Enumerations and Constants
=========================================

Electrode configurations, voltage classes, and physical constants.
"""

from enum import Enum


class ElectrodeConfig(str, Enum):
    """
    Electrode configuration per IEEE 1584-2018 Section 3.2.
    
    VCB:  Vertical conductors/electrodes inside a metal box/enclosure
    VCBB: Vertical conductors/electrodes terminated in insulating barrier inside a metal box
    HCB:  Horizontal conductors/electrodes inside a metal box/enclosure
    VOA:  Vertical conductors/electrodes in open air
    HOA:  Horizontal conductors/electrodes in open air
    """
    VCB = "VCB"
    VCBB = "VCBB"
    HCB = "HCB"
    VOA = "VOA"
    HOA = "HOA"


class VoltageClass(str, Enum):
    """Voltage classification for coefficient selection."""
    LV = "LV"      # Voc <= 600V
    MV = "MV"      # 600V < Voc <= 15000V


# Reference voltages for intermediate calculations (V)
V_REF_600 = 600
V_REF_2700 = 2700
V_REF_14300 = 14300

# Unit conversions
MM_TO_INCHES = 0.03937
INCHES_TO_MM = 25.4
JOULES_PER_CAL = 4.184

# Arc flash boundary threshold
AFB_THRESHOLD_J_CM2 = 5.0      # J/cm² (equivalent to 1.2 cal/cm²)
AFB_THRESHOLD_CAL_CM2 = 1.2    # cal/cm²

# Model validity ranges per IEEE 1584-2018 Section 4.2
VALID_VOLTAGE_MIN_KV = 0.208
VALID_VOLTAGE_MAX_KV = 15.0

VALID_CURRENT_LV_MIN_KA = 0.5      # 500 A
VALID_CURRENT_LV_MAX_KA = 106.0    # 106,000 A
VALID_CURRENT_MV_MIN_KA = 0.2      # 200 A  
VALID_CURRENT_MV_MAX_KA = 65.0     # 65,000 A

VALID_GAP_LV_MIN_MM = 6.35         # 0.25 inches
VALID_GAP_LV_MAX_MM = 76.2         # 3 inches
VALID_GAP_MV_MIN_MM = 19.05        # 0.75 inches
VALID_GAP_MV_MAX_MM = 254.0        # 10 inches

VALID_DISTANCE_MIN_MM = 305.0      # 12 inches