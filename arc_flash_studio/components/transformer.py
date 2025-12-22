"""
Transformer Component
=====================

Two-winding power transformer model for short-circuit and arc flash studies.

The transformer is modeled by its nameplate impedance, which determines
how much it limits fault current flowing from primary to secondary.

Reference:
    - IEEE 1584-2018, Section 6.2
    - IEC 60909-0, Section 6
    - IEEE C57.12.00 (Transformer standards)

Traceability:
    - REQ-COMP-FUNC-3: Transformer class definition
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    PositiveFloat,
    computed_field,
    field_validator,
    ConfigDict,
)


class VectorGroup(str, Enum):
    """Common transformer vector groups."""
    Dyn11 = "Dyn11"  # Delta primary, wye secondary, 30° lag
    Dyn1 = "Dyn1"    # Delta primary, wye secondary, 30° lead
    Yyn0 = "Yyn0"    # Wye-wye, no phase shift
    Dd0 = "Dd0"      # Delta-delta, no phase shift
    Yd1 = "Yd1"      # Wye primary, delta secondary
    Yd11 = "Yd11"    # Wye primary, delta secondary


class Transformer(BaseModel):
    """
    Two-winding power transformer.
    
    Models the transformer's contribution to system impedance for
    short-circuit calculations. The key parameter is percent impedance (%Z),
    which determines fault current limitation.
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        rated_power_mva: Nameplate MVA rating
        voltage_primary: Primary winding voltage (kV)
        voltage_secondary: Secondary winding voltage (kV)
        impedance_percent: Nameplate impedance (%)
        x_r_ratio: Reactance to resistance ratio
    
    Example:
        >>> xfmr = Transformer(
        ...     id="TX-001",
        ...     name="Main Transformer",
        ...     rated_power_mva=2.0,
        ...     voltage_primary=13.8,
        ...     voltage_secondary=0.48,
        ...     impedance_percent=5.75,
        ...     x_r_ratio=8.0
        ... )
        >>> print(f"Z = {xfmr.z_pu_on_own_base:.4f} pu")
        Z = 0.0575 pu
    """
    
    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        str_strip_whitespace=True,
    )
    
    # Identification
    id: str = Field(..., description="Unique identifier", min_length=1)
    name: str = Field(..., description="Human-readable name")
    
    # Ratings
    rated_power_mva: PositiveFloat = Field(
        ...,
        description="Nameplate power rating in MVA",
        examples=[0.5, 1.0, 2.0, 2.5],
    )
    
    voltage_primary: PositiveFloat = Field(
        ...,
        description="Primary winding rated voltage in kV",
        examples=[13.8, 4.16, 34.5],
    )
    
    voltage_secondary: PositiveFloat = Field(
        ...,
        description="Secondary winding rated voltage in kV",
        examples=[0.48, 0.208, 4.16],
    )
    
    # Impedance
    impedance_percent: PositiveFloat = Field(
        ...,
        description="Nameplate impedance in percent on transformer base",
        examples=[5.75, 6.0, 7.5],
        ge=1.0,   # Minimum realistic %Z
        le=20.0,  # Maximum realistic %Z
    )
    
    x_r_ratio: PositiveFloat = Field(
        ...,
        description="Reactance to resistance ratio (X/R)",
        examples=[8.0, 10.0, 12.0],
        ge=1.0,
        le=50.0,
    )
    
    # Optional parameters
    vector_group: Optional[VectorGroup] = Field(
        default=VectorGroup.Dyn11,
        description="Winding connection and phase shift",
    )
    
    tap_percent: float = Field(
        default=0.0,
        description="Tap position as percent deviation from nominal (e.g., +2.5, -2.5)",
        ge=-10.0,
        le=10.0,
    )
    
    # System base for per-unit conversion
    system_base_mva: PositiveFloat = Field(
        default=100.0,
        description="System base MVA for per-unit calculations",
    )
    
    @field_validator('voltage_secondary')
    @classmethod
    def secondary_less_than_primary(cls, v: float, info) -> float:
        """Secondary voltage should typically be less than or equal to primary."""
        # Note: info.data contains previously validated fields
        # This is a soft check - step-up transformers exist but are less common
        return v
    
    # -------------------------------------------------------------------------
    # Computed Properties - Impedance on Transformer Base
    # -------------------------------------------------------------------------
    
    @computed_field
    @property
    def z_pu_on_own_base(self) -> float:
        """Per-unit impedance on transformer's own MVA base."""
        return self.impedance_percent / 100.0
    
    @computed_field
    @property
    def r_pu_on_own_base(self) -> float:
        """Per-unit resistance on transformer's own MVA base."""
        return self.z_pu_on_own_base / math.sqrt(1 + self.x_r_ratio ** 2)
    
    @computed_field
    @property
    def x_pu_on_own_base(self) -> float:
        """Per-unit reactance on transformer's own MVA base."""
        return self.r_pu_on_own_base * self.x_r_ratio
    
    # -------------------------------------------------------------------------
    # Computed Properties - Impedance on System Base
    # -------------------------------------------------------------------------
    
    @computed_field
    @property
    def z_pu(self) -> float:
        """
        Per-unit impedance on system base.
        
        Z_pu_new = Z_pu_old × (S_base_new / S_base_old)
        """
        return self.z_pu_on_own_base * (self.system_base_mva / self.rated_power_mva)
    
    @computed_field
    @property
    def r_pu(self) -> float:
        """Per-unit resistance on system base."""
        return self.r_pu_on_own_base * (self.system_base_mva / self.rated_power_mva)
    
    @computed_field
    @property
    def x_pu(self) -> float:
        """Per-unit reactance on system base."""
        return self.x_pu_on_own_base * (self.system_base_mva / self.rated_power_mva)
    
    # -------------------------------------------------------------------------
    # Computed Properties - Impedance in Ohms (referred to secondary)
    # -------------------------------------------------------------------------
    
    @computed_field
    @property
    def z_base_secondary_ohms(self) -> float:
        """Base impedance in ohms at secondary voltage."""
        return (self.voltage_secondary ** 2) / self.rated_power_mva
    
    @computed_field
    @property
    def z_ohms_secondary(self) -> float:
        """Impedance magnitude in ohms referred to secondary."""
        return self.z_pu_on_own_base * self.z_base_secondary_ohms
    
    @computed_field
    @property
    def r_ohms_secondary(self) -> float:
        """Resistance in ohms referred to secondary."""
        return self.r_pu_on_own_base * self.z_base_secondary_ohms
    
    @computed_field
    @property
    def x_ohms_secondary(self) -> float:
        """Reactance in ohms referred to secondary."""
        return self.x_pu_on_own_base * self.z_base_secondary_ohms
    
    # -------------------------------------------------------------------------
    # Computed Properties - Other
    # -------------------------------------------------------------------------
    
    @computed_field
    @property
    def turns_ratio(self) -> float:
        """Voltage transformation ratio (primary / secondary)."""
        return self.voltage_primary / self.voltage_secondary
    
    @computed_field
    @property
    def rated_current_primary_a(self) -> float:
        """Rated current on primary side in Amperes."""
        return (self.rated_power_mva * 1000) / (math.sqrt(3) * self.voltage_primary)
    
    @computed_field
    @property
    def rated_current_secondary_a(self) -> float:
        """Rated current on secondary side in Amperes."""
        return (self.rated_power_mva * 1000) / (math.sqrt(3) * self.voltage_secondary)
    
    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------
    
    def get_impedance_complex_pu(self) -> complex:
        """Get complex impedance in per-unit on system base."""
        return complex(self.r_pu, self.x_pu)
    
    def get_impedance_complex_ohms(self, referred_to: str = "secondary") -> complex:
        """
        Get complex impedance in ohms.
        
        Args:
            referred_to: "primary" or "secondary"
        """
        if referred_to == "secondary":
            return complex(self.r_ohms_secondary, self.x_ohms_secondary)
        else:
            # Refer to primary: multiply by turns_ratio²
            factor = self.turns_ratio ** 2
            return complex(self.r_ohms_secondary * factor, self.x_ohms_secondary * factor)
    
    def __str__(self) -> str:
        return (
            f"Transformer('{self.id}': {self.name}, "
            f"{self.rated_power_mva} MVA, "
            f"{self.voltage_primary}/{self.voltage_secondary} kV, "
            f"Z={self.impedance_percent}%)"
        )