"""
Utility Source Component
========================

Utility (grid) connection point - external power source.

The utility source represents the connection to the electric
utility grid. It's characterized by its available short-circuit
MVA and X/R ratio.

References:
    - IEC 60909-0: External grid representation
    - IEEE 551 (Violet Book): Utility source modeling

Traceability:
    - REQ-COMP-FUNC-7: Utility source with short-circuit parameters
"""

from pydantic import BaseModel, Field, PositiveFloat, computed_field, ConfigDict


class UtilitySource(BaseModel):
    """
    Utility (grid) connection.
    
    A UtilitySource represents the connection to the electric
    utility grid. In PandaPower, this becomes an ext_grid element.
    
    The utility is characterized by:
        - short_circuit_mva: Maximum available fault current capacity
        - x_r_ratio: Ratio of reactance to resistance (affects DC offset)
    
    These parameters are typically provided by the utility company
    or estimated based on the service voltage and transformer size.
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        bus_id: ID of the bus where utility connects
        short_circuit_mva: Available 3-phase short-circuit MVA
        x_r_ratio: X/R ratio of the utility source impedance
    
    PandaPower Mapping:
        - short_circuit_mva → s_sc_max_mva
        - x_r_ratio → converted to rx_max (R/X = 1/(X/R))
    
    Example:
        >>> utility = UtilitySource(
        ...     id="UTIL-1",
        ...     name="Grid Connection",
        ...     bus_id="MAIN-BUS",
        ...     short_circuit_mva=500,
        ...     x_r_ratio=15
        ... )
        >>> utility.rx_ratio  # For PandaPower
        0.0667
    """
    model_config = ConfigDict(frozen=False, validate_assignment=True)
    
    id: str = Field(
        ..., 
        min_length=1, 
        description="Unique identifier"
    )
    name: str = Field(
        ..., 
        description="Human-readable name"
    )
    bus_id: str = Field(
        ..., 
        description="ID of the bus where this utility connects"
    )
    
    # Short-circuit parameters
    short_circuit_mva: PositiveFloat = Field(
        ...,
        description="Available 3-phase short-circuit MVA from utility"
    )
    x_r_ratio: PositiveFloat = Field(
        ...,
        ge=1.0,
        le=100.0,
        description="X/R ratio of utility source impedance (typically 10-20)"
    )
    
    @computed_field
    @property
    def rx_ratio(self) -> float:
        """
        R/X ratio (reciprocal of X/R).
        
        PandaPower uses R/X ratio (rx_max) rather than X/R ratio.
        
        Returns:
            R/X ratio = 1 / (X/R ratio)
        """
        return 1.0 / self.x_r_ratio
    
    def __str__(self) -> str:
        return f"UtilitySource({self.id}, {self.short_circuit_mva} MVA)"