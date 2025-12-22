"""
Unit Tests for Cable Component
==============================

Test Philosophy:
    The Cable component models conductor impedance based on length
    and per-unit-length parameters. Key calculations are total ohmic
    impedance and conversion to per-unit.

Reference Equations:
    Ohmic values:
        R_ohms = R_per_km × length_km
        X_ohms = X_per_km × length_km
        Z_ohms = √(R² + X²)
    
    Per-unit values:
        Z_base = V² / S_base
        R_pu = R_ohms / Z_base
        X_pu = X_ohms / Z_base

Traceability:
    - REQ-COMP-FUNC-4: Cable class properties
    - NEC Chapter 9, Table 9: Cable impedance data
"""

import pytest
import math
from arc_flash_studio.components.cable import Cable, create_cable_from_size, COMMON_CABLE_DATA


class TestCableCreation:
    """Test basic cable creation."""

    def test_create_cable_with_explicit_impedance(self):
        """Create a cable with explicitly specified impedance."""
        cable = Cable(
            id="CBL-001",
            name="Main Feeder",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
        )
        
        assert cable.id == "CBL-001"
        assert cable.length_m == 30.0
        assert cable.r_per_km == 0.105
        assert cable.x_per_km == 0.128
    
    def test_create_cable_from_size_lookup(self):
        """Create a cable using standard conductor size."""
        cable = create_cable_from_size(
            id="CBL-002",
            name="500 kcmil Feeder",
            conductor_size="500 kcmil",
            length_m=50.0,
            voltage_nominal=0.48,
        )
        
        assert cable.id == "CBL-002"
        assert cable.length_m == 50.0
        assert cable.conductor_size == "500 kcmil"
        # Check impedance matches lookup table
        assert cable.r_per_km == COMMON_CABLE_DATA["500 kcmil"][0]
        assert cable.x_per_km == COMMON_CABLE_DATA["500 kcmil"][1]
    
    def test_invalid_conductor_size_raises_error(self):
        """Unknown conductor size should raise error."""
        with pytest.raises(ValueError, match="Unknown conductor size"):
            create_cable_from_size(
                id="CBL-003",
                name="Invalid",
                conductor_size="999 kcmil",  # Doesn't exist
                length_m=50.0,
                voltage_nominal=0.48,
            )


class TestCableLengthConversion:
    """Test length unit conversions."""

    def test_length_in_km(self):
        """Length should be convertible to km."""
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=100.0,
            r_per_km=0.1,
            x_per_km=0.1,
            voltage_nominal=0.48,
        )
        
        assert cable.length_km == pytest.approx(0.1, rel=1e-6)
    
    def test_short_cable_length(self):
        """Test short cable (30m)."""
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.1,
            x_per_km=0.1,
            voltage_nominal=0.48,
        )
        
        assert cable.length_km == pytest.approx(0.030, rel=1e-6)


class TestCableOhmicImpedance:
    """Test impedance calculations in ohms."""

    def test_resistance_ohms(self):
        """
        Total resistance = R_per_km × length_km
        
        For 30m cable with R = 0.105 Ω/km:
            R = 0.105 × 0.030 = 0.00315 Ω
        """
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
        )
        
        expected_r = 0.105 * 0.030
        assert cable.r_ohms == pytest.approx(expected_r, rel=1e-6)
    
    def test_reactance_ohms(self):
        """
        Total reactance = X_per_km × length_km
        
        For 30m cable with X = 0.128 Ω/km:
            X = 0.128 × 0.030 = 0.00384 Ω
        """
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
        )
        
        expected_x = 0.128 * 0.030
        assert cable.x_ohms == pytest.approx(expected_x, rel=1e-6)
    
    def test_impedance_magnitude(self):
        """
        Z = √(R² + X²)
        """
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
        )
        
        r = 0.105 * 0.030
        x = 0.128 * 0.030
        expected_z = math.sqrt(r**2 + x**2)
        
        assert cable.z_ohms == pytest.approx(expected_z, rel=1e-6)
    
    def test_x_r_ratio(self):
        """X/R ratio calculation."""
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
        )
        
        expected_xr = 0.128 / 0.105
        assert cable.x_r_ratio == pytest.approx(expected_xr, rel=1e-6)


class TestCablePerUnitImpedance:
    """Test impedance conversion to per-unit."""

    def test_z_base_ohms(self):
        """
        Base impedance = V² / S_base
        
        For 480V, 100 MVA base:
            Z_base = 0.48² / 100 = 0.002304 Ω
        """
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
            system_base_mva=100.0,
        )
        
        expected_z_base = (0.48 ** 2) / 100.0
        assert cable.z_base_ohms == pytest.approx(expected_z_base, rel=1e-6)
    
    def test_r_pu(self):
        """
        R_pu = R_ohms / Z_base
        
        For R = 0.00315 Ω, Z_base = 0.002304 Ω:
            R_pu = 0.00315 / 0.002304 = 1.367 pu
        """
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
            system_base_mva=100.0,
        )
        
        r_ohms = 0.105 * 0.030
        z_base = (0.48 ** 2) / 100.0
        expected_r_pu = r_ohms / z_base
        
        assert cable.r_pu == pytest.approx(expected_r_pu, rel=1e-3)
    
    def test_x_pu(self):
        """
        X_pu = X_ohms / Z_base
        
        For X = 0.00384 Ω, Z_base = 0.002304 Ω:
            X_pu = 0.00384 / 0.002304 = 1.667 pu
        """
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
            system_base_mva=100.0,
        )
        
        x_ohms = 0.128 * 0.030
        z_base = (0.48 ** 2) / 100.0
        expected_x_pu = x_ohms / z_base
        
        assert cable.x_pu == pytest.approx(expected_x_pu, rel=1e-3)
    
    def test_z_pu(self):
        """Per-unit impedance magnitude."""
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
            system_base_mva=100.0,
        )
        
        z_calc = math.sqrt(cable.r_pu**2 + cable.x_pu**2)
        assert cable.z_pu == pytest.approx(z_calc, rel=1e-6)


