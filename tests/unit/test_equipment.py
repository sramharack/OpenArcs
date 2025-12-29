"""
Unit Tests for Equipment Types
==============================

Tests for Bus, Switchgear, Panelboard, MCC, CableJunction, and OpenAir.

All equipment types inherit from NetworkNode and map to PandaPower buses.
Each type provides equipment-specific default arc flash parameters.

Traceability:
    - REQ-COMP-FUNC-1 through REQ-COMP-FUNC-6: Equipment components
"""

import pytest
from arc_flash_studio.components import (
    Bus, Switchgear, Panelboard, MCC, CableJunction, OpenAir,
    VoltageLevel, ElectrodeConfig, EquipmentType, EnclosureInfo,
)


class TestBus:
    """Tests for generic Bus component."""
    
    def test_create_bus(self):
        """Create a valid bus."""
        bus = Bus(id="B1", name="Test Bus", voltage_kv=0.48)
        assert bus.id == "B1"
        assert bus.name == "Test Bus"
        assert bus.voltage_kv == 0.48
    
    def test_bus_equipment_type(self):
        """Bus returns OTHER equipment type."""
        bus = Bus(id="B1", name="Test", voltage_kv=0.48)
        assert bus.equipment_type == EquipmentType.OTHER
    
    def test_bus_voltage_level_lv(self):
        """480V bus is LV."""
        bus = Bus(id="B1", name="Test", voltage_kv=0.48)
        assert bus.voltage_level == VoltageLevel.LV
    
    def test_bus_voltage_level_mv(self):
        """13.8kV bus is MV."""
        bus = Bus(id="B1", name="Test", voltage_kv=13.8)
        assert bus.voltage_level == VoltageLevel.MV
    
    def test_bus_voltage_level_hv(self):
        """69kV bus is HV."""
        bus = Bus(id="B1", name="Test", voltage_kv=69.0)
        assert bus.voltage_level == VoltageLevel.HV
    
    def test_bus_ieee1584_scope_in(self):
        """4.16kV is within IEEE 1584 scope."""
        bus = Bus(id="B1", name="Test", voltage_kv=4.16)
        assert bus.in_ieee1584_scope is True
    
    def test_bus_ieee1584_scope_below(self):
        """120V is below IEEE 1584 scope."""
        bus = Bus(id="B1", name="Test", voltage_kv=0.120)
        assert bus.in_ieee1584_scope is False
    
    def test_bus_ieee1584_scope_above(self):
        """34.5kV is above IEEE 1584 scope."""
        bus = Bus(id="B1", name="Test", voltage_kv=34.5)
        assert bus.in_ieee1584_scope is False


class TestSwitchgear:
    """Tests for Switchgear component."""
    
    def test_create_switchgear(self):
        """Create a valid switchgear."""
        swgr = Switchgear(id="SWGR-1", name="Main", voltage_kv=0.48)
        assert swgr.id == "SWGR-1"
        assert swgr.voltage_kv == 0.48
    
    def test_switchgear_equipment_type(self):
        """Switchgear returns SWITCHGEAR equipment type."""
        swgr = Switchgear(id="S1", name="Test", voltage_kv=0.48)
        assert swgr.equipment_type == EquipmentType.SWITCHGEAR
    
    def test_switchgear_lv_gap(self):
        """LV switchgear default gap is 32mm."""
        swgr = Switchgear(id="S1", name="Test", voltage_kv=0.48)
        assert swgr.get_gap_mm() == 32.0
    
    def test_switchgear_mv_gap(self):
        """MV switchgear default gap is 104mm."""
        swgr = Switchgear(id="S1", name="Test", voltage_kv=4.16)
        assert swgr.get_gap_mm() == 104.0
    
    def test_switchgear_working_distance(self):
        """Switchgear default working distance is 610mm."""
        swgr = Switchgear(id="S1", name="Test", voltage_kv=0.48)
        assert swgr.get_working_distance_mm() == 610.0
    
    def test_switchgear_custom_gap(self):
        """Custom gap overrides default."""
        swgr = Switchgear(id="S1", name="Test", voltage_kv=0.48, gap_mm=40.0)
        assert swgr.get_gap_mm() == 40.0


class TestPanelboard:
    """Tests for Panelboard component."""
    
    def test_create_panelboard(self):
        """Create a valid panelboard."""
        panel = Panelboard(id="LP-1", name="Lighting", voltage_kv=0.208)
        assert panel.id == "LP-1"
    
    def test_panelboard_equipment_type(self):
        """Panelboard returns PANELBOARD equipment type."""
        panel = Panelboard(id="P1", name="Test", voltage_kv=0.208)
        assert panel.equipment_type == EquipmentType.PANELBOARD
    
    def test_panelboard_gap(self):
        """Panelboard default gap is 25mm."""
        panel = Panelboard(id="P1", name="Test", voltage_kv=0.208)
        assert panel.get_gap_mm() == 25.0
    
    def test_panelboard_working_distance(self):
        """Panelboard default working distance is 455mm."""
        panel = Panelboard(id="P1", name="Test", voltage_kv=0.208)
        assert panel.get_working_distance_mm() == 455.0


