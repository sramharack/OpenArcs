"""
Unit Tests for Network
======================

Tests for the Network class (PandaPower wrapper).

Traceability:
    - REQ-COMP-FUNC-10: Network topology support
    - REQ-COMP-FUNC-12: Short-circuit calculation via PandaPower
"""

import pytest
import math
from arc_flash_studio import (
    Network, ShortCircuitResult,
    Bus, Switchgear, Panelboard, MCC,
    UtilitySource, Transformer, Cable,
    EquipmentType, ElectrodeConfig,
)


class TestNetworkCreation:
    """Tests for creating Network instances."""
    
    def test_create_empty_network(self):
        """Create an empty network."""
        net = Network(name="Test")
        assert net.name == "Test"
        assert len(net.list_buses()) == 0
    
    def test_default_frequency(self):
        """Default frequency is 60 Hz."""
        net = Network()
        assert net.frequency_hz == 60.0
    
    def test_custom_frequency(self):
        """Can specify custom frequency."""
        net = Network(frequency_hz=50.0)
        assert net.frequency_hz == 50.0


class TestNetworkAddComponents:
    """Tests for adding components to network."""
    
    def test_add_bus(self):
        """Add a bus to the network."""
        net = Network()
        bus = Bus(id="B1", name="Test", voltage_kv=0.48)
        net.add_bus(bus)
        assert "B1" in net.list_buses()
    
    def test_add_switchgear(self):
        """Add switchgear (uses add_bus internally)."""
        net = Network()
        swgr = Switchgear(id="S1", name="Main", voltage_kv=0.48)
        net.add_bus(swgr)
        assert "S1" in net.list_buses()
    
    def test_add_duplicate_bus_raises_error(self):
        """Adding duplicate bus ID raises error."""
        net = Network()
        net.add_bus(Bus(id="B1", name="First", voltage_kv=0.48))
        with pytest.raises(ValueError, match="already exists"):
            net.add_bus(Bus(id="B1", name="Second", voltage_kv=0.48))
    
    def test_add_utility(self):
        """Add utility source to network."""
        net = Network()
        net.add_bus(Bus(id="B1", name="Main", voltage_kv=13.8))
        net.add_utility(UtilitySource(
            id="U1", name="Grid", bus_id="B1",
            short_circuit_mva=500, x_r_ratio=15
        ))
        # If no error, utility was added
    
    def test_add_utility_nonexistent_bus_raises_error(self):
        """Adding utility to nonexistent bus raises error."""
        net = Network()
        with pytest.raises(ValueError, match="not found"):
            net.add_utility(UtilitySource(
                id="U1", name="Grid", bus_id="B1",
                short_circuit_mva=500, x_r_ratio=15
            ))
    
    def test_add_transformer(self):
        """Add transformer to network."""
        net = Network()
        net.add_bus(Bus(id="HV", name="HV Bus", voltage_kv=13.8))
        net.add_bus(Bus(id="LV", name="LV Bus", voltage_kv=0.48))
        net.add_transformer(Transformer(
            id="TX1", name="Main",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        ))
    
    def test_add_transformer_nonexistent_bus_raises_error(self):
        """Adding transformer with nonexistent bus raises error."""
        net = Network()
        net.add_bus(Bus(id="HV", name="HV", voltage_kv=13.8))
        with pytest.raises(ValueError, match="not found"):
            net.add_transformer(Transformer(
                id="TX1", name="Main",
                hv_bus_id="HV", lv_bus_id="LV",  # LV doesn't exist
                rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
                impedance_percent=5.75, x_r_ratio=8.0
            ))
    
    def test_add_cable(self):
        """Add cable to network."""
        net = Network()
        net.add_bus(Bus(id="B1", name="From", voltage_kv=0.48))
        net.add_bus(Bus(id="B2", name="To", voltage_kv=0.48))
        net.add_cable(Cable(
            id="C1", name="Feeder",
            from_bus_id="B1", to_bus_id="B2",
            length_m=30.0, r_ohm_per_km=0.1, x_ohm_per_km=0.1
        ))
    
    def test_add_cable_nonexistent_bus_raises_error(self):
        """Adding cable with nonexistent bus raises error."""
        net = Network()
        net.add_bus(Bus(id="B1", name="From", voltage_kv=0.48))
        with pytest.raises(ValueError, match="not found"):
            net.add_cable(Cable(
                id="C1", name="Feeder",
                from_bus_id="B1", to_bus_id="B2",  # B2 doesn't exist
                length_m=30.0, r_ohm_per_km=0.1, x_ohm_per_km=0.1
            ))


class TestNetworkGetBus:
    """Tests for retrieving buses."""
    
    def test_get_bus(self):
        """Retrieve bus by ID."""
        net = Network()
        swgr = Switchgear(id="S1", name="Main", voltage_kv=0.48)
        net.add_bus(swgr)
        
        retrieved = net.get_bus("S1")
        assert retrieved.id == "S1"
        assert retrieved.name == "Main"
    
    def test_get_nonexistent_bus_raises_error(self):
        """Getting nonexistent bus raises KeyError."""
        net = Network()
        with pytest.raises(KeyError):
            net.get_bus("INVALID")


class TestNetworkRepr:
    """Tests for network string representation."""
    
    def test_repr_contains_name(self):
        """Repr contains network name."""
        net = Network(name="My Plant")
        assert "My Plant" in repr(net)
    
    def test_repr_contains_counts(self):
        """Repr contains component counts."""
        net = Network()
        net.add_bus(Bus(id="B1", name="Test", voltage_kv=0.48))
        r = repr(net)
        assert "buses=1" in r


