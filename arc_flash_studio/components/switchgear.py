"""
Switchgear Component
====================

Low-voltage or medium-voltage switchgear.

Switchgear is enclosed switching and interrupting equipment.
It typically has larger enclosures and greater working distances
than panels or MCCs.

References:
    - IEEE 1584-2018, Table 8: Typical gaps
    - IEEE 1584-2018, Table 3: Working distances

Traceability:
    - REQ-COMP-FUNC-2: Switchgear component with equipment-specific defaults
"""

from arc_flash_studio.components.base import NetworkNode
from arc_flash_studio.components.enums import EquipmentType


class Switchgear(NetworkNode):
    """
    Low-voltage or medium-voltage switchgear.
    
    Switchgear consists of switching, interrupting, metering,
    and protective devices mounted in a metal enclosure.
    
    Default Arc Flash Parameters (per IEEE 1584-2018):
        - LV (≤1 kV): 32 mm gap
        - MV (>1 kV): 104 mm gap (5 kV class typical)
        - Working distance: 610 mm (24 inches)
        - Enclosure: 914 x 914 x 914 mm (36" cube)
        - Configuration: VCB (vertical conductors in box)
    
    Attributes:
        id: Unique identifier
        name: Human-readable name  
        voltage_kv: Nominal voltage in kilovolts
        gap_mm: Optional explicit gap (overrides default)
        working_distance_mm: Optional explicit working distance
        enclosure: Optional explicit enclosure info
    
    Example:
        >>> swgr = Switchgear(id="SWGR-1", name="Main Switchgear", voltage_kv=13.8)
        >>> swgr.equipment_type
        <EquipmentType.SWITCHGEAR: 'switchgear'>
        >>> swgr.get_gap_mm()  # MV default
        104.0
        >>> swgr.get_working_distance_mm()
        610.0
    """
    
    @property
    def equipment_type(self) -> EquipmentType:
        """Return switchgear equipment type."""
        return EquipmentType.SWITCHGEAR