class TestMCC:
    """Tests for Motor Control Center component."""
    
    def test_create_mcc(self):
        """Create a valid MCC."""
        mcc = MCC(id="MCC-1", name="Building A", voltage_kv=0.48)
        assert mcc.id == "MCC-1"
    
    def test_mcc_equipment_type(self):
        """MCC returns MCC equipment type."""
        mcc = MCC(id="M1", name="Test", voltage_kv=0.48)
        assert mcc.equipment_type == EquipmentType.MCC
    
    def test_mcc_gap(self):
        """MCC default gap is 25mm."""
        mcc = MCC(id="M1", name="Test", voltage_kv=0.48)
        assert mcc.get_gap_mm() == 25.0
    
    def test_mcc_working_distance(self):
        """MCC default working distance is 455mm."""
        mcc = MCC(id="M1", name="Test", voltage_kv=0.48)
        assert mcc.get_working_distance_mm() == 455.0


class TestCableJunction:
    """Tests for CableJunction component."""
    
    def test_create_cable_junction(self):
        """Create a valid cable junction."""
        jb = CableJunction(id="JB-1", name="Splice", voltage_kv=0.48)
        assert jb.id == "JB-1"
    
    def test_cable_junction_equipment_type(self):
        """CableJunction returns CABLE_JUNCTION equipment type."""
        jb = CableJunction(id="J1", name="Test", voltage_kv=0.48)
        assert jb.equipment_type == EquipmentType.CABLE_JUNCTION
    
    def test_cable_junction_gap(self):
        """CableJunction default gap is 13mm."""
        jb = CableJunction(id="J1", name="Test", voltage_kv=0.48)
        assert jb.get_gap_mm() == 13.0


class TestOpenAir:
    """Tests for OpenAir component."""
    
    def test_create_open_air(self):
        """Create a valid open air equipment."""
        oa = OpenAir(id="OA-1", name="Outdoor Bus", voltage_kv=13.8)
        assert oa.id == "OA-1"
    
    def test_open_air_equipment_type(self):
        """OpenAir returns OPEN_AIR equipment type."""
        oa = OpenAir(id="O1", name="Test", voltage_kv=13.8)
        assert oa.equipment_type == EquipmentType.OPEN_AIR
    
    def test_open_air_enclosure_is_none(self):
        """OpenAir enclosure attribute is None."""
        oa = OpenAir(id="O1", name="Test", voltage_kv=13.8)
        assert oa.enclosure is None
    
    def test_open_air_get_enclosure_returns_voa(self):
        """OpenAir get_enclosure returns VOA configuration."""
        oa = OpenAir(id="O1", name="Test", voltage_kv=13.8)
        enc = oa.get_enclosure()
        assert enc.electrode_config == ElectrodeConfig.VOA
    
    def test_open_air_enclosure_large_dimensions(self):
        """OpenAir enclosure has very large dimensions."""
        oa = OpenAir(id="O1", name="Test", voltage_kv=13.8)
        enc = oa.get_enclosure()
        assert enc.height_mm >= 9999
        assert enc.width_mm >= 9999


class TestNetworkNodeValidation:
    """Tests for validation inherited from NetworkNode."""
    
    def test_empty_id_raises_error(self):
        """Empty ID raises validation error."""
        with pytest.raises(ValueError):
            Bus(id="", name="Test", voltage_kv=0.48)
    
    def test_negative_voltage_raises_error(self):
        """Negative voltage raises validation error."""
        with pytest.raises(ValueError):
            Bus(id="B1", name="Test", voltage_kv=-0.48)
    
    def test_zero_voltage_raises_error(self):
        """Zero voltage raises validation error."""
        with pytest.raises(ValueError):
            Switchgear(id="S1", name="Test", voltage_kv=0)
    
    def test_negative_gap_raises_error(self):
        """Negative gap raises validation error."""
        with pytest.raises(ValueError):
            Bus(id="B1", name="Test", voltage_kv=0.48, gap_mm=-10)
    
    def test_negative_working_distance_raises_error(self):
        """Negative working distance raises validation error."""
        with pytest.raises(ValueError):
            Bus(id="B1", name="Test", voltage_kv=0.48, working_distance_mm=-100)


class TestNetworkNodeEnclosure:
    """Tests for enclosure handling in NetworkNode."""
    
    def test_custom_enclosure(self):
        """Custom enclosure is preserved."""
        custom = EnclosureInfo(
            height_mm=600, width_mm=700, depth_mm=800,
            electrode_config=ElectrodeConfig.HCB
        )
        bus = Bus(id="B1", name="Test", voltage_kv=0.48, enclosure=custom)
        assert bus.get_enclosure().height_mm == 600
        assert bus.get_enclosure().electrode_config == ElectrodeConfig.HCB
    
    def test_default_enclosure_by_equipment_type(self):
        """Default enclosure varies by equipment type."""
        swgr = Switchgear(id="S1", name="Test", voltage_kv=0.48)
        mcc = MCC(id="M1", name="Test", voltage_kv=0.48)
        
        # Switchgear larger than MCC
        assert swgr.get_enclosure().height_mm > mcc.get_enclosure().height_mm


class TestEquipmentStrRepresentation:
    """Tests for string representation."""
    
    def test_bus_str(self):
        """Bus string contains class name and ID."""
        bus = Bus(id="B1", name="Test", voltage_kv=0.48)
        s = str(bus)
        assert "Bus" in s
        assert "B1" in s
    
    def test_switchgear_str(self):
        """Switchgear string contains class name."""
        swgr = Switchgear(id="S1", name="Test", voltage_kv=0.48)
        s = str(swgr)
        assert "Switchgear" in s