"""
Integration Tests for RadialNetwork
====================================

Test Philosophy:
    Integration tests verify that components work together correctly
    in realistic configurations. Each test uses a hand-calculated
    reference value to verify the fault current calculation.

Test Patterns:
    1. Simple Radial: Utility → Bus → Fault
    2. With Transformer: Utility → Xfmr → Bus → Fault
    3. With Cable: Utility → Xfmr → Cable → Bus → Fault
    4. Full Industrial: Utility → Xfmr → Cable → Panel → Fault

Reference:
    - IEEE 551 (Violet Book): Short-circuit calculation methods
    - IEC 60909-0: Short-circuit currents in AC systems

Traceability:
    - REQ-COMP-FUNC-12: Short-circuit calculation at any bus
"""

import pytest
import math
from arc_flash_studio import (
    Bus,
    UtilitySource,
    Transformer,
    Cable,
    create_cable_from_size,
    RadialNetwork,
)


class TestNetworkConstruction:
    """Test network construction and validation."""

    def test_create_empty_network(self):
        """Create an empty network."""
        network = RadialNetwork(system_base_mva=100.0)
        
        assert network.system_base_mva == 100.0
        assert len(network.list_buses()) == 0
    
    def test_add_bus_to_network(self):
        """Add a bus to the network."""
        network = RadialNetwork()
        bus = Bus(id="BUS-001", name="Test", voltage_nominal=0.48)
        
        network.add_bus(bus)
        
        assert "BUS-001" in network.list_buses()
        assert network.get_bus("BUS-001") == bus
    
    def test_duplicate_bus_raises_error(self):
        """Cannot add bus with duplicate ID."""
        network = RadialNetwork()
        bus1 = Bus(id="BUS-001", name="First", voltage_nominal=0.48)
        bus2 = Bus(id="BUS-001", name="Duplicate", voltage_nominal=0.48)
        
        network.add_bus(bus1)
        
        with pytest.raises(ValueError, match="already exists"):
            network.add_bus(bus2)
    
    def test_add_utility_source(self):
        """Add utility source connected to a bus."""
        network = RadialNetwork()
        bus = Bus(id="BUS-001", name="Main", voltage_nominal=13.8)
        source = UtilitySource(
            id="UTIL-001",
            name="Grid",
            short_circuit_mva=500.0,
            voltage_nominal=13.8,
            x_r_ratio=15.0,
        )
        
        network.add_bus(bus)
        network.add_utility_source(source, bus_id="BUS-001")
        
        # Should not raise
        assert True
    
    def test_utility_source_requires_bus(self):
        """Utility source must connect to existing bus."""
        network = RadialNetwork()
        source = UtilitySource(
            id="UTIL-001",
            name="Grid",
            short_circuit_mva=500.0,
            voltage_nominal=13.8,
            x_r_ratio=15.0,
        )
        
        with pytest.raises(ValueError, match="not found"):
            network.add_utility_source(source, bus_id="NONEXISTENT")
    
    def test_only_one_utility_source(self):
        """Radial network supports only one utility source."""
        network = RadialNetwork()
        bus1 = Bus(id="BUS-001", name="Main", voltage_nominal=13.8)
        bus2 = Bus(id="BUS-002", name="Alt", voltage_nominal=13.8)
        source1 = UtilitySource(
            id="UTIL-001", name="Grid1",
            short_circuit_mva=500.0, voltage_nominal=13.8, x_r_ratio=15.0,
        )
        source2 = UtilitySource(
            id="UTIL-002", name="Grid2",
            short_circuit_mva=350.0, voltage_nominal=13.8, x_r_ratio=12.0,
        )
        
        network.add_bus(bus1)
        network.add_bus(bus2)
        network.add_utility_source(source1, bus_id="BUS-001")
        
        with pytest.raises(ValueError, match="already has a utility"):
            network.add_utility_source(source2, bus_id="BUS-002")


