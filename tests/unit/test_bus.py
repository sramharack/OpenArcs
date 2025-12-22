"""
Unit Tests for Bus Component
============================

Test Philosophy:
    The Bus component is a network node representing a point at a
    specific voltage level. It has no impedance - it's purely a
    connection point.

Traceability:
    - REQ-COMP-FUNC-1: Bus class properties
    - IEEE 1584-2018, Section 6.2: Voltage classification
"""

import pytest
from arc_flash_studio.components.bus import Bus, VoltageLevel


class TestBusCreation:
    """Test basic bus creation and properties."""

    def test_create_lv_bus(self):
        """Create a low-voltage (480V) bus."""
        bus = Bus(
            id="BUS-001",
            name="Main 480V Bus",
            voltage_nominal=0.48,
        )
        
        assert bus.id == "BUS-001"
        assert bus.name == "Main 480V Bus"
        assert bus.voltage_nominal == 0.48
    
    def test_create_mv_bus(self):
        """Create a medium-voltage (13.8kV) bus."""
        bus = Bus(
            id="BUS-002",
            name="13.8kV Switchgear",
            voltage_nominal=13.8,
        )
        
        assert bus.id == "BUS-002"
        assert bus.voltage_nominal == 13.8
    
    def test_default_voltage_base(self):
        """Voltage base defaults to nominal if not specified."""
        bus = Bus(
            id="BUS-001",
            name="Test",
            voltage_nominal=0.48,
        )
        
        assert bus.voltage_base is None
        assert bus.voltage_base_kv == 0.48  # Computed field uses nominal
    
    def test_explicit_voltage_base(self):
        """Voltage base can be set explicitly."""
        bus = Bus(
            id="BUS-001",
            name="Test",
            voltage_nominal=0.48,
            voltage_base=0.50,  # Different from nominal
        )
        
        assert bus.voltage_base == 0.50
        assert bus.voltage_base_kv == 0.50


class TestBusVoltageLevel:
    """Test voltage level classification per IEEE 1584-2018."""

    def test_lv_classification_208v(self):
        """208V is low voltage."""
        bus = Bus(id="B1", name="Test", voltage_nominal=0.208)
        assert bus.voltage_level == VoltageLevel.LV
    
    def test_lv_classification_480v(self):
        """480V is low voltage."""
        bus = Bus(id="B1", name="Test", voltage_nominal=0.48)
        assert bus.voltage_level == VoltageLevel.LV
    
    def test_lv_classification_600v(self):
        """600V is low voltage."""
        bus = Bus(id="B1", name="Test", voltage_nominal=0.6)
        assert bus.voltage_level == VoltageLevel.LV
    
    def test_lv_boundary_1000v(self):
        """1000V (1kV) is the LV/MV boundary - should be LV."""
        bus = Bus(id="B1", name="Test", voltage_nominal=1.0)
        assert bus.voltage_level == VoltageLevel.LV
    
    def test_mv_classification_4160v(self):
        """4.16kV is medium voltage."""
        bus = Bus(id="B1", name="Test", voltage_nominal=4.16)
        assert bus.voltage_level == VoltageLevel.MV
    
    def test_mv_classification_13800v(self):
        """13.8kV is medium voltage."""
        bus = Bus(id="B1", name="Test", voltage_nominal=13.8)
        assert bus.voltage_level == VoltageLevel.MV
    
    def test_mv_classification_34500v(self):
        """34.5kV is medium voltage."""
        bus = Bus(id="B1", name="Test", voltage_nominal=34.5)
        assert bus.voltage_level == VoltageLevel.MV
    
    def test_hv_classification_69kv(self):
        """69kV is high voltage (above 35kV)."""
        bus = Bus(id="B1", name="Test", voltage_nominal=69.0)
        assert bus.voltage_level == VoltageLevel.HV
    
    def test_hv_classification_138kv(self):
        """138kV is high voltage."""
        bus = Bus(id="B1", name="Test", voltage_nominal=138.0)
        assert bus.voltage_level == VoltageLevel.HV


