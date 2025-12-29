"""
Transformer Component
=====================

Two-winding power transformer.

Transforms voltage between two levels. Characterized by its
MVA rating, voltage ratio, and impedance.

References:
    - IEC 60909-0: Transformer impedance for short-circuit
    - IEEE C57.12.00: Transformer standards

Traceability:
    - REQ-COMP-FUNC-8: Transformer with impedance conversion
"""

import math

from pydantic import BaseModel, Field, PositiveFloat, computed_field, ConfigDict


class Transformer(BaseModel):
    """
    Two-winding power transformer.
    
    A Transformer connects two voltage levels and introduces
    impedance into the network. In PandaPower, this becomes
    a transformer element.
    
    Key Parameters:
        - impedance_percent: Nameplate %Z (typically 4-8% for distribution)
        - x_r_ratio: X/R ratio (typically 5-15 for power transformers)
    
    Conversion to PandaPower:
        - impedance_percent → vk_percent
        - vkr_percent = impedance_percent / sqrt(1 + (X/R)²)
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        hv_bus_id: High-voltage side bus ID
        lv_bus_id: Low-voltage side bus ID
        rated_mva: Nameplate MVA rating
        hv_kv: High-voltage winding voltage (kV)
        lv_kv: Low-voltage winding voltage (kV)
        impedance_percent: Nameplate impedance (%Z)
        x_r_ratio: X/R ratio
        vector_group: Winding connection (e.g., "Dyn11")
    
    Example:
        >>> xfmr = Transformer(
        ...     id="TX-1",
        ...     name="Main Transformer",
        ...     hv_bus_id="HV-BUS",
        ...     lv_bus_id="LV-BUS",
        ...     rated_mva=2.0,
        ...     hv_kv=13.8,
        ...     lv_kv=0.48,
        ...     impedance_percent=5.75,
        ...     x_r_ratio=8.0
        ... )
        >>> xfmr.vkr_percent  # Resistive component
        0.713
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
    hv_bus_id: str = Field(
        ..., 
        description="High-voltage side bus ID"
    )
    lv_bus_id: str = Field(
        ..., 
        description="Low-voltage side bus ID"
    )
    
    # Ratings
    rated_mva: PositiveFloat = Field(
        ..., 
        description="Nameplate MVA rating"
    )
    hv_kv: PositiveFloat = Field(
        ..., 
        description="High-voltage winding voltage (kV)"
    )
    lv_kv: PositiveFloat = Field(
        ..., 
        description="Low-voltage winding voltage (kV)"
    )
    
    # Impedance
    impedance_percent: PositiveFloat = Field(
        ...,
        ge=1.0,
        le=20.0,
        description="Nameplate impedance (%Z), typically 4-8% for distribution"
    )
    x_r_ratio: PositiveFloat = Field(
        ...,
        ge=1.0,
        le=50.0,
        description="X/R ratio, typically 5-15 for power transformers"
    )
    
    # Vector group (winding connection)
    vector_group: str = Field(
        default="Dyn",
        description="Winding connection (e.g., Dyn11, Yyn0, Dd0)"
    )
    
    @computed_field
    @property
    def vkr_percent(self) -> float:
        """
        Resistive component of short-circuit voltage.
        
        PandaPower requires both vk_percent (total) and vkr_percent
        (resistive component) to properly model the transformer.
        
        Calculation:
            R/Z = 1 / sqrt(1 + (X/R)²)
            vkr = vk × (R/Z)
        
        Returns:
            Resistive component of impedance (%)
        """
        r_over_z = 1.0 / math.sqrt(1.0 + self.x_r_ratio ** 2)
        return self.impedance_percent * r_over_z
    
    @computed_field
    @property
    def turns_ratio(self) -> float:
        """
        Transformer turns ratio (HV/LV).
        
        Returns:
            Ratio of HV to LV voltage
        """
        return self.hv_kv / self.lv_kv
    
    def __str__(self) -> str:
        return (
            f"Transformer({self.id}, {self.rated_mva} MVA, "
            f"{self.hv_kv}/{self.lv_kv} kV)"
        )