class TestPattern1_UtilityOnly:
    """
    Pattern 1: Utility → Bus → Fault
    
    The simplest case - fault at the utility connection point.
    Fault current limited only by utility source impedance.
    
    Test Configuration:
        Utility: 500 MVA, 13.8 kV, X/R = 15
        
    Hand Calculation:
        Z_util = 100 / 500 = 0.2 pu
        I_fault_pu = 1.0 / 0.2 = 5.0 pu
        I_base = 100,000 / (√3 × 13.8) = 4184 A = 4.184 kA
        I_fault = 5.0 × 4.184 = 20.92 kA
    """

    def test_fault_at_utility_bus(self):
        """Fault current at utility connection point."""
        # Build network
        network = RadialNetwork(system_base_mva=100.0)
        
        bus = Bus(id="BUS-001", name="13.8kV Bus", voltage_nominal=13.8)
        source = UtilitySource(
            id="UTIL-001",
            name="Utility",
            short_circuit_mva=500.0,
            voltage_nominal=13.8,
            x_r_ratio=15.0,
            system_base_mva=100.0,
        )
        
        network.add_bus(bus)
        network.add_utility_source(source, bus_id="BUS-001")
        
        # Calculate fault
        result = network.calculate_fault_at_bus("BUS-001")
        
        # Verify against hand calculation
        expected_z_pu = 0.2
        expected_i_ka = 20.92
        
        assert result.z_total_pu == pytest.approx(expected_z_pu, rel=1e-3)
        assert result.i_fault_ka == pytest.approx(expected_i_ka, rel=1e-2)
        assert result.x_r_ratio == pytest.approx(15.0, rel=1e-3)


class TestPattern2_WithTransformer:
    """
    Pattern 2: Utility → Transformer → Bus → Fault
    
    Fault on secondary side of transformer.
    Fault current limited by utility + transformer impedance.
    
    Test Configuration:
        Utility: 500 MVA, 13.8 kV, X/R = 15
        Transformer: 2 MVA, 13.8/0.48 kV, 5.75% Z, X/R = 8
        
    Hand Calculation (100 MVA base):
        Z_util = 0.2 pu (R=0.01331, X=0.1996)
        Z_xfmr = 0.0575 × (100/2) = 2.875 pu (R=0.3566, X=2.8528)
        Z_total = √((0.01331+0.3566)² + (0.1996+2.8528)²)
                = √(0.3699² + 3.0524²) = √(0.1368 + 9.317) = 3.075 pu
        I_fault_pu = 1.0 / 3.075 = 0.3252 pu
        I_base at 480V = 100,000 / (√3 × 0.48) = 120,281 A
        I_fault = 0.3252 × 120.281 = 39.11 kA
    """

    def test_fault_at_transformer_secondary(self):
        """Fault current at transformer secondary."""
        network = RadialNetwork(system_base_mva=100.0)
        
        # Components
        bus_pri = Bus(id="BUS-PRI", name="13.8kV Bus", voltage_nominal=13.8)
        bus_sec = Bus(id="BUS-SEC", name="480V Bus", voltage_nominal=0.48)
        
        source = UtilitySource(
            id="UTIL-001", name="Utility",
            short_circuit_mva=500.0, voltage_nominal=13.8, x_r_ratio=15.0,
            system_base_mva=100.0,
        )
        
        xfmr = Transformer(
            id="TX-001", name="Main Xfmr",
            rated_power_mva=2.0,
            voltage_primary=13.8, voltage_secondary=0.48,
            impedance_percent=5.75, x_r_ratio=8.0,
            system_base_mva=100.0,
        )
        
        # Build network
        network.add_bus(bus_pri)
        network.add_bus(bus_sec)
        network.add_utility_source(source, bus_id="BUS-PRI")
        network.add_transformer(xfmr, from_bus="BUS-PRI", to_bus="BUS-SEC")
        
        # Calculate fault at secondary
        result = network.calculate_fault_at_bus("BUS-SEC")
        
        # Verify against hand calculation
        expected_z_pu = 3.075
        expected_i_ka = 39.11
        
        assert result.z_total_pu == pytest.approx(expected_z_pu, rel=1e-2)
        assert result.i_fault_ka == pytest.approx(expected_i_ka, rel=2e-2)
    
    def test_fault_at_primary_unchanged(self):
        """Fault at primary should not include transformer impedance."""
        network = RadialNetwork(system_base_mva=100.0)
        
        bus_pri = Bus(id="BUS-PRI", name="13.8kV Bus", voltage_nominal=13.8)
        bus_sec = Bus(id="BUS-SEC", name="480V Bus", voltage_nominal=0.48)
        
        source = UtilitySource(
            id="UTIL-001", name="Utility",
            short_circuit_mva=500.0, voltage_nominal=13.8, x_r_ratio=15.0,
            system_base_mva=100.0,
        )
        
        xfmr = Transformer(
            id="TX-001", name="Main Xfmr",
            rated_power_mva=2.0,
            voltage_primary=13.8, voltage_secondary=0.48,
            impedance_percent=5.75, x_r_ratio=8.0,
            system_base_mva=100.0,
        )
        
        network.add_bus(bus_pri)
        network.add_bus(bus_sec)
        network.add_utility_source(source, bus_id="BUS-PRI")
        network.add_transformer(xfmr, from_bus="BUS-PRI", to_bus="BUS-SEC")
        
        # Fault at primary - should only see utility impedance
        result = network.calculate_fault_at_bus("BUS-PRI")
        
        expected_z_pu = 0.2  # Only utility
        assert result.z_total_pu == pytest.approx(expected_z_pu, rel=1e-3)