class TestBusIEEE1584Scope:
    """Test IEEE 1584-2018 scope checking (0.208 to 15 kV)."""

    def test_in_scope_208v(self):
        """208V is within IEEE 1584 scope."""
        bus = Bus(id="B1", name="Test", voltage_nominal=0.208)
        assert bus.in_ieee1584_scope is True
    
    def test_in_scope_480v(self):
        """480V is within IEEE 1584 scope."""
        bus = Bus(id="B1", name="Test", voltage_nominal=0.48)
        assert bus.in_ieee1584_scope is True
    
    def test_in_scope_13800v(self):
        """13.8kV is within IEEE 1584 scope."""
        bus = Bus(id="B1", name="Test", voltage_nominal=13.8)
        assert bus.in_ieee1584_scope is True
    
    def test_in_scope_15kv(self):
        """15kV is within IEEE 1584 scope (upper boundary)."""
        bus = Bus(id="B1", name="Test", voltage_nominal=15.0)
        assert bus.in_ieee1584_scope is True
    
    def test_out_of_scope_below(self):
        """120V is below IEEE 1584 scope."""
        bus = Bus(id="B1", name="Test", voltage_nominal=0.120)
        assert bus.in_ieee1584_scope is False
    
    def test_out_of_scope_above(self):
        """34.5kV is above IEEE 1584 scope."""
        bus = Bus(id="B1", name="Test", voltage_nominal=34.5)
        assert bus.in_ieee1584_scope is False


class TestBusValidation:
    """Test input validation for Bus."""

    def test_negative_voltage_raises_error(self):
        """Voltage must be positive."""
        with pytest.raises(ValueError):
            Bus(id="B1", name="Test", voltage_nominal=-0.48)
    
    def test_zero_voltage_raises_error(self):
        """Voltage cannot be zero."""
        with pytest.raises(ValueError):
            Bus(id="B1", name="Test", voltage_nominal=0.0)
    
    def test_empty_id_raises_error(self):
        """ID cannot be empty."""
        with pytest.raises(ValueError):
            Bus(id="", name="Test", voltage_nominal=0.48)
    
    def test_whitespace_id_stripped(self):
        """Whitespace in ID should be stripped."""
        bus = Bus(id="  BUS-001  ", name="Test", voltage_nominal=0.48)
        assert bus.id == "BUS-001"


class TestBusStrRepresentation:
    """Test string representation."""

    def test_str_contains_id(self):
        """String representation contains ID."""
        bus = Bus(id="BUS-001", name="Test Bus", voltage_nominal=0.48)
        assert "BUS-001" in str(bus)
    
    def test_str_contains_voltage(self):
        """String representation contains voltage."""
        bus = Bus(id="BUS-001", name="Test Bus", voltage_nominal=0.48)
        assert "0.48" in str(bus)


class TestBusJSONSerialization:
    """Test Pydantic JSON serialization."""

    def test_export_to_json(self):
        """Bus can be exported to JSON."""
        bus = Bus(id="BUS-001", name="Test", voltage_nominal=0.48)
        json_str = bus.model_dump_json()
        
        assert "BUS-001" in json_str
        assert "0.48" in json_str
    
    def test_import_from_json(self):
        """Bus can be created from JSON."""
        json_str = '{"id": "BUS-002", "name": "From JSON", "voltage_nominal": 13.8}'
        bus = Bus.model_validate_json(json_str)
        
        assert bus.id == "BUS-002"
        assert bus.voltage_nominal == 13.8
    
    def test_computed_fields_in_json(self):
        """Computed fields are included in JSON output."""
        bus = Bus(id="BUS-001", name="Test", voltage_nominal=0.48)
        data = bus.model_dump()
        
        assert "voltage_level" in data
        assert "in_ieee1584_scope" in data
        assert "voltage_base_kv" in data