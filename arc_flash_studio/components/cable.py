"""
Cable Component
===============

Power cable model for short-circuit studies.

Cables add impedance to the system, limiting fault current. The impedance
depends on conductor size, length, and installation method.

Reference:
    - IEEE 1584-2018, Section 6.2
    - IEC 60909-0, Section 6
    - NEC Chapter 9, Table 9

Traceability:
    - REQ-COMP-FUNC-4: Cable class definition
"""

from __future__ import annotations

import math
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    PositiveFloat,
    computed_field,
    ConfigDict,
)


class Cable(BaseModel):
    """
    Power cable connecting two buses.
    
    Models cable impedance for short-circuit calculations.
    Impedance is specified per unit length and multiplied by total length.
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        length_m: Cable length in meters
        r_per_km: Resistance per kilometer (Ω/km)
        x_per_km: Reactance per kilometer (Ω/km)
        voltage_nominal: Nominal voltage for per-unit calculations (kV)
    
    Example:
        >>> cable = Cable(
        ...     id="CBL-001",
        ...     name="Feeder to Panel",
        ...     length_m=30.0,
        ...     r_per_km=0.125,
        ...     x_per_km=0.093,
        ...     voltage_nominal=0.48
        ... )
        >>> print(f"Z = {cable.z_ohms:.6f} Ω")
    """
    
    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        str_strip_whitespace=True,
    )
    
    # Identification
    id: str = Field(..., description="Unique identifier", min_length=1)
    name: str = Field(..., description="Human-readable name")
    
    # Physical parameters
    length_m: PositiveFloat = Field(
        ...,
        description="Cable length in meters",
        examples=[10.0, 30.0, 100.0],
    )
    
    # Impedance per unit length
    r_per_km: PositiveFloat = Field(
        ...,
        description="Resistance per kilometer (Ω/km) at operating temperature",
        examples=[0.125, 0.0754, 0.0473],
    )
    
    x_per_km: PositiveFloat = Field(
        ...,
        description="Reactance per kilometer (Ω/km)",
        examples=[0.093, 0.075, 0.066],
    )
    
    # For per-unit calculations
    voltage_nominal: PositiveFloat = Field(
        ...,
        description="Nominal voltage in kV (for per-unit conversion)",
        examples=[0.48, 0.208, 4.16],
    )
    
    system_base_mva: PositiveFloat = Field(
        default=100.0,
        description="System base MVA for per-unit calculations",
    )
    
    # Optional
    ampacity: Optional[PositiveFloat] = Field(
        default=None,
        description="Continuous current rating in Amperes",
    )
    
    conductor_size: Optional[str] = Field(
        default=None,
        description="Conductor size (e.g., '500 kcmil', '4/0 AWG')",
    )
    
    # -------------------------------------------------------------------------
    # Computed Properties - Ohmic Values
    # -------------------------------------------------------------------------
    
    @computed_field
    @property
    def length_km(self) -> float:
        """Cable length in kilometers."""
        return self.length_m / 1000.0
    
    @computed_field
    @property
    def r_ohms(self) -> float:
        """Total resistance in ohms."""
        return self.r_per_km * self.length_km
    
    @computed_field
    @property
    def x_ohms(self) -> float:
        """Total reactance in ohms."""
        return self.x_per_km * self.length_km
    
    @computed_field
    @property
    def z_ohms(self) -> float:
        """Total impedance magnitude in ohms."""
        return math.sqrt(self.r_ohms ** 2 + self.x_ohms ** 2)
    
    @computed_field
    @property
    def x_r_ratio(self) -> float:
        """Reactance to resistance ratio."""
        if self.r_ohms == 0:
            return float('inf')
        return self.x_ohms / self.r_ohms
    
    # -------------------------------------------------------------------------
    # Computed Properties - Per-Unit Values
    # -------------------------------------------------------------------------
    
    @computed_field
    @property
    def z_base_ohms(self) -> float:
        """Base impedance in ohms at nominal voltage."""
        return (self.voltage_nominal ** 2) / self.system_base_mva
    
    @computed_field
    @property
    def r_pu(self) -> float:
        """Per-unit resistance on system base."""
        return self.r_ohms / self.z_base_ohms
    
    @computed_field
    @property
    def x_pu(self) -> float:
        """Per-unit reactance on system base."""
        return self.x_ohms / self.z_base_ohms
    
    @computed_field
    @property
    def z_pu(self) -> float:
        """Per-unit impedance magnitude on system base."""
        return self.z_ohms / self.z_base_ohms
    
    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------
    
    def get_impedance_complex_pu(self) -> complex:
        """Get complex impedance in per-unit on system base."""
        return complex(self.r_pu, self.x_pu)
    
    def get_impedance_complex_ohms(self) -> complex:
        """Get complex impedance in ohms."""
        return complex(self.r_ohms, self.x_ohms)
    
    def __str__(self) -> str:
        return (
            f"Cable('{self.id}': {self.name}, "
            f"{self.length_m}m, Z={self.z_ohms:.6f}Ω)"
        )