class TestPattern3_WithCable:
    """
    Pattern 3: Utility → Transformer → Cable → Bus → Fault
    
    Full industrial feeder with cable.
    
    Test Configuration:
        Utility: 500 MVA, 13.8 kV, X/R = 15
        Transformer: 2 MVA, 13.8/0.48 kV, 5.75% Z, X/R = 8
        Cable: 30m of 500 kcmil (R=0.105 Ω/km, X=0.128 Ω/km)
        
    Hand Calculation (100 MVA base):
        Z_util = 0.2 pu
        Z_xfmr = 2.875 pu
        
        Cable in ohms:
            R = 0.105 × 0.030 = 0.00315 Ω
            X = 0.128 × 0.030 = 0.00384 Ω
        
        Z_base at 480V = 0.48² / 100 = 0.002304 Ω
        Cable in pu:
            R_pu = 0.00315 / 0.002304 = 1.367 pu
            X_pu = 0.00384 / 0.002304 = 1.667 pu
        
        Total:
            R_total = 0.01331 + 0.3566 + 1.367 = 1.737 pu
            X_total = 0.1996 + 2.8528 + 1.667 = 4.720 pu
            Z_total = √(1.737² + 4.720²) = 5.029 pu
        
        I_fault = 1.0 / 5.029 = 0.1988 pu
        I_fault = 0.1988 × 120.281 = 23.91 kA
    """

    def test_fault_at_end_of_cable(self):
        """Fault current at end of cable."""
        network = RadialNetwork(system_base_mva=100.0)
        
        # Buses
        bus_pri = Bus(id="BUS-PRI", name="13.8kV", voltage_nominal=13.8)
        bus_sec = Bus(id="BUS-SEC", name="480V Switchgear", voltage_nominal=0.48)
        bus_panel = Bus(id="BUS-PANEL", name="480V Panel", voltage_nominal=0.48)
        
        # Source
        source = UtilitySource(
            id="UTIL-001", name="Utility",
            short_circuit_mva=500.0, voltage_nominal=13.8, x_r_ratio=15.0,
            system_base_mva=100.0,
        )
        
        # Transformer
        xfmr = Transformer(
            id="TX-001", name="Main Xfmr",
            rated_power_mva=2.0,
            voltage_primary=13.8, voltage_secondary=0.48,
            impedance_percent=5.75, x_r_ratio=8.0,
            system_base_mva=100.0,
        )
        
        # Cable
        cable = Cable(
            id="CBL-001", name="Feeder",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
            system_base_mva=100.0,
        )
        
        # Build network
        network.add_bus(bus_pri)
        network.add_bus(bus_sec)
        network.add_bus(bus_panel)
        network.add_utility_source(source, bus_id="BUS-PRI")
        network.add_transformer(xfmr, from_bus="BUS-PRI", to_bus="BUS-SEC")
        network.add_cable(cable, from_bus="BUS-SEC", to_bus="BUS-PANEL")
        
        # Calculate fault at panel
        result = network.calculate_fault_at_bus("BUS-PANEL")
        
        # Verify against hand calculation
        expected_z_pu = 5.029
        expected_i_ka = 23.91
        
        assert result.z_total_pu == pytest.approx(expected_z_pu, rel=2e-2)
        assert result.i_fault_ka == pytest.approx(expected_i_ka, rel=2e-2)


class TestImpedanceBreakdown:
    """Test that impedance breakdown is correctly reported."""

    def test_breakdown_contains_all_components(self):
        """Impedance breakdown should list all contributing components."""
        network = RadialNetwork(system_base_mva=100.0)
        
        bus_pri = Bus(id="BUS-PRI", name="13.8kV", voltage_nominal=13.8)
        bus_sec = Bus(id="BUS-SEC", name="480V", voltage_nominal=0.48)
        
        source = UtilitySource(
            id="UTIL-001", name="Utility",
            short_circuit_mva=500.0, voltage_nominal=13.8, x_r_ratio=15.0,
            system_base_mva=100.0,
        )
        
        xfmr = Transformer(
            id="TX-001", name="Xfmr",
            rated_power_mva=2.0,
            voltage_primary=13.8, voltage_secondary=0.48,
            impedance_percent=5.75, x_r_ratio=8.0,
            system_base_mva=100.0,
        )
        
        network.add_bus(bus_pri)
        network.add_bus(bus_sec)
        network.add_utility_source(source, bus_id="BUS-PRI")
        network.add_transformer(xfmr, from_bus="BUS-PRI", to_bus="BUS-SEC")
        
        result = network.calculate_fault_at_bus("BUS-SEC")
        
        # Check breakdown contains expected components
        assert len(result.impedance_breakdown) == 2
        assert any("UTIL-001" in key for key in result.impedance_breakdown.keys())
        assert any("TX-001" in key for key in result.impedance_breakdown.keys())


