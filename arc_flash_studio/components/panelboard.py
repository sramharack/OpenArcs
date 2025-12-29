"""
Panelboard Component
====================

Distribution panelboard (breaker panel).

Panelboards are typically smaller enclosures with closer
working distances than switchgear. Common in commercial
and industrial distribution systems.

References:
    - IEEE 1584-2018, Table 8: Typical gaps
    - IEEE 1584-2018, Table 3: Working distances

Traceability:
    - REQ-COMP-FUNC-3: Panelboard component with equipment-specific defaults
"""

from arc_flash_studio.components.base import NetworkNode
from arc_flash_studio.components.enums import EquipmentType


class Panelboard(NetworkNode):
    """
    Distribution panelboard.
    
    A panelboard is a panel containing overcurrent protective
    devices (circuit breakers or fuses) for distribution circuits.
    Typically found in lighting and power distribution systems.
    
    Default Arc Flash Parameters (per IEEE 1584-2018):
        - Gap: 25 mm
        - Working distance: 455 mm (18 inches)
        - Enclosure: 508 x 508 x 254 mm (20" x 20" x 10")
        - Configuration: VCB (vertical conductors in box)
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        voltage_kv: Nominal voltage in kilovolts
        gap_mm: Optional explicit gap (overrides default)
        working_distance_mm: Optional explicit working distance
        enclosure: Optional explicit enclosure info
    
    Example:
        >>> panel = Panelboard(id="LP-1", name="Lighting Panel", voltage_kv=0.208)
        >>> panel.equipment_type
        <EquipmentType.PANELBOARD: 'panelboard'>
        >>> panel.get_gap_mm()
        25.0
        >>> panel.get_working_distance_mm()
        455.0
    """
    
    @property
    def equipment_type(self) -> EquipmentType:
        """Return panelboard equipment type."""
        return EquipmentType.PANELBOARD