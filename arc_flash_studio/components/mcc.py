"""
Motor Control Center (MCC) Component
====================================

Motor control center - assemblies of motor starters and controls.

MCCs contain multiple motor starter units (buckets) in a
common enclosure. Each bucket may have different arc flash
characteristics based on its configuration.

References:
    - IEEE 1584-2018, Table 8: Typical gaps
    - IEEE 1584-2018, Table 3: Working distances

Traceability:
    - REQ-COMP-FUNC-4: MCC component with equipment-specific defaults
"""

from arc_flash_studio.components.base import NetworkNode
from arc_flash_studio.components.enums import EquipmentType


class MCC(NetworkNode):
    """
    Motor Control Center.
    
    An MCC is an assembly of one or more enclosed sections
    containing motor control units (starters, disconnects,
    overload relays) with a common bus.
    
    Default Arc Flash Parameters (per IEEE 1584-2018):
        - Gap: 25 mm
        - Working distance: 455 mm (18 inches)
        - Enclosure: 660 x 660 x 660 mm (26" cube)
        - Configuration: VCB (or VCBB with barriers)
    
    Note:
        Individual MCC buckets may have different arc flash
        hazards. This component represents the MCC as a whole.
        For detailed bucket-level analysis, create separate
        nodes for each bucket location.
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        voltage_kv: Nominal voltage in kilovolts
        gap_mm: Optional explicit gap (overrides default)
        working_distance_mm: Optional explicit working distance
        enclosure: Optional explicit enclosure info
    
    Example:
        >>> mcc = MCC(id="MCC-1", name="Building A MCC", voltage_kv=0.48)
        >>> mcc.equipment_type
        <EquipmentType.MCC: 'mcc'>
        >>> mcc.get_gap_mm()
        25.0
    """
    
    @property
    def equipment_type(self) -> EquipmentType:
        """Return MCC equipment type."""
        return EquipmentType.MCC