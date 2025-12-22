"""
Utility Source Component (Pydantic Implementation)
==================================================

Represents a utility grid connection as a Thévenin equivalent source.

This component models the "infinite bus" connection to the utility grid,
characterized by its available short-circuit capacity (MVA) and X/R ratio.

Reference:
    - IEEE 1584-2018, Section 6.2
    - IEC 60909-0, Section 6 (Network feeder)
    - IEEE 551 (Violet Book), Chapter 4

Traceability:
    - REQ-COMP-FUNC-7: UtilitySource class definition
"""

from __future__ import annotations

import math

# =============================================================================
# PYDANTIC IMPORTS EXPLAINED
# =============================================================================
#
# BaseModel: The parent class for all Pydantic models (like dataclass but better)
# Field: Adds constraints, defaults, and documentation to fields
# PositiveFloat: A float that must be > 0 (built-in validation!)
# computed_field: Decorator for properties that should be included in serialization
# field_validator: Decorator for custom validation logic on a specific field
# model_validator: Decorator for validation that involves multiple fields
# ConfigDict: Type-safe way to configure model behavior

from pydantic import (
    BaseModel,
    Field,
    PositiveFloat,
    computed_field,
    field_validator,
    ConfigDict,
)


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_SYSTEM_BASE_MVA: float = 100.0


# =============================================================================
# THE PYDANTIC MODEL
# =============================================================================