class TestShortCircuitCalculation:
    """Tests for short-circuit calculations."""
    
    @pytest.fixture
    def simple_network(self):
        """Simple network with utility source."""
        net = Network()
        net.add_bus(Switchgear(id="SWGR", name="Main", voltage_kv=0.48))
        net.add_utility(UtilitySource(
            id="U1", name="Grid", bus_id="SWGR",
            short_circuit_mva=500, x_r_ratio=15
        ))
        return net
    
    def test_calculate_returns_results(self, simple_network):
        """Calculation returns results dictionary."""
        results = simple_network.calculate_short_circuit()
        assert isinstance(results, dict)
        assert "SWGR" in results
    
    def test_result_is_shortcircuitresult(self, simple_network):
        """Result is ShortCircuitResult dataclass."""
        results = simple_network.calculate_short_circuit()
        assert isinstance(results["SWGR"], ShortCircuitResult)
    
    def test_result_has_expected_fields(self, simple_network):
        """Result contains all expected fields."""
        results = simple_network.calculate_short_circuit()
        result = results["SWGR"]
        
        assert result.bus_id == "SWGR"
        assert result.bus_name == "Main"
        assert result.voltage_kv == 0.48
        assert result.ikss_ka > 0
        assert result.equipment_type == EquipmentType.SWITCHGEAR
        assert result.gap_mm == 32.0  # LV switchgear default
        assert result.working_distance_mm == 610.0  # Switchgear default
    
    def test_calculate_specific_buses(self, simple_network):
        """Can calculate for specific bus only."""
        results = simple_network.calculate_short_circuit(bus_ids=["SWGR"])
        assert len(results) == 1
    
    def test_calculate_invalid_bus_raises_error(self, simple_network):
        """Calculating for invalid bus raises error."""
        with pytest.raises(ValueError, match="not found"):
            simple_network.calculate_short_circuit(bus_ids=["INVALID"])
    
    def test_fault_current_positive(self, simple_network):
        """Fault current is positive."""
        results = simple_network.calculate_short_circuit()
        assert results["SWGR"].ikss_ka > 0


class TestShortCircuitEquipmentDefaults:
    """Tests that equipment defaults flow through to results."""
    
    def test_switchgear_defaults_in_result(self):
        """Switchgear defaults appear in result."""
        net = Network()
        net.add_bus(Switchgear(id="S1", name="SWGR", voltage_kv=0.48))
        net.add_utility(UtilitySource(
            id="U1", name="Grid", bus_id="S1",
            short_circuit_mva=500, x_r_ratio=15
        ))
        
        results = net.calculate_short_circuit()
        assert results["S1"].equipment_type == EquipmentType.SWITCHGEAR
        assert results["S1"].gap_mm == 32.0
        assert results["S1"].working_distance_mm == 610.0
    
    def test_mcc_defaults_in_result(self):
        """MCC defaults appear in result."""
        net = Network()
        net.add_bus(MCC(id="M1", name="MCC", voltage_kv=0.48))
        net.add_utility(UtilitySource(
            id="U1", name="Grid", bus_id="M1",
            short_circuit_mva=500, x_r_ratio=15
        ))
        
        results = net.calculate_short_circuit()
        assert results["M1"].equipment_type == EquipmentType.MCC
        assert results["M1"].gap_mm == 25.0
        assert results["M1"].working_distance_mm == 455.0
    
    def test_panelboard_defaults_in_result(self):
        """Panelboard defaults appear in result."""
        net = Network()
        net.add_bus(Panelboard(id="P1", name="Panel", voltage_kv=0.208))
        net.add_utility(UtilitySource(
            id="U1", name="Grid", bus_id="P1",
            short_circuit_mva=100, x_r_ratio=10
        ))
        
        results = net.calculate_short_circuit()
        assert results["P1"].equipment_type == EquipmentType.PANELBOARD
        assert results["P1"].gap_mm == 25.0
    
    def test_custom_gap_preserved(self):
        """Custom gap overrides default in result."""
        net = Network()
        net.add_bus(Switchgear(id="S1", name="SWGR", voltage_kv=0.48, gap_mm=40.0))
        net.add_utility(UtilitySource(
            id="U1", name="Grid", bus_id="S1",
            short_circuit_mva=500, x_r_ratio=15
        ))
        
        results = net.calculate_short_circuit()
        assert results["S1"].gap_mm == 40.0


class TestPandaPowerAccess:
    """Tests for accessing underlying PandaPower network."""
    
    def test_pp_network_accessible(self):
        """Can access PandaPower network."""
        net = Network()
        net.add_bus(Bus(id="B1", name="Test", voltage_kv=0.48))
        
        pp_net = net.pp_network
        assert pp_net is not None
        assert len(pp_net.bus) == 1
    
    def test_pp_network_rebuilt_on_change(self):
        """PP network rebuilds when components added."""
        net = Network()
        net.add_bus(Bus(id="B1", name="First", voltage_kv=0.48))
        
        pp_net1 = net.pp_network
        assert len(pp_net1.bus) == 1
        
        net.add_bus(Bus(id="B2", name="Second", voltage_kv=0.48))
        pp_net2 = net.pp_network
        assert len(pp_net2.bus) == 2