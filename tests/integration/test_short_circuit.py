"""
Integration Tests for Short-Circuit Calculations
=================================================

These tests verify that complete networks produce correct
short-circuit results using PandaPower (IEC 60909).

Test Networks:
    1. Utility only - simplest case
    2. Utility + Transformer - voltage transformation
    3. Utility + Transformer + Cable - full radial system

Traceability:
    - REQ-COMP-FUNC-12: Short-circuit calculation at any bus
"""

import pytest
import math
from arc_flash_studio import (
    Network,
    Switchgear, Panelboard, MCC, Bus,
    UtilitySource, Transformer, Cable, create_cable,
)


class TestUtilityOnlyNetwork:
    """
    Test Network: Utility → Bus → FAULT
    
    Simplest case - fault directly at utility connection.
    """
    
    @pytest.fixture
    def network(self):
        """Create utility-only network."""
        net = Network(name="Utility Only")
        net.add_bus(Switchgear(id="MAIN", name="Main Switchgear", voltage_kv=13.8))
        net.add_utility(UtilitySource(
            id="UTIL", name="Grid",
            bus_id="MAIN",
            short_circuit_mva=500,
            x_r_ratio=15
        ))
        return net
    
    def test_fault_current_at_utility(self, network):
        """
        Fault current at utility bus.
        
        Expected: I = S / (√3 × V) = 500 / (√3 × 13.8) = 20.9 kA
        Note: IEC 60909 may adjust this slightly with voltage factor.
        """
        results = network.calculate_short_circuit()
        ikss = results["MAIN"].ikss_ka
        
        # Approximate check - PandaPower uses IEC 60909
        assert 18 < ikss < 25, f"Unexpected fault current: {ikss} kA"
    
    def test_result_has_mv_gap(self, network):
        """MV switchgear should have 104mm gap."""
        results = network.calculate_short_circuit()
        assert results["MAIN"].gap_mm == 104.0
    
    def test_result_voltage_correct(self, network):
        """Result has correct voltage."""
        results = network.calculate_short_circuit()
        assert results["MAIN"].voltage_kv == 13.8


class TestUtilityTransformerNetwork:
    """
    Test Network: Utility → Transformer → LV Bus → FAULT
    
    Tests voltage transformation and impedance addition.
    """
    
    @pytest.fixture
    def network(self):
        """Create utility + transformer network."""
        net = Network(name="With Transformer")
        
        # MV switchgear
        net.add_bus(Switchgear(id="HV-SWGR", name="13.8kV Switchgear", voltage_kv=13.8))
        
        # LV switchgear
        net.add_bus(Switchgear(id="LV-SWGR", name="480V Switchgear", voltage_kv=0.48))
        
        # Utility
        net.add_utility(UtilitySource(
            id="UTIL", name="Grid",
            bus_id="HV-SWGR",
            short_circuit_mva=500,
            x_r_ratio=15
        ))
        
        # Transformer
        net.add_transformer(Transformer(
            id="TX-1", name="Main Transformer",
            hv_bus_id="HV-SWGR",
            lv_bus_id="LV-SWGR",
            rated_mva=2.0,
            hv_kv=13.8,
            lv_kv=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0
        ))
        
        return net
    
    def test_hv_fault_current(self, network):
        """Fault at HV bus unaffected by transformer."""
        results = network.calculate_short_circuit(bus_ids=["HV-SWGR"])
        ikss = results["HV-SWGR"].ikss_ka
        
        # Should be similar to utility-only case
        assert 18 < ikss < 25
    
    def test_lv_fault_current_higher_than_hv(self, network):
        """
        LV fault current (A) is higher due to voltage transformation.
        
        But short-circuit MVA is lower due to transformer impedance.
        """
        results = network.calculate_short_circuit()
        
        # LV current in kA should be much higher than HV
        # (because I = S / (√3 × V) and V is lower)
        assert results["LV-SWGR"].ikss_ka > results["HV-SWGR"].ikss_ka
    
    def test_lv_fault_limited_by_transformer(self, network):
        """LV fault current limited by transformer impedance."""
        results = network.calculate_short_circuit()
        ikss_lv = results["LV-SWGR"].ikss_ka
        
        # With 5.75% impedance on 2 MVA transformer at 480V,
        # max fault is roughly 2.0 / 0.0575 / (√3 × 0.48) × 1000 ≈ 41 kA
        # (this is approximate - IEC 60909 adjusts)
        assert 35 < ikss_lv < 50
    
    def test_equipment_types_preserved(self, network):
        """Equipment types flow through to results."""
        results = network.calculate_short_circuit()
        
        from arc_flash_studio import EquipmentType
        assert results["HV-SWGR"].equipment_type == EquipmentType.SWITCHGEAR
        assert results["LV-SWGR"].equipment_type == EquipmentType.SWITCHGEAR