# =============================================================================
# Common Cable Data (NEC Table 9 approximations)
# =============================================================================
# These are approximate values for copper conductors in steel conduit at 75°C

COMMON_CABLE_DATA = {
    # AWG/kcmil: (R Ω/km, X Ω/km, Ampacity A)
    "14 AWG":    (10.17, 0.190, 15),
    "12 AWG":    (6.56,  0.177, 20),
    "10 AWG":    (3.94,  0.164, 30),
    "8 AWG":     (2.56,  0.171, 50),
    "6 AWG":     (1.61,  0.167, 65),
    "4 AWG":     (1.02,  0.157, 85),
    "2 AWG":     (0.62,  0.148, 115),
    "1/0 AWG":   (0.39,  0.144, 150),
    "2/0 AWG":   (0.33,  0.141, 175),
    "3/0 AWG":   (0.269, 0.138, 200),
    "4/0 AWG":   (0.220, 0.135, 230),
    "250 kcmil": (0.187, 0.135, 255),
    "300 kcmil": (0.161, 0.135, 285),
    "350 kcmil": (0.141, 0.131, 310),
    "400 kcmil": (0.125, 0.131, 335),
    "500 kcmil": (0.105, 0.128, 380),
    "600 kcmil": (0.092, 0.128, 420),
    "750 kcmil": (0.079, 0.125, 475),
}


def create_cable_from_size(
    id: str,
    name: str,
    conductor_size: str,
    length_m: float,
    voltage_nominal: float,
    system_base_mva: float = 100.0,
) -> Cable:
    """
    Create a cable using standard conductor size data.
    
    Args:
        id: Unique identifier
        name: Human-readable name
        conductor_size: Size from COMMON_CABLE_DATA (e.g., "500 kcmil")
        length_m: Length in meters
        voltage_nominal: Nominal voltage in kV
        system_base_mva: System base MVA
    
    Returns:
        Cable instance with impedance data from lookup table
    
    Example:
        >>> cable = create_cable_from_size(
        ...     id="CBL-001",
        ...     name="Main Feeder",
        ...     conductor_size="500 kcmil",
        ...     length_m=50.0,
        ...     voltage_nominal=0.48
        ... )
    """
    if conductor_size not in COMMON_CABLE_DATA:
        available = ", ".join(COMMON_CABLE_DATA.keys())
        raise ValueError(f"Unknown conductor size '{conductor_size}'. Available: {available}")
    
    r_per_km, x_per_km, ampacity = COMMON_CABLE_DATA[conductor_size]
    
    return Cable(
        id=id,
        name=name,
        length_m=length_m,
        r_per_km=r_per_km,
        x_per_km=x_per_km,
        voltage_nominal=voltage_nominal,
        system_base_mva=system_base_mva,
        ampacity=ampacity,
        conductor_size=conductor_size,
    )