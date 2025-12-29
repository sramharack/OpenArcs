"""
Cable Component
===============

Power cable or busway connecting two buses.

Cables introduce impedance (resistance and reactance) between
buses based on their length and per-unit-length parameters.

References:
    - NEC Chapter 9, Table 9: Conductor impedance
    - IEEE 141 (Red Book): Cable impedance data

Traceability:
    - REQ-COMP-FUNC-9: Cable with impedance parameters
    - REQ-COMP-DATA-4: Cable lookup table from NEC Table 9
"""

from typing import Optional

from pydantic import BaseModel, Field, PositiveFloat, computed_field, ConfigDict


class Cable(BaseModel):
    """
    Power cable or busway.
    
    A Cable connects two buses and introduces series impedance.
    In PandaPower, this becomes a line element.
    
    Impedance Parameters:
        - r_ohm_per_km: Resistance per kilometer
        - x_ohm_per_km: Reactance per kilometer
        - length_m: Cable length in meters
    
    These values can be specified directly or looked up from
    the CABLE_DATA table using create_cable().
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        from_bus_id: Source bus ID
        to_bus_id: Destination bus ID
        length_m: Cable length in meters
        r_ohm_per_km: Resistance (Ω/km)
        x_ohm_per_km: Reactance (Ω/km)
        ampacity_a: Optional continuous current rating (A)
        conductor_size: Optional conductor size string
    
    Example:
        >>> cable = Cable(
        ...     id="C1", name="Feeder",
        ...     from_bus_id="B1", to_bus_id="B2",
        ...     length_m=30,
        ...     r_ohm_per_km=0.105,
        ...     x_ohm_per_km=0.128
        ... )
        >>> cable.length_km
        0.03
    """
    model_config = ConfigDict(frozen=False, validate_assignment=True)
    
    # Identification
    id: str = Field(
        ..., 
        min_length=1, 
        description="Unique identifier"
    )
    name: str = Field(
        ..., 
        description="Human-readable name"
    )
    
    # Connections
    from_bus_id: str = Field(
        ..., 
        description="Source bus ID"
    )
    to_bus_id: str = Field(
        ..., 
        description="Destination bus ID"
    )
    
    # Physical parameters
    length_m: PositiveFloat = Field(
        ..., 
        description="Cable length in meters"
    )
    r_ohm_per_km: PositiveFloat = Field(
        ..., 
        description="Resistance per kilometer (Ω/km)"
    )
    x_ohm_per_km: PositiveFloat = Field(
        ..., 
        description="Reactance per kilometer (Ω/km)"
    )
    
    # Optional parameters
    ampacity_a: Optional[PositiveFloat] = Field(
        default=None,
        description="Continuous current rating (A)"
    )
    conductor_size: Optional[str] = Field(
        default=None,
        description="Conductor size (e.g., '500 kcmil', '4/0 AWG')"
    )
    
    @computed_field
    @property
    def length_km(self) -> float:
        """Cable length in kilometers."""
        return self.length_m / 1000.0
    
    @computed_field
    @property
    def r_ohms(self) -> float:
        """Total cable resistance in ohms."""
        return self.r_ohm_per_km * self.length_km
    
    @computed_field
    @property
    def x_ohms(self) -> float:
        """Total cable reactance in ohms."""
        return self.x_ohm_per_km * self.length_km
    
    def __str__(self) -> str:
        size = f", {self.conductor_size}" if self.conductor_size else ""
        return f"Cable({self.id}, {self.length_m}m{size})"


# =============================================================================
# Cable Lookup Table
# =============================================================================
# Source: NEC Chapter 9, Table 9 (Copper conductors in steel conduit at 75°C)
# Format: (r_ohm_per_km, x_ohm_per_km, ampacity_a)

CABLE_DATA: dict[str, tuple[float, float, float]] = {
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


def create_cable(
    id: str,
    name: str,
    from_bus_id: str,
    to_bus_id: str,
    length_m: float,
    conductor_size: str,
) -> Cable:
    """
    Create a Cable using standard conductor data from NEC Table 9.
    
    This is a convenience function that looks up impedance values
    from the CABLE_DATA table based on conductor size.
    
    Args:
        id: Unique identifier
        name: Human-readable name
        from_bus_id: Source bus ID
        to_bus_id: Destination bus ID
        length_m: Cable length in meters
        conductor_size: Size from CABLE_DATA (e.g., "500 kcmil", "4/0 AWG")
    
    Returns:
        Cable instance with impedance from lookup table
    
    Raises:
        ValueError: If conductor_size not found in CABLE_DATA
    
    Example:
        >>> cable = create_cable(
        ...     id="C1", name="Feeder",
        ...     from_bus_id="B1", to_bus_id="B2",
        ...     length_m=30, conductor_size="500 kcmil"
        ... )
        >>> cable.r_ohm_per_km
        0.105
    
    Reference:
        NEC Chapter 9, Table 9
    """
    if conductor_size not in CABLE_DATA:
        available = ", ".join(sorted(CABLE_DATA.keys()))
        raise ValueError(
            f"Unknown conductor size '{conductor_size}'. "
            f"Available sizes: {available}"
        )
    
    r, x, amp = CABLE_DATA[conductor_size]
    
    return Cable(
        id=id,
        name=name,
        from_bus_id=from_bus_id,
        to_bus_id=to_bus_id,
        length_m=length_m,
        r_ohm_per_km=r,
        x_ohm_per_km=x,
        ampacity_a=amp,
        conductor_size=conductor_size,
    )