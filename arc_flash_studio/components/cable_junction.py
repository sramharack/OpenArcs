"""
Cable Junction Component
========================

Cable junction box or splice box.

Small enclosures where cables are joined or spliced.
These typically have the smallest gaps of enclosed equipment.

References:
    - IEEE 1584-2018, Table 8: Typical gaps

Traceability:
    - REQ-COMP-FUNC-5: Cable junction component
"""

from arc_flash_studio.components.base import NetworkNode
from arc_flash_studio.components.enums import EquipmentType


class CableJunction(NetworkNode):
    """
    Cable junction or splice box.
    
    A cable junction is a small enclosure where cables
    are joined, spliced, or terminated. Due to the confined
    space, conductor gaps are typically smaller than other
    equipment types.
    
    Default Arc Flash Parameters (per IEEE 1584-2018):
        - Gap: 13 mm
        - Working distance: 455 mm (18 inches)
        - Enclosure: 305 x 305 x 203 mm (12" x 12" x 8")
        - Configuration: VCB
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        voltage_kv: Nominal voltage in kilovolts
        gap_mm: Optional explicit gap (overrides default)
        working_distance_mm: Optional explicit working distance
        enclosure: Optional explicit enclosure info
    
    Example:
        >>> junction = CableJunction(id="JB-1", name="Splice Box", voltage_kv=0.48)
        >>> junction.get_gap_mm()
        13.0
    """
    
    @property
    def equipment_type(self) -> EquipmentType:
        """Return cable junction equipment type."""
        return EquipmentType.CABLE_JUNCTION