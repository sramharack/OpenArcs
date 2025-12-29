"""
Base Classes for Network Components
====================================

This module defines the abstract base class for all network nodes.

All equipment that represents a point in the electrical network
(bus, switchgear, panel, MCC, etc.) inherits from NetworkNode.
In PandaPower terms, every NetworkNode becomes a bus.

References:
    - IEEE 1584-2018, Section 6.2: Equipment classes

Traceability:
    - REQ-COMP-FUNC-1: Network node base properties
"""

from typing import Optional

from pydantic import BaseModel, Field, PositiveFloat, computed_field, ConfigDict

from arc_flash_studio.components.enums import (
    VoltageLevel, 
    ElectrodeConfig, 
    EquipmentType
)
from arc_flash_studio.components.enclosure import EnclosureInfo
from arc_flash_studio.components.defaults import (
    get_default_gap_mm,
    get_default_working_distance_mm,
    get_default_enclosure_size_mm,
)


class NetworkNode(BaseModel):
    """
    Abstract base class for network nodes (buses).
    
    A NetworkNode represents any point in the electrical network where
    voltage is defined and connections can be made. All equipment types
    (Bus, Switchgear, Panel, MCC, etc.) inherit from this class.
    
    In PandaPower, every NetworkNode becomes a bus. The equipment type
    determines arc flash parameters but not short-circuit behavior.
    
    Attributes:
        id: Unique identifier for the node
        name: Human-readable name
        voltage_kv: Nominal voltage in kilovolts
        gap_mm: Conductor gap (mm). If None, uses equipment default.
        working_distance_mm: Working distance (mm). If None, uses default.
        enclosure: Enclosure info. If None, uses equipment default.
    
    Computed Properties:
        voltage_level: Classification (LV, MV, HV)
        in_ieee1584_scope: True if within 0.208-15 kV range
        equipment_type: Type of equipment (override in subclasses)
    
    Example:
        >>> from arc_flash_studio.components import Switchgear
        >>> swgr = Switchgear(id="SWGR-1", name="Main Switchgear", voltage_kv=0.48)
        >>> print(swgr.get_gap_mm())  # Returns 32.0 (LV switchgear default)
    """
    model_config = ConfigDict(frozen=False, validate_assignment=True)
    
    # Identification
    id: str = Field(
        ..., 
        min_length=1, 
        description="Unique identifier for this node"
    )
    name: str = Field(
        ..., 
        description="Human-readable name"
    )
    
    # Electrical parameters
    voltage_kv: PositiveFloat = Field(
        ..., 
        description="Nominal voltage in kilovolts"
    )
    
    # Arc flash parameters (optional - defaults used if not specified)
    gap_mm: Optional[PositiveFloat] = Field(
        default=None,
        description="Conductor gap (mm). Uses equipment default if not specified."
    )
    working_distance_mm: Optional[PositiveFloat] = Field(
        default=None,
        description="Working distance (mm). Uses equipment default if not specified."
    )
    enclosure: Optional[EnclosureInfo] = Field(
        default=None,
        description="Enclosure dimensions. Uses equipment default if not specified."
    )
    
    # -------------------------------------------------------------------------
    # Computed Properties
    # -------------------------------------------------------------------------
    
    @computed_field
    @property
    def voltage_level(self) -> VoltageLevel:
        """
        Classify voltage level per IEEE 1584-2018.
        
        Returns:
            VoltageLevel.LV for ≤ 1 kV
            VoltageLevel.MV for > 1 kV to 35 kV
            VoltageLevel.HV for > 35 kV
        """
        if self.voltage_kv <= 1.0:
            return VoltageLevel.LV
        elif self.voltage_kv <= 35.0:
            return VoltageLevel.MV
        else:
            return VoltageLevel.HV
    
    @computed_field
    @property
    def in_ieee1584_scope(self) -> bool:
        """
        Check if voltage is within IEEE 1584-2018 scope.
        
        IEEE 1584-2018 applies to three-phase systems from
        208 V to 15,000 V.
        
        Returns:
            True if 0.208 kV ≤ voltage ≤ 15 kV
        """
        return 0.208 <= self.voltage_kv <= 15.0
    
    # -------------------------------------------------------------------------
    # Equipment Type (Override in subclasses)
    # -------------------------------------------------------------------------
    
    @property
    def equipment_type(self) -> EquipmentType:
        """
        Equipment type for arc flash parameter defaults.
        
        Override this property in subclasses to return the
        appropriate equipment type.
        
        Returns:
            EquipmentType enum value
        """
        return EquipmentType.OTHER
    
    # -------------------------------------------------------------------------
    # Arc Flash Parameter Methods
    # -------------------------------------------------------------------------
    
    def get_gap_mm(self) -> float:
        """
        Get conductor gap distance.
        
        Returns explicitly set gap_mm if provided, otherwise
        returns the default for this equipment type and voltage level.
        
        Returns:
            Gap distance in millimeters
        
        Reference:
            IEEE 1584-2018 Table 8
        """
        if self.gap_mm is not None:
            return self.gap_mm
        return get_default_gap_mm(self.equipment_type, self.voltage_level)
    
    def get_working_distance_mm(self) -> float:
        """
        Get working distance.
        
        Returns explicitly set working_distance_mm if provided,
        otherwise returns the default for this equipment type.
        
        Returns:
            Working distance in millimeters
        
        Reference:
            IEEE 1584-2018 Table 3
        """
        if self.working_distance_mm is not None:
            return self.working_distance_mm
        return get_default_working_distance_mm(self.equipment_type)
    
    def get_enclosure(self) -> EnclosureInfo:
        """
        Get enclosure information.
        
        Returns explicitly set enclosure if provided, otherwise
        creates a default enclosure for this equipment type.
        
        Returns:
            EnclosureInfo with dimensions and electrode config
        
        Reference:
            IEEE 1584-2018 Table 9
        """
        if self.enclosure is not None:
            return self.enclosure
        
        h, w, d = get_default_enclosure_size_mm(self.equipment_type)
        return EnclosureInfo(
            height_mm=h,
            width_mm=w,
            depth_mm=d,
            electrode_config=ElectrodeConfig.VCB
        )
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id}, {self.voltage_kv}kV)"