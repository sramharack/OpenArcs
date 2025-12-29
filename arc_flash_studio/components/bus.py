"""
Bus Component
=============

Generic electrical bus - a connection point in the network.

Use Bus when the equipment type doesn't fit other categories
(Switchgear, Panel, MCC, etc.) or when specifying all parameters manually.

References:
    - IEEE 1584-2018, Section 6.2: Equipment classes

Traceability:
    - REQ-COMP-FUNC-1: Bus component
"""

from arc_flash_studio.components.base import NetworkNode
from arc_flash_studio.components.enums import EquipmentType


class Bus(NetworkNode):
    """
    Generic electrical bus.
    
    A Bus is the most basic network node. It represents a point
    where conductors connect and voltage is defined. Use this class
    when the equipment doesn't fit into a more specific category.
    
    For equipment-specific defaults, use:
        - Switchgear for LV/MV switchgear
        - Panelboard for distribution panels
        - MCC for motor control centers
        - CableJunction for junction boxes
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        voltage_kv: Nominal voltage in kilovolts
        gap_mm: Optional explicit gap distance
        working_distance_mm: Optional explicit working distance
        enclosure: Optional explicit enclosure info
    
    Example:
        >>> bus = Bus(id="B1", name="Main Bus", voltage_kv=0.48)
        >>> bus.voltage_level
        <VoltageLevel.LV: 'LV'>
        >>> bus.get_gap_mm()  # Uses default for generic equipment
        32.0
    """
    
    @property
    def equipment_type(self) -> EquipmentType:
        """Return generic equipment type."""
        return EquipmentType.OTHER