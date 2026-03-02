"""
IEEE 1584-2018 Coefficient Tables
=================================

Tables 1-7 from IEEE 1584-2018.

Table 1: Arcing current coefficients (Equation 1)
Table 2: Arcing current variation coefficients (Equation 2)
Table 3: Incident energy/AFB coefficients for 600V (Equations 3, 6, 7, 10)
Table 4: Incident energy/AFB coefficients for 2700V (Equations 4, 8)
Table 5: Incident energy/AFB coefficients for 14300V (Equations 5, 9)
Table 7: Enclosure size correction factor coefficients (Equations 14-15)

IMPORTANT: Validate these coefficients against the IEEE 1584-2018 standard.
The coefficient values here are transcribed and may contain errors.
"""

from typing import Dict
from .constants import ElectrodeConfig


# =============================================================================
# TABLE 1: Arcing Current Coefficients - Equation (1)
# =============================================================================
# Iarc = 10^(k1 + k2*lg(Ibf) + k3*lg(G)) × [k4*Ibf^6 + k5*Ibf^5 + k6*Ibf^4 + 
#                                            k7*Ibf^3 + k8*Ibf^2 + k9*Ibf + k10]
#
# Note: The polynomial part is a MULTIPLIER, not part of the exponent.

TABLE_1_ARCING_CURRENT: Dict[ElectrodeConfig, Dict[int, Dict[str, float]]] = {
    # TODO: Validate all coefficients against IEEE 1584-2018 Table 1
    ElectrodeConfig.VCB: {
        600: {
            "k1": -0.04287, "k2": 1.035, "k3": -0.083,
            "k4": 0, "k5": 0, "k6": -4.783e-9,
            "k7": 1.962e-6, "k8": -0.000229, "k9": 0.003141, "k10": 1.092
        },
        2700: {
            "k1": 0.0065, "k2": 1.001, "k3": -0.024,
            "k4": -1.557e-12, "k5": 4.556e-10, "k6": -4.186e-8,
            "k7": 8.346e-7, "k8": 5.482e-5, "k9": -0.003191, "k10": 0.9729
        },
        14300: {
            "k1": 0.005795, "k2": 1.015, "k3": -0.011,
            "k4": -1.557e-12, "k5": 4.556e-10, "k6": -4.186e-8,
            "k7": 8.346e-7, "k8": 5.482e-5, "k9": -0.003191, "k10": 0.9729
        },
    },
    ElectrodeConfig.VCBB: {
        600: {
            "k1": -0.017432, "k2": 0.98, "k3": -0.05,
            "k4": 0, "k5": 0, "k6": -5.567e-9,
            "k7": 2.524e-6, "k8": -0.00034, "k9": 0.01187, "k10": 1.013
        },
        2700: {
            "k1": 0.002823, "k2": 0.995, "k3": -0.01215,
            "k4": 0, "k5": -9.204e-11, "k6": 2.901e-8,
            "k7": -3.262e-6, "k8": 0.0001569, "k9": -0.004003, "k10": 0.9825
        },
        14300: {
            "k1": 0.014827, "k2": 1.01, "k3": -0.01,
            "k4": 0, "k5": -9.204e-11, "k6": 2.901e-8,
            "k7": -3.262e-6, "k8": 0.0001569, "k9": -0.004003, "k10": 0.9825
        },
    },
    ElectrodeConfig.HCB: {
        600: {
            "k1": 0.054922, "k2": 0.988, "k3": -0.11,
            "k4": 0, "k5": 0, "k6": -5.382e-9,
            "k7": 2.316e-6, "k8": -0.000302, "k9": 0.0091, "k10": 0.9725
        },
        2700: {
            "k1": 0.001011, "k2": 1.003, "k3": -0.0249,
            "k4": 0, "k5": 0, "k6": 4.859e-10,
            "k7": -1.814e-7, "k8": -9.128e-6, "k9": -0.0007, "k10": 0.9881
        },
        14300: {
            "k1": 0.008693, "k2": 0.999, "k3": -0.02,
            "k4": 0, "k5": -5.043e-11, "k6": 2.233e-8,
            "k7": -3.046e-6, "k8": 0.000116, "k9": -0.001145, "k10": 0.9839
        },
    },
    ElectrodeConfig.VOA: {
        600: {
            "k1": 0.043785, "k2": 1.04, "k3": -0.18,
            "k4": 0, "k5": 0, "k6": -4.783e-9,
            "k7": 1.962e-6, "k8": -0.000229, "k9": 0.003141, "k10": 1.092
        },
        2700: {
            "k1": -0.02395, "k2": 1.006, "k3": -0.0188,
            "k4": -1.557e-12, "k5": 4.556e-10, "k6": -4.186e-8,
            "k7": 8.346e-7, "k8": 5.482e-5, "k9": -0.003191, "k10": 0.9729
        },
        14300: {
            "k1": 0.005371, "k2": 1.0102, "k3": -0.029,
            "k4": -1.557e-12, "k5": 4.556e-10, "k6": -4.186e-8,
            "k7": 8.346e-7, "k8": 5.482e-5, "k9": -0.003191, "k10": 0.9729
        },
    },
    ElectrodeConfig.HOA: {
        600: {
            "k1": 0.111147, "k2": 1.008, "k3": -0.24,
            "k4": 0, "k5": 0, "k6": -3.895e-9,
            "k7": 1.641e-6, "k8": -0.000197, "k9": 0.002615, "k10": 1.1
        },
        2700: {
            "k1": 0.000435, "k2": 1.006, "k3": -0.038,
            "k4": 0, "k5": 0, "k6": 7.859e-10,
            "k7": -1.914e-7, "k8": -9.128e-6, "k9": -0.0007, "k10": 0.9981
        },
        14300: {
            "k1": 0.000904, "k2": 0.999, "k3": -0.02,
            "k4": 0, "k5": 0, "k6": 7.859e-10,
            "k7": -1.914e-7, "k8": -9.128e-6, "k9": -0.0007, "k10": 0.9981
        },
    },
}


