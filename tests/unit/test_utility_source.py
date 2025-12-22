"""
Unit Tests for UtilitySource Component
======================================

Test Philosophy:
    These tests validate that the UtilitySource class correctly calculates
    the Thévenin equivalent impedance of a utility grid connection from
    nameplate/study data.

Reference Equations (IEC 60909 / IEEE 551):
    Z_pu = V_base² / (SC_MVA × S_base)
    
    Where:
        - V_base is in per-unit (1.0 on the system base)
        - SC_MVA is the available short-circuit MVA
        - S_base is the system base MVA (we use 100 MVA)
    
    R and X are derived from the X/R ratio:
        Z = √(R² + X²)
        X/R = ratio
        
    Solving:
        R = Z / √(1 + (X/R)²)
        X = R × (X/R)

Traceability:
    - REQ-COMP-FUNC-7: UtilitySource class properties
    - IEEE 1584-2018, Section 6.2: Short-circuit data collection
    - IEC 60909-0, Section 6: Network feeder impedance
"""

import pytest
import math


class TestUtilitySourceImpedance:
    """Test impedance calculations from utility source parameters."""

    def test_impedance_from_500mva_source(self):
        """
        Test Case: Typical industrial utility connection
        
        Given:
            - Short-circuit MVA: 500 MVA
            - Voltage: 13.8 kV
            - X/R ratio: 15
            - System base: 100 MVA
        
        Hand Calculation:
            Z_pu = 1.0² / (500/100) = 0.2 pu
            R = 0.2 / √(1 + 15²) = 0.2 / 15.033 = 0.01331 pu
            X = 0.01331 × 15 = 0.1996 pu
        
        On 13.8 kV, 100 MVA base:
            Z_base = V² / S = 13.8² / 100 = 1.9044 Ω
            Z_ohms = 0.2 × 1.9044 = 0.3809 Ω 
            R_ohms = 0.01331 × 1.9044 = 0.02535 Ω
            X_ohms = 0.1996 × 1.9044 = 0.3801 Ω
            Z_ohms is also referred to as Z_TH explicitly in some works.
        """
        from components.utility_source import UtilitySource
        
        source = UtilitySource(
            id="UTIL-001",
            name="Main Utility Feed",
            short_circuit_mva=500.0,
            voltage_nominal=13.8,  # kV
            x_r_ratio=15.0
        )
        
        # Test per-unit values (on 100 MVA base)
        assert source.z_pu == pytest.approx(0.2, rel=1e-3)
        assert source.r_pu == pytest.approx(0.01331, rel=1e-2)
        assert source.x_pu == pytest.approx(0.1996, rel=1e-2)
        
        # Test ohmic values (on 13.8 kV base)
        assert source.z_ohms == pytest.approx(0.3809, rel=1e-2)
        assert source.r_ohms == pytest.approx(0.02535, rel=1e-2)
        assert source.x_ohms == pytest.approx(0.3801, rel=1e-2)

    def test_impedance_from_150mva_source(self):
        """
        Test Case: Weaker utility source (rural/end of feeder)
        
        Given:
            - Short-circuit MVA: 150 MVA
            - Voltage: 13.8 kV
            - X/R ratio: 10
        
        Hand Calculation:
            Z_pu = 1.0² / (150/100) = 0.6667 pu
            R = 0.6667 / √(1 + 100) = 0.6667 / 10.05 = 0.06633 pu
            X = 0.06633 × 10 = 0.6633 pu
        """
        from components.utility_source import UtilitySource
        
        source = UtilitySource(
            id="UTIL-002",
            name="Rural Substation",
            short_circuit_mva=150.0,
            voltage_nominal=13.8,
            x_r_ratio=10.0
        )
        
        assert source.z_pu == pytest.approx(0.6667, rel=1e-3)
        assert source.r_pu == pytest.approx(0.06633, rel=1e-2)
        assert source.x_pu == pytest.approx(0.6633, rel=1e-2)

    def test_impedance_from_1000mva_source(self):
        """
        Test Case: Stiff utility source (close to substation)
        
        Given:
            - Short-circuit MVA: 1000 MVA
            - Voltage: 13.8 kV
            - X/R ratio: 20
        
        Hand Calculation:
            Z_pu = 1.0² / (1000/100) = 0.1 pu
            R = 0.1 / √(1 + 400) = 0.1 / 20.025 = 0.004994 pu
            X = 0.004994 × 20 = 0.09988 pu
        """
        from components.utility_source import UtilitySource
        
        source = UtilitySource(
            id="UTIL-003",
            name="Industrial Substation",
            short_circuit_mva=1000.0,
            voltage_nominal=13.8,
            x_r_ratio=20.0
        )
        
        assert source.z_pu == pytest.approx(0.1, rel=1e-3)
        assert source.r_pu == pytest.approx(0.004994, rel=1e-2)
        assert source.x_pu == pytest.approx(0.09988, rel=1e-2)

    def test_low_voltage_source(self):
        """
        Test Case: Low-voltage utility (480V service entrance)
        
        Given:
            - Short-circuit MVA: 50 MVA (typical for 480V service)
            - Voltage: 0.48 kV
            - X/R ratio: 5
        
        Hand Calculation:
            Z_pu = 1.0² / (50/100) = 2.0 pu
            R = 2.0 / √(1 + 25) = 2.0 / 5.099 = 0.3922 pu
            X = 0.3922 × 5 = 1.961 pu
            
        On 480V, 100 MVA base:
            Z_base = 0.48² / 100 = 0.002304 Ω
            Z_ohms = 2.0 × 0.002304 = 0.004608 Ω
        """
        from components.utility_source import UtilitySource
        
        source = UtilitySource(
            id="UTIL-004",
            name="480V Service",
            short_circuit_mva=50.0,
            voltage_nominal=0.48,
            x_r_ratio=5.0
        )
        
        assert source.z_pu == pytest.approx(2.0, rel=1e-3)
        assert source.r_pu == pytest.approx(0.3922, rel=1e-2)
        assert source.x_pu == pytest.approx(1.961, rel=1e-2)