class TestFullRadialNetwork:
    """
    Test Network: Utility → Transformer → Cable → MCC → FAULT
    
    Full radial system with cumulative impedance.
    """
    
    @pytest.fixture
    def network(self):
        """Create full radial network."""
        net = Network(name="Full Radial")
        
        # Buses
        net.add_bus(Switchgear(id="HV", name="13.8kV Bus", voltage_kv=13.8))
        net.add_bus(Switchgear(id="LV-MAIN", name="480V Main", voltage_kv=0.48))
        net.add_bus(MCC(id="MCC-1", name="MCC 1", voltage_kv=0.48))
        
        # Utility
        net.add_utility(UtilitySource(
            id="UTIL", name="Grid", bus_id="HV",
            short_circuit_mva=500, x_r_ratio=15
        ))
        
        # Transformer
        net.add_transformer(Transformer(
            id="TX-1", name="Main",
            hv_bus_id="HV", lv_bus_id="LV-MAIN",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        ))
        
        # Cable using NEC Table 9 data
        net.add_cable(create_cable(
            id="CBL-1", name="Feeder to MCC",
            from_bus_id="LV-MAIN", to_bus_id="MCC-1",
            length_m=30.0,
            conductor_size="500 kcmil"
        ))
        
        return net
    
    def test_fault_current_decreases_along_feeder(self, network):
        """Fault current decreases as we move away from source."""
        results = network.calculate_short_circuit()
        
        # Current decreases: HV (lowest due to voltage) 
        # LV-MAIN (higher current, but lower MVA than HV)
        # MCC-1 (lowest MVA due to cable impedance)
        
        # Compare short-circuit MVA (more meaningful comparison)
        skss_lv = results["LV-MAIN"].ikss_ka * 0.48 * math.sqrt(3)
        skss_mcc = results["MCC-1"].ikss_ka * 0.48 * math.sqrt(3)
        
        assert skss_mcc < skss_lv, "Cable should reduce fault MVA"
    
    def test_mcc_gap_different_from_switchgear(self, network):
        """MCC has different default gap than switchgear."""
        results = network.calculate_short_circuit()
        
        assert results["LV-MAIN"].gap_mm == 32.0  # LV switchgear
        assert results["MCC-1"].gap_mm == 25.0   # MCC


class TestMultipleBranchNetwork:
    """
    Test Network: Utility → Transformer → Main Bus with multiple feeders.
    
           ┌─ Cable → MCC-1
    Main ──┤
           └─ Cable → Panel
    """
    
    @pytest.fixture
    def network(self):
        """Create multi-branch network."""
        net = Network(name="Multi-Branch")
        
        # Main buses
        net.add_bus(Switchgear(id="HV", name="HV", voltage_kv=13.8))
        net.add_bus(Switchgear(id="MAIN", name="Main", voltage_kv=0.48))
        
        # Branch equipment
        net.add_bus(MCC(id="MCC-1", name="MCC 1", voltage_kv=0.48))
        net.add_bus(Panelboard(id="PNL-1", name="Panel 1", voltage_kv=0.48))
        
        # Source
        net.add_utility(UtilitySource(
            id="UTIL", name="Grid", bus_id="HV",
            short_circuit_mva=500, x_r_ratio=15
        ))
        
        # Transformer
        net.add_transformer(Transformer(
            id="TX", name="Main",
            hv_bus_id="HV", lv_bus_id="MAIN",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        ))
        
        # Cables to branches
        net.add_cable(Cable(
            id="CBL-MCC", name="To MCC",
            from_bus_id="MAIN", to_bus_id="MCC-1",
            length_m=30.0, r_ohm_per_km=0.105, x_ohm_per_km=0.128
        ))
        
        net.add_cable(Cable(
            id="CBL-PNL", name="To Panel",
            from_bus_id="MAIN", to_bus_id="PNL-1",
            length_m=50.0, r_ohm_per_km=0.220, x_ohm_per_km=0.135  # 4/0 AWG
        ))
        
        return net
    
    def test_all_buses_have_results(self, network):
        """All buses have short-circuit results."""
        results = network.calculate_short_circuit()
        
        assert "HV" in results
        assert "MAIN" in results
        assert "MCC-1" in results
        assert "PNL-1" in results
    
    def test_longer_cable_lower_fault(self, network):
        """Longer/smaller cable has lower fault current."""
        results = network.calculate_short_circuit()
        
        # Panel has longer cable with higher impedance
        assert results["PNL-1"].ikss_ka < results["MCC-1"].ikss_ka
    
    def test_equipment_types_preserved(self, network):
        """Different equipment types preserved in results."""
        results = network.calculate_short_circuit()
        
        from arc_flash_studio import EquipmentType
        assert results["MCC-1"].equipment_type == EquipmentType.MCC
        assert results["PNL-1"].equipment_type == EquipmentType.PANELBOARD