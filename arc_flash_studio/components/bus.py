"""
Bus Component
=============

A bus represents a node in the electrical network - a point where
components connect at a common voltage level.

In a single-line diagram, buses are the vertical bars where multiple
feeders, transformers, and loads connect.

Reference:
    - IEEE 1584-2018, Section 6.2
    - IEC 60909-0

Traceability:
    - REQ-COMP-FUNC-1: Bus class definition
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, PositiveFloat, computed_field, ConfigDict


class VoltageLevel(str, Enum):
    """Voltage level classification per IEEE 1584-2018."""
    LV = "LV"      # Low Voltage: ≤ 1000 V
    MV = "MV"      # Medium Voltage: > 1000 V to 35 kV
    HV = "HV"      # High Voltage: > 35 kV (outside IEEE 1584 scope)


class Bus(BaseModel):
    """
    Electrical bus - a node in the network at a specific voltage level.
    
    A bus is where components connect. It has no impedance itself;
    it's simply a connection point at a defined voltage.
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        voltage_nominal: Nominal voltage in kV
        voltage_base: Base voltage for per-unit calculations (defaults to nominal)
    
    Example:
        >>> bus = Bus(id="BUS-001", name="Main 480V Bus", voltage_nominal=0.48)
        >>> print(bus.voltage_level)
        VoltageLevel.LV
    """
    
    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        str_strip_whitespace=True,
    )
    
    # Input fields
    id: str = Field(
        ...,
        description="Unique identifier for the bus",
        min_length=1,
    )
    
    name: str = Field(
        ...,
        description="Human-readable name",
    )
    
    voltage_nominal: PositiveFloat = Field(
        ...,
        description="Nominal voltage in kV",
        examples=[0.208, 0.48, 4.16, 13.8],
    )
    
    voltage_base: Optional[PositiveFloat] = Field(
        default=None,
        description="Base voltage for per-unit calculations (kV). Defaults to nominal.",
    )
    
    # Optional metadata
    description: str = Field(
        default="",
        description="Additional notes about the bus",
    )
    
    @computed_field
    @property
    def voltage_base_kv(self) -> float:
        """Base voltage for per-unit calculations. Defaults to nominal if not set."""
        return self.voltage_base if self.voltage_base is not None else self.voltage_nominal
    
    @computed_field
    @property
    def voltage_level(self) -> VoltageLevel:
        """
        Classify voltage level per IEEE 1584-2018.
        
        - LV: ≤ 1.0 kV (1000 V)
        - MV: > 1.0 kV to 35 kV
        - HV: > 35 kV
        """
        if self.voltage_nominal <= 1.0:
            return VoltageLevel.LV
        elif self.voltage_nominal <= 35.0:
            return VoltageLevel.MV
        else:
            return VoltageLevel.HV
    
    @computed_field
    @property
    def in_ieee1584_scope(self) -> bool:
        """Check if voltage is within IEEE 1584-2018 scope (0.208 to 15 kV)."""
        return 0.208 <= self.voltage_nominal <= 15.0
    
    def __str__(self) -> str:
        return f"Bus('{self.id}': {self.name}, {self.voltage_nominal} kV)"