class TestCableDifferentSystemBases:
    """Test per-unit conversion with different system bases."""

    def test_100mva_base(self):
        """Test with 100 MVA system base."""
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
            system_base_mva=100.0,
        )
        
        z_base = (0.48 ** 2) / 100.0
        assert cable.z_base_ohms == pytest.approx(z_base, rel=1e-6)
    
    def test_10mva_base(self):
        """Test with 10 MVA system base - should give 10x lower Z_pu."""
        cable_100 = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
            system_base_mva=100.0,
        )
        
        cable_10 = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
            system_base_mva=10.0,
        )
        
        # Z_pu should scale inversely with S_base
        # (smaller base = larger Z_base = smaller Z_pu)
        assert cable_10.z_pu == pytest.approx(cable_100.z_pu / 10.0, rel=1e-6)


class TestCableValidation:
    """Test input validation."""

    def test_negative_length_raises_error(self):
        """Cable length must be positive."""
        with pytest.raises(ValueError):
            Cable(
                id="CBL-001",
                name="Test",
                length_m=-30.0,
                r_per_km=0.105,
                x_per_km=0.128,
                voltage_nominal=0.48,
            )
    
    def test_zero_length_raises_error(self):
        """Cable length cannot be zero."""
        with pytest.raises(ValueError):
            Cable(
                id="CBL-001",
                name="Test",
                length_m=0.0,
                r_per_km=0.105,
                x_per_km=0.128,
                voltage_nominal=0.48,
            )
    
    def test_negative_resistance_raises_error(self):
        """Resistance must be positive."""
        with pytest.raises(ValueError):
            Cable(
                id="CBL-001",
                name="Test",
                length_m=30.0,
                r_per_km=-0.105,
                x_per_km=0.128,
                voltage_nominal=0.48,
            )


class TestCableComplexImpedance:
    """Test complex impedance methods."""

    def test_complex_impedance_pu(self):
        """Get complex impedance in per-unit."""
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
            system_base_mva=100.0,
        )
        
        z_complex = cable.get_impedance_complex_pu()
        
        assert z_complex.real == pytest.approx(cable.r_pu, rel=1e-6)
        assert z_complex.imag == pytest.approx(cable.x_pu, rel=1e-6)
    
    def test_complex_impedance_ohms(self):
        """Get complex impedance in ohms."""
        cable = Cable(
            id="CBL-001",
            name="Test",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
        )
        
        z_complex = cable.get_impedance_complex_ohms()
        
        assert z_complex.real == pytest.approx(cable.r_ohms, rel=1e-6)
        assert z_complex.imag == pytest.approx(cable.x_ohms, rel=1e-6)


class TestCommonCableData:
    """Test the common cable data lookup table."""

    def test_500kcmil_data(self):
        """Verify 500 kcmil data matches NEC Table 9 approximation."""
        r, x, ampacity = COMMON_CABLE_DATA["500 kcmil"]
        
        assert r == 0.105  # Ω/km
        assert x == 0.128  # Ω/km
        assert ampacity == 380  # A
    
    def test_4_0_awg_data(self):
        """Verify 4/0 AWG data."""
        r, x, ampacity = COMMON_CABLE_DATA["4/0 AWG"]
        
        assert r == 0.220
        assert x == 0.135
        assert ampacity == 230
    
    def test_all_sizes_have_three_values(self):
        """Every cable size should have (R, X, ampacity)."""
        for size, data in COMMON_CABLE_DATA.items():
            assert len(data) == 3, f"Size {size} should have 3 values"
            assert all(v > 0 for v in data), f"Size {size} values should be positive"


class TestCableJSONSerialization:
    """Test Pydantic JSON serialization."""

    def test_export_to_json(self):
        """Cable can be exported to JSON."""
        cable = Cable(
            id="CBL-001",
            name="Test Feeder",
            length_m=30.0,
            r_per_km=0.105,
            x_per_km=0.128,
            voltage_nominal=0.48,
        )
        
        json_str = cable.model_dump_json()
        assert "CBL-001" in json_str
        assert "30.0" in json_str
    
    def test_import_from_json(self):
        """Cable can be created from JSON."""
        json_str = '''
        {
            "id": "CBL-002",
            "name": "From JSON",
            "length_m": 50.0,
            "r_per_km": 0.1,
            "x_per_km": 0.08,
            "voltage_nominal": 0.48
        }
        '''
        cable = Cable.model_validate_json(json_str)
        
        assert cable.id == "CBL-002"
        assert cable.length_m == 50.0