# =============================================================================
# TABLE 2: Arcing Current Variation Coefficients - Equation (2)
# =============================================================================
# VarCf = k1*Voc^6 + k2*Voc^5 + k3*Voc^4 + k4*Voc^3 + k5*Voc^2 + k6*Voc + k7
# Iarc_min = Iarc × (1 - 0.5 × VarCf)

TABLE_2_VARIATION: Dict[ElectrodeConfig, Dict[str, float]] = {
    # TODO: Validate coefficients against IEEE 1584-2018 Table 2
    ElectrodeConfig.VCB: {
        "k1": 0, "k2": -0.0000014269, "k3": 0.000083137,
        "k4": -0.0019382, "k5": 0.022366, "k6": -0.12645, "k7": 0.30226
    },
    ElectrodeConfig.VCBB: {
        "k1": 1.138e-6, "k2": -6.0287e-5, "k3": 0.0012758,
        "k4": -0.013778, "k5": 0.080217, "k6": -0.24066, "k7": 0.33524
    },
    ElectrodeConfig.HCB: {
        "k1": 0, "k2": -3.097e-6, "k3": 0.00016405,
        "k4": -0.0033609, "k5": 0.033308, "k6": -0.16182, "k7": 0.34627
    },
    ElectrodeConfig.VOA: {
        "k1": 9.5606e-7, "k2": -5.1543e-5, "k3": 0.0011161,
        "k4": -0.01242, "k5": 0.075125, "k6": -0.23584, "k7": 0.33696
    },
    ElectrodeConfig.HOA: {
        "k1": 0, "k2": -3.1555e-6, "k3": 0.0001682,
        "k4": -0.0034607, "k5": 0.034124, "k6": -0.15999, "k7": 0.34629
    },
}


# =============================================================================
# TABLE 3: Incident Energy/AFB Coefficients for 600V
# =============================================================================
# Used by Equations (3), (6), (7), (10)