class UtilitySource(BaseModel):
    """
    Utility grid connection modeled as a Thévenin equivalent.
    
    The utility source represents the grid's contribution to fault current
    at the point of common coupling (PCC). It is characterized by:
    
    - Available short-circuit MVA (fault capacity)
    - X/R ratio (determines DC offset and asymmetry)
    - Nominal voltage at the connection point
    
    Example:
        >>> source = UtilitySource(
        ...     id="UTIL-001",
        ...     name="Main Utility Feed",
        ...     short_circuit_mva=500.0,
        ...     voltage_nominal=13.8,
        ...     x_r_ratio=15.0
        ... )
        >>> print(f"Z = {source.z_pu:.4f} pu")
        Z = 0.2000 pu
        
        >>> # Export to JSON (built-in!)
        >>> print(source.model_dump_json(indent=2))
        
        >>> # Create from JSON (built-in!)
        >>> source2 = UtilitySource.model_validate_json('{"id": "U1", ...}')
    """
    
    # -------------------------------------------------------------------------
    # MODEL CONFIGURATION
    # -------------------------------------------------------------------------
    # This replaces the old @dataclass decorator options
    # ConfigDict is a TypedDict that provides IDE autocomplete for options
    
    model_config = ConfigDict(
        # If True, objects become immutable after creation (like frozen=True in dataclass)
        frozen=False,
        
        # If True, re-validates when you change an attribute
        # e.g., source.short_circuit_mva = 600  # This triggers validation
        validate_assignment=True,
        
        # Strip whitespace from string fields automatically
        str_strip_whitespace=True,
        
        # Add JSON schema extras for documentation
        json_schema_extra={
            "examples": [
                {
                    "id": "UTIL-001",
                    "name": "Main Utility Feed", 
                    "short_circuit_mva": 500.0,
                    "voltage_nominal": 13.8,
                    "x_r_ratio": 15.0
                }
            ]
        }
    )
    
    # -------------------------------------------------------------------------
    # INPUT FIELDS (what the user provides)
    # -------------------------------------------------------------------------
    # 
    # Field() is optional but lets you add:
    #   - description: Shows up in JSON schema and documentation
    #   - examples: Sample values for documentation
    #   - ge, gt, le, lt: Greater/less than (or equal) constraints
    #   - default: Default value (or ... for required)
    #
    # PositiveFloat is equivalent to: float = Field(gt=0)
    # It automatically rejects zero and negative values!
    
    id: str = Field(
        ...,  # ... means REQUIRED (no default)
        description="Unique identifier for the component",
        examples=["UTIL-001", "UTIL-MAIN", "SOURCE-A"],
        min_length=1,  # Can't be empty string
    )
    
    name: str = Field(
        ...,
        description="Human-readable name",
        examples=["Main Utility Feed", "Backup Source"],
    )
    
    short_circuit_mva: PositiveFloat = Field(
        ...,
        description="Available three-phase short-circuit MVA at the connection point",
        examples=[500.0, 150.0, 1000.0],
        # You could add realistic bounds:
        # ge=10.0,   # Minimum 10 MVA (very weak source)
        # le=100000.0,  # Maximum 100 GVA (strongest transmission)
    )
    
    voltage_nominal: PositiveFloat = Field(
        ...,
        description="Nominal voltage at the connection point in kV, limited to 15kV",
        examples=[13.8, 4.16, 0.48, 15],
    )
    
    x_r_ratio: PositiveFloat = Field(
        ...,
        description="Reactance to resistance ratio (X/R) of the source impedance",
        examples=[15.0, 10.0, 20.0],
        ge=1.0,   # X/R < 1 is unrealistic for utility (would mean more R than X)
        le=100.0,  # X/R > 100 is unrealistic
    )
    
    system_base_mva: PositiveFloat = Field(
        default=DEFAULT_SYSTEM_BASE_MVA,
        description="System base MVA for per-unit calculations",
        examples=[100.0, 10.0],
    )
    
    # -------------------------------------------------------------------------
    # CUSTOM VALIDATORS
    # -------------------------------------------------------------------------
    # Use @field_validator when you need logic beyond simple constraints
    # The validator receives the value AFTER Pydantic's type coercion
    
    @field_validator('voltage_nominal')
    @classmethod
    def validate_voltage_range(cls, v: float) -> float:
        """
        Validate voltage is in a reasonable range.
        
        Note: This is a loose check for utility voltage.
        IEEE 1584-2018 scope is 0.208-15 kV, but utility connections
        can be at transmission voltage (69, 138, 230+ kV).
        """
        if v > 500:
            raise ValueError(
                f"voltage_nominal {v} kV exceeds maximum expected utility voltage (500 kV)"
            )
        return v
    
    @field_validator('id')
    @classmethod  
    def validate_id_format(cls, v: str) -> str:
        """Ensure ID doesn't contain problematic characters."""
        # Remove any accidental whitespace
        v = v.strip()
        if not v:
            raise ValueError("id cannot be empty or whitespace only")
        return v
    
    # -------------------------------------------------------------------------
    # COMPUTED FIELDS (derived from inputs)
    # -------------------------------------------------------------------------
    # @computed_field makes a @property that:
    #   1. Gets included in .model_dump() and .model_dump_json()
    #   2. Shows up in the JSON schema
    #   3. Is cached (computed once, not on every access)
    #
    # The math here is identical to our dataclass version
    
    @computed_field
    @property
    def z_pu(self) -> float:
        """
        Per-unit impedance magnitude on system base.
        
        Z_pu = S_base / SC_MVA
        
        Reference: IEC 60909-0, Section 6
        """
        return self.system_base_mva / self.short_circuit_mva
    
    @computed_field
    @property
    def r_pu(self) -> float:
        """
        Per-unit resistance on system base.
        
        From Z and X/R ratio:
            Z = √(R² + X²)
            X = R × (X/R)
            Z = R × √(1 + (X/R)²)
            R = Z / √(1 + (X/R)²)
        """
        return self.z_pu / math.sqrt(1 + self.x_r_ratio ** 2)
    
    @computed_field
    @property
    def x_pu(self) -> float:
        """
        Per-unit reactance on system base.
        
        X = R × (X/R)
        """
        return self.r_pu * self.x_r_ratio
    
    @computed_field
    @property
    def z_base_ohms(self) -> float:
        """
        Base impedance in ohms at nominal voltage.
        
        Z_base = V² / S = (kV)² / MVA  [Ω]
        """
        return (self.voltage_nominal ** 2) / self.system_base_mva
    
    @computed_field
    @property
    def z_ohms(self) -> float:
        """Impedance magnitude in ohms at nominal voltage."""
        return self.z_pu * self.z_base_ohms
    
    @computed_field
    @property
    def r_ohms(self) -> float:
        """Resistance in ohms at nominal voltage."""
        return self.r_pu * self.z_base_ohms
    
    @computed_field
    @property
    def x_ohms(self) -> float:
        """Reactance in ohms at nominal voltage."""
        return self.x_pu * self.z_base_ohms
    
    @computed_field
    @property
    def available_fault_current_ka(self) -> float:
        """
        Three-phase symmetrical fault current in kA.
        
        I_fault = SC_MVA / (√3 × V_kV)
        """
        return self.short_circuit_mva / (math.sqrt(3) * self.voltage_nominal)
    
    @computed_field
    @property
    def impedance_angle_deg(self) -> float:
        """Impedance angle in degrees (arctan of X/R)."""
        return math.degrees(math.atan(self.x_r_ratio))
    
    # -------------------------------------------------------------------------
    # METHODS (same as before)
    # -------------------------------------------------------------------------
    
    def get_impedance_at_voltage(self, voltage_kv: float) -> float:
        """
        Get impedance magnitude referred to a different voltage level.
        
        Impedance transforms with the square of the voltage ratio:
            Z_new = Z_old × (V_new / V_old)²
        
        Args:
            voltage_kv: Target voltage level in kV
        
        Returns:
            Impedance magnitude in ohms at the target voltage
        
        Example:
            >>> source = UtilitySource(id="U1", name="Test", 
            ...     short_circuit_mva=500, voltage_nominal=13.8, x_r_ratio=15)
            >>> z_at_4kv = source.get_impedance_at_voltage(4.16)
        """
        if voltage_kv <= 0:
            raise ValueError(f"voltage_kv must be positive, got {voltage_kv}")
        voltage_ratio_squared = (voltage_kv / self.voltage_nominal) ** 2
        return self.z_ohms * voltage_ratio_squared
    
    def get_impedance_complex(self) -> complex:
        """Get complex impedance in per-unit."""
        return complex(self.r_pu, self.x_pu)
    
    def get_impedance_complex_ohms(self) -> complex:
        """Get complex impedance in ohms at nominal voltage."""
        return complex(self.r_ohms, self.x_ohms)
    
    # -------------------------------------------------------------------------
    # STRING REPRESENTATION
    # -------------------------------------------------------------------------
    # Pydantic provides __repr__ automatically, but we can customize __str__
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"UtilitySource('{self.id}': {self.name}, "
            f"{self.short_circuit_mva} MVA @ {self.voltage_nominal} kV, "
            f"X/R={self.x_r_ratio})"
        )