class TestErrorHandling:
    """Test error handling in fault calculations."""

    def test_fault_at_nonexistent_bus(self):
        """Cannot calculate fault at bus that doesn't exist."""
        network = RadialNetwork()
        bus = Bus(id="BUS-001", name="Test", voltage_nominal=0.48)
        network.add_bus(bus)
        
        with pytest.raises(ValueError, match="not found"):
            network.calculate_fault_at_bus("NONEXISTENT")
    
    def test_fault_without_source(self):
        """Cannot calculate fault without utility source."""
        network = RadialNetwork()
        bus = Bus(id="BUS-001", name="Test", voltage_nominal=0.48)
        network.add_bus(bus)
        
        with pytest.raises(ValueError, match="No utility source"):
            network.calculate_fault_at_bus("BUS-001")
    
    def test_fault_at_disconnected_bus(self):
        """Cannot calculate fault at bus with no path from source."""
        network = RadialNetwork()
        
        bus1 = Bus(id="BUS-001", name="Connected", voltage_nominal=13.8)
        bus2 = Bus(id="BUS-002", name="Disconnected", voltage_nominal=0.48)
        
        source = UtilitySource(
            id="UTIL-001", name="Utility",
            short_circuit_mva=500.0, voltage_nominal=13.8, x_r_ratio=15.0,
        )
        
        network.add_bus(bus1)
        network.add_bus(bus2)  # Not connected to anything
        network.add_utility_source(source, bus_id="BUS-001")
        
        with pytest.raises(ValueError, match="No path"):
            network.calculate_fault_at_bus("BUS-002")


class TestXRRatioCalculation:
    """Test X/R ratio is correctly calculated for the total impedance."""

    def test_xr_ratio_single_component(self):
        """X/R ratio for single component."""
        network = RadialNetwork(system_base_mva=100.0)
        
        bus = Bus(id="BUS-001", name="Test", voltage_nominal=13.8)
        source = UtilitySource(
            id="UTIL-001", name="Utility",
            short_circuit_mva=500.0, voltage_nominal=13.8, x_r_ratio=15.0,
            system_base_mva=100.0,
        )
        
        network.add_bus(bus)
        network.add_utility_source(source, bus_id="BUS-001")
        
        result = network.calculate_fault_at_bus("BUS-001")
        
        # X/R should match source
        assert result.x_r_ratio == pytest.approx(15.0, rel=1e-3)
    
    def test_xr_ratio_combined_components(self):
        """X/R ratio for combined utility + transformer."""
        network = RadialNetwork(system_base_mva=100.0)
        
        bus_pri = Bus(id="BUS-PRI", name="13.8kV", voltage_nominal=13.8)
        bus_sec = Bus(id="BUS-SEC", name="480V", voltage_nominal=0.48)
        
        source = UtilitySource(
            id="UTIL-001", name="Utility",
            short_circuit_mva=500.0, voltage_nominal=13.8, x_r_ratio=15.0,
            system_base_mva=100.0,
        )
        
        xfmr = Transformer(
            id="TX-001", name="Xfmr",
            rated_power_mva=2.0,
            voltage_primary=13.8, voltage_secondary=0.48,
            impedance_percent=5.75, x_r_ratio=8.0,
            system_base_mva=100.0,
        )
        
        network.add_bus(bus_pri)
        network.add_bus(bus_sec)
        network.add_utility_source(source, bus_id="BUS-PRI")
        network.add_transformer(xfmr, from_bus="BUS-PRI", to_bus="BUS-SEC")
        
        result = network.calculate_fault_at_bus("BUS-SEC")
        
        # Calculate expected X/R
        # R_total = 0.01331 + 0.3566 = 0.3699 pu
        # X_total = 0.1996 + 2.8528 = 3.0524 pu
        # X/R = 3.0524 / 0.3699 = 8.25
        expected_xr = 3.0524 / 0.3699
        
        assert result.x_r_ratio == pytest.approx(expected_xr, rel=2e-2)