TABLE_3_ENERGY_600V: Dict[ElectrodeConfig, Dict[str, float]] = {
    # DONE (01/03/2026): Validate coefficients against IEEE 1584-2018 Table 3
    ElectrodeConfig.VCB: {
        "k1": 0.753364, "k2": 0.566, "k3": 1.752636,
        "k4": 0, "k5": 0, "k6": -4.783e-9,
        "k7": 1.962e-6, "k8": -0.000229, "k9": 0.003141, "k10": 1.092,
        "k11": 0, "k12": -1.598, "k13": 0.957
    },
    ElectrodeConfig.VCBB: {
        "k1": 3.068459, "k2": 0.26, "k3": -0.098107,
        "k4": 0, "k5": 0, "k6": -5.767e-9,
        "k7": 2.524e-6, "k8": -0.00034, "k9": 0.01187, "k10": 1.013,
        "k11": -0.06, "k12": -1.809, "k13": 1.19
    },
    ElectrodeConfig.HCB: {
        "k1": 4.073745, "k2": 0.344, "k3": -0.370259,
        "k4": 0, "k5": 0, "k6": -5.382e-9,
        "k7": 2.316e-6, "k8": -0.000302, "k9": 0.0091, "k10": 0.9725,
        "k11": 0, "k12": -2.03, "k13": 1.036
    },
    ElectrodeConfig.VOA: {
        "k1": 0.679294, "k2": 0.746, "k3": 1.222636,
        "k4": 0, "k5": 0, "k6": -4.783e-9,
        "k7": 1.962e-6, "k8": -0.000229, "k9": 0.003141, "k10": 1.092,
        "k11": 0, "k12": -1.598, "k13": 0.997
    },
    ElectrodeConfig.HOA: {
        "k1": 3.470417, "k2": 0.465, "k3": -0.261863,
        "k4": 0, "k5": 0, "k6": -3.895e-9,
        "k7": 1.641e-6, "k8": -0.000197, "k9": 0.002615, "k10": 1.1,
        "k11": 0, "k12": -1.99, "k13": 1.04
    },
}


# =============================================================================
# TABLE 4: Incident Energy/AFB Coefficients for 2700V
# =============================================================================
# Used by Equations (4), (8)

TABLE_4_ENERGY_2700V: Dict[ElectrodeConfig, Dict[str, float]] = {
    # DONE (01/03/2026): Validate coefficients against IEEE 1584-2018 Table 4
    ElectrodeConfig.VCB: {
        "k1": 2.40021, "k2": 0.165, "k3": 0.354202,
        "k4": -1.557e-12, "k5": 4.556e-10, "k6": -4.186e-8,
        "k7": 8.346e-7, "k8": 5.482e-5, "k9": -0.003191, "k10": 0.9729,
        "k11": 0, "k12": -1.569, "k13": 0.9778
    },
    ElectrodeConfig.VCBB: {
        "k1": 3.870592, "k2": 0.185, "k3": -0.736618,
        "k4": 0, "k5": -9.204e-11, "k6": 2.901e-8,
        "k7": -3.262e-6, "k8": 0.0001569, "k9": -0.004003, "k10": 0.9825,
        "k11": 0, "k12": -1.742, "k13": 1.09
    },
    ElectrodeConfig.HCB: {
        "k1": 3.486391, "k2": 0.177, "k3": -0.193101,
        "k4": 0, "k5": 0, "k6": 4.859e-10,
        "k7": -1.814e-7, "k8": -9.128e-6, "k9": -0.0007, "k10": 0.9881,
        "k11": 0.027, "k12": -1.723, "k13": 1.055
    },
    ElectrodeConfig.VOA: {
        "k1": 3.880724, "k2": 0.105, "k3": -1.906033,
        "k4": -1.557e-12, "k5": 4.556e-10, "k6": -4.186e-8,
        "k7": 8.346e-7, "k8": 5.482e-5, "k9": -0.003191, "k10": 0.9729,
        "k11": 0, "k12": -1.515, "k13": 1.115
    },
    ElectrodeConfig.HOA: {
        "k1": 3.616266, "k2": 0.149, "k3": -0.761561,
        "k4": 0, "k5": 0, "k6": 7.859e-10,
        "k7": -1.914e-7, "k8": -9.128e-6, "k9": -0.0007, "k10": 0.9981,
        "k11": 0, "k12": -1.639, "k13": 1.078
    },
}


# =============================================================================
# TABLE 5: Incident Energy/AFB Coefficients for 14300V
# =============================================================================
# Used by Equations (5), (9)

