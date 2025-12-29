"""
Open Air Component
==================

Open-air equipment (outdoor, unenclosed).

Used for outdoor substations, open bus work, and other
equipment without enclosures. Uses VOA or HOA electrode
configuration instead of box configurations.

References:
    - IEEE 1584-2018, Section 4.2: Electrode configurations

Traceability:
    - REQ-COMP-FUNC-6: Open air component with VOA/HOA configuration
"""

from arc_flash_studio.components.base import NetworkNode
from arc_flash_studio.components.enums import EquipmentType, ElectrodeConfig
from arc_flash_studio.components.enclosure import EnclosureInfo


class OpenAir(NetworkNode):
    """
    Open-air equipment (no enclosure).
    
    Open-air equipment includes outdoor substations, open bus
    structures, and other unenclosed electrical equipment.
    Arc flash behavior differs from enclosed equipment because
    the arc can expand freely in all directions.
    
    Default Arc Flash Parameters:
        - LV (≤1 kV): 32 mm gap
        - MV (>1 kV): 104 mm gap
        - Working distance: 455 mm (18 inches)
        - Configuration: VOA (vertical conductors in open air)
    
    Note:
        The enclosure field is set to None for open-air equipment.
        The get_enclosure() method returns a special "open" enclosure
        with VOA configuration for calculation purposes.
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        voltage_kv: Nominal voltage in kilovolts
        gap_mm: Optional explicit gap (overrides default)
        working_distance_mm: Optional explicit working distance
    
    Example:
        >>> outdoor = OpenAir(id="OA-1", name="Outdoor Bus", voltage_kv=13.8)
        >>> outdoor.get_enclosure().electrode_config
        <ElectrodeConfig.VOA: 'VOA'>
    """
    
    # Override enclosure to always be None for open air
    enclosure: None = None
    
    @property
    def equipment_type(self) -> EquipmentType:
        """Return open air equipment type."""
        return EquipmentType.OPEN_AIR
    
    def get_enclosure(self) -> EnclosureInfo:
        """
        Get enclosure info for open-air equipment.
        
        Returns a special EnclosureInfo with very large dimensions
        (effectively open) and VOA electrode configuration.
        
        Returns:
            EnclosureInfo with VOA configuration
        """
        # For open air, use large dimensions to minimize
        # enclosure correction factor, and VOA configuration
        return EnclosureInfo(
            height_mm=9999.0,
            width_mm=9999.0,
            depth_mm=9999.0,
            electrode_config=ElectrodeConfig.VOA
        )