class TestUtilitySourceValidation:
    """Test input validation for UtilitySource."""

    def test_negative_sc_mva_raises_error(self):
        """Short-circuit MVA must be positive."""
        from components.utility_source import UtilitySource
        
        with pytest.raises(ValueError, match="short_circuit_mva"):
            UtilitySource(
                id="UTIL-ERR",
                name="Invalid",
                short_circuit_mva=-100.0,
                voltage_nominal=13.8,
                x_r_ratio=15.0
            )

    def test_zero_sc_mva_raises_error(self):
        """Short-circuit MVA cannot be zero (infinite impedance)."""
        from components.utility_source import UtilitySource
        
        with pytest.raises(ValueError, match="short_circuit_mva"):
            UtilitySource(
                id="UTIL-ERR",
                name="Invalid",
                short_circuit_mva=0.0,
                voltage_nominal=13.8,
                x_r_ratio=15.0
            )

    def test_negative_xr_ratio_raises_error(self):
        """X/R ratio must be positive."""
        from components.utility_source import UtilitySource
        
        with pytest.raises(ValueError, match="x_r_ratio"):
            UtilitySource(
                id="UTIL-ERR",
                name="Invalid",
                short_circuit_mva=500.0,
                voltage_nominal=13.8,
                x_r_ratio=-5.0
            )

    def test_zero_xr_ratio_raises_error(self):
        """X/R ratio cannot be zero (pure resistance is unrealistic for utility)."""
        from components.utility_source import UtilitySource
        
        with pytest.raises(ValueError, match="x_r_ratio"):
            UtilitySource(
                id="UTIL-ERR",
                name="Invalid",
                short_circuit_mva=500.0,
                voltage_nominal=13.8,
                x_r_ratio=0.0
            )

    def test_negative_voltage_raises_error(self):
        """Voltage must be positive."""
        from components.utility_source import UtilitySource
        
        with pytest.raises(ValueError, match="voltage"):
            UtilitySource(
                id="UTIL-ERR",
                name="Invalid",
                short_circuit_mva=500.0,
                voltage_nominal=-13.8,
                x_r_ratio=15.0
            )


class TestUtilitySourceProperties:
    """Test computed properties and methods."""

    def test_available_fault_current(self):
        """
        Test the available three-phase fault current calculation.
        
        I_fault = SC_MVA / (√3 × V_kV)
        
        For 500 MVA at 13.8 kV:
            I_fault = 500 / (1.732 × 13.8) = 500 / 23.90 = 20.92 kA
        """
        from components.utility_source import UtilitySource
        
        source = UtilitySource(
            id="UTIL-001",
            name="Test",
            short_circuit_mva=500.0,
            voltage_nominal=13.8,
            x_r_ratio=15.0
        )
        
        assert source.available_fault_current_ka == pytest.approx(20.92, rel=1e-2)

    def test_string_representation(self):
        """Test that __str__ provides useful information."""
        from components.utility_source import UtilitySource
        
        source = UtilitySource(
            id="UTIL-001",
            name="Main Feed",
            short_circuit_mva=500.0,
            voltage_nominal=13.8,
            x_r_ratio=15.0
        )
        
        str_repr = str(source)
        assert "UTIL-001" in str_repr
        assert "500" in str_repr or "500.0" in str_repr


class TestUtilitySourceSystemBase:
    """Test behavior with different system bases."""

    def test_custom_system_base(self):
        """
        Test impedance calculation with non-default system base.
        
        Using 10 MVA base instead of 100 MVA:
            Z_pu = 1.0² / (500/10) = 0.02 pu
        """
        from components.utility_source import UtilitySource
        
        source = UtilitySource(
            id="UTIL-001",
            name="Test",
            short_circuit_mva=500.0,
            voltage_nominal=13.8,
            x_r_ratio=15.0,
            system_base_mva=10.0
        )
        
        assert source.z_pu == pytest.approx(0.02, rel=1e-3)

    def test_impedance_on_different_voltage_base(self):
        """
        Test getting impedance referred to a different voltage level.
        
        Source at 13.8 kV, referred to 4.16 kV:
            Z_ratio = (4.16/13.8)² = 0.0909
            Z_4.16kV = Z_13.8kV × 0.0909
        """
        from components.utility_source import UtilitySource
        
        source = UtilitySource(
            id="UTIL-001",
            name="Test",
            short_circuit_mva=500.0,
            voltage_nominal=13.8,
            x_r_ratio=15.0
        )
        
        z_at_4kv = source.get_impedance_at_voltage(4.16)
        z_ratio = (4.16 / 13.8) ** 2
        
        assert z_at_4kv == pytest.approx(source.z_ohms * z_ratio, rel=1e-3)