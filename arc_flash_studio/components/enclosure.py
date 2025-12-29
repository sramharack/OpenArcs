"""
Enclosure Model
===============

This module defines the EnclosureInfo class for arc flash enclosure parameters.

The enclosure size affects the enclosure size correction factor (CF)
in IEEE 1584-2018, which modifies the incident energy calculation.

References:
    - IEEE 1584-2018, Section 4.8: Enclosure size correction factor
    - IEEE 1584-2018, Table 9: Typical enclosure sizes

Traceability:
    - REQ-ARC-CALC-25: Enclosure size correction factor
"""

from pydantic import BaseModel, Field, PositiveFloat, computed_field, ConfigDict

from arc_flash_studio.components.enums import ElectrodeConfig


class EnclosureInfo(BaseModel):
    """
    Enclosure dimensions and configuration for arc flash calculations.
    
    IEEE 1584-2018 uses enclosure size to calculate the enclosure size
    correction factor (CF) which affects incident energy. Larger enclosures
    generally result in lower incident energy at the working distance.
    
    Attributes:
        height_mm: Internal height in millimeters
        width_mm: Internal width in millimeters
        depth_mm: Internal depth in millimeters
        electrode_config: Electrode arrangement (VCB, VCBB, HCB, VOA, HOA)
    
    Example:
        >>> enclosure = EnclosureInfo(
        ...     height_mm=914, width_mm=914, depth_mm=914,
        ...     electrode_config=ElectrodeConfig.VCB
        ... )
        >>> print(f"Size: {enclosure.height_in}\" x {enclosure.width_in}\"")
    """
    model_config = ConfigDict(frozen=False, validate_assignment=True)
    
    height_mm: PositiveFloat = Field(
        ..., 
        description="Internal enclosure height (mm)"
    )
    width_mm: PositiveFloat = Field(
        ..., 
        description="Internal enclosure width (mm)"
    )
    depth_mm: PositiveFloat = Field(
        ..., 
        description="Internal enclosure depth (mm)"
    )
    electrode_config: ElectrodeConfig = Field(
        default=ElectrodeConfig.VCB,
        description="Electrode configuration per IEEE 1584-2018"
    )
    
    @computed_field
    @property
    def height_in(self) -> float:
        """Height converted to inches."""
        return self.height_mm / 25.4
    
    @computed_field
    @property
    def width_in(self) -> float:
        """Width converted to inches."""
        return self.width_mm / 25.4
    
    @computed_field
    @property
    def depth_in(self) -> float:
        """Depth converted to inches."""
        return self.depth_mm / 25.4
    
    def __str__(self) -> str:
        return (
            f"Enclosure({self.height_mm}x{self.width_mm}x{self.depth_mm}mm, "
            f"{self.electrode_config.value})"
        )