TABLE_5_ENERGY_14300V: Dict[ElectrodeConfig, Dict[str, float]] = {
    # DONE (01/03/2026): Validate coefficients against IEEE 1584-2018 Table 5
    ElectrodeConfig.VCB: {
        "k1": 3.825917, "k2": 0.11, "k3": -0.999749,
        "k4": -1.557e-12, "k5": 4.556e-10, "k6": -4.186e-8,
        "k7": 8.346e-7, "k8": 5.482e-5, "k9": -0.003191, "k10": 0.9729,
        "k11": 0, "k12": -1.568, "k13": 0.99
    },
    ElectrodeConfig.VCBB: {
        "k1": 3.644309, "k2": 0.215, "k3": -0.585522,
        "k4": 0, "k5": -9.204e-11, "k6": 2.901e-8,
        "k7": -3.262e-6, "k8": 0.0001569, "k9": -0.004003, "k10": 0.9825,
        "k11": 0, "k12": -1.677, "k13": 1.06
    },
    ElectrodeConfig.HCB: {
        "k1": 3.044516, "k2": 0.125, "k3": 0.245106,
        "k4": 0, "k5": -5.043e-11, "k6": 2.233e-8,
        "k7": -3.046e-6, "k8": 0.000116, "k9": -0.001145, "k10": 0.9839,
        "k11": 0, "k12": -1.655, "k13": 1.084
    },
    ElectrodeConfig.VOA: {
        "k1": 3.405454, "k2": 0.12, "k3": -0.93245,
        "k4": -1.557e-12, "k5": 4.556e-10, "k6": -4.186e-8,
        "k7": 8.346e-7, "k8": 5.482e-5, "k9": -0.003191, "k10": 0.9729,
        "k11": 0, "k12": -1.534, "k13": 0.979
    },
    ElectrodeConfig.HOA: {
        "k1": 2.04049, "k2": 0.177, "k3": 1.005092,
        "k4": 0, "k5": 0, "k6": 7.859e-10,
        "k7": -1.914e-7, "k8": -9.128e-6, "k9": -0.0007, "k10": 0.9981,
        "k11": -0.05, "k12": -1.633, "k13": 1.151
    },
}


# =============================================================================
# TABLE 7: Enclosure Size Correction Factor Coefficients
# =============================================================================
# Typical: CF = b1*EES² + b2*EES + b3          (Equation 14)
# Shallow: CF = 1 / (b1*EES² + b2*EES + b3)    (Equation 15)
# Note: EES is in INCHES

TABLE_7_ENCLOSURE_TYPICAL: Dict[ElectrodeConfig, Dict[str, float]] = {
    # TODO: Validate coefficients against IEEE 1584-2018 Table 7
    ElectrodeConfig.VCB: {"b1": -0.000302, "b2": 0.03441, "b3": 0.4325},
    ElectrodeConfig.VCBB: {"b1": -0.0002976, "b2": 0.032, "b3": 0.479},
    ElectrodeConfig.HCB: {"b1": -0.0001923, "b2": 0.01935, "b3": 0.6899},
    ElectrodeConfig.VOA: {"b1": 0, "b2": 0, "b3": 1.0},  # CF = 1 for open air
    ElectrodeConfig.HOA: {"b1": 0, "b2": 0, "b3": 1.0},  # CF = 1 for open air
}

TABLE_7_ENCLOSURE_SHALLOW: Dict[ElectrodeConfig, Dict[str, float]] = {
    # TODO: Validate coefficients against IEEE 1584-2018 Table 7
    ElectrodeConfig.VCB: {"b1": 0.002222, "b2": -0.025556, "b3": 0.6222},
    ElectrodeConfig.VCBB: {"b1": -0.002778, "b2": 0.1194, "b3": -0.2778},
    ElectrodeConfig.HCB: {"b1": -0.0005556, "b2": 0.03722, "b3": 0.4778},
    ElectrodeConfig.VOA: {"b1": 0, "b2": 0, "b3": 1.0},
    ElectrodeConfig.HOA: {"b1": 0, "b2": 0, "b3": 1.0},
}


# =============================================================================
# Accessor Functions
# =============================================================================

def get_arcing_current_coefficients(config: ElectrodeConfig, voltage_ref: int) -> Dict[str, float]:
    """Get Table 1 coefficients for arcing current calculation."""
    return TABLE_1_ARCING_CURRENT[config][voltage_ref]


def get_variation_coefficients(config: ElectrodeConfig) -> Dict[str, float]:
    """Get Table 2 coefficients for variation factor calculation."""
    return TABLE_2_VARIATION[config]


def get_energy_coefficients(config: ElectrodeConfig, voltage_ref: int) -> Dict[str, float]:
    """Get Table 3/4/5 coefficients for incident energy calculation."""
    if voltage_ref == 600:
        return TABLE_3_ENERGY_600V[config]
    elif voltage_ref == 2700:
        return TABLE_4_ENERGY_2700V[config]
    elif voltage_ref == 14300:
        return TABLE_5_ENERGY_14300V[config]
    else:
        raise ValueError(f"Invalid voltage reference: {voltage_ref}")


def get_enclosure_coefficients(config: ElectrodeConfig, is_shallow: bool) -> Dict[str, float]:
    """Get Table 7 coefficients for enclosure correction factor."""
    if is_shallow:
        return TABLE_7_ENCLOSURE_SHALLOW[config]
    else:
        return TABLE_7_ENCLOSURE_TYPICAL[config]