"""
Unit Tests for Transformer Component
====================================

Test Philosophy:
    The Transformer component models the impedance between two voltage
    levels. The critical calculation is converting nameplate %Z to
    per-unit impedance on the system base.

Reference Equations:
    On transformer's own base:
        Z_pu = Z% / 100
    
    On system base (S_base):
        Z_pu_system = Z_pu_own × (S_base / S_rated)
    
    In ohms (referred to secondary):
        Z_base = V_secondary² / S_rated
        Z_ohms = Z_pu_own × Z_base

Traceability:
    - REQ-COMP-FUNC-3: Transformer class properties
    - IEC 60909-0, Section 6: Transformer impedance
"""

import pytest
import math
from arc_flash_studio.components.transformer import Transformer, VectorGroup


class TestTransformerCreation:
    """Test basic transformer creation."""

    def test_create_typical_transformer(self):
        """Create a typical 2 MVA, 13.8kV/480V transformer."""
        xfmr = Transformer(
            id="TX-001",
            name="Main Transformer",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        assert xfmr.id == "TX-001"
        assert xfmr.rated_power_mva == 2.0
        assert xfmr.voltage_primary == 13.8
        assert xfmr.voltage_secondary == 0.48
        assert xfmr.impedance_percent == 5.75
        assert xfmr.x_r_ratio == 8.0
    
    def test_default_vector_group(self):
        """Default vector group is Dyn11."""
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=1.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        assert xfmr.vector_group == VectorGroup.Dyn11
    
    def test_default_tap_position(self):
        """Default tap position is 0% (nominal)."""
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=1.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        assert xfmr.tap_percent == 0.0


class TestTransformerImpedanceOnOwnBase:
    """Test impedance calculations on transformer's own MVA base."""

    def test_z_pu_on_own_base(self):
        """
        Z_pu on own base = Z% / 100
        
        For 5.75% impedance:
            Z_pu = 5.75 / 100 = 0.0575 pu
        """
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        assert xfmr.z_pu_on_own_base == pytest.approx(0.0575, rel=1e-6)
    
    def test_r_x_split_on_own_base(self):
        """
        Test R and X split using X/R ratio.
        
        For Z = 0.0575 pu, X/R = 8:
            Z = √(R² + X²)
            X = R × 8
            Z = R × √(1 + 64) = R × 8.062
            R = 0.0575 / 8.062 = 0.00713 pu
            X = 0.00713 × 8 = 0.05705 pu
        """
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        expected_r = 0.0575 / math.sqrt(1 + 64)
        expected_x = expected_r * 8.0
        
        assert xfmr.r_pu_on_own_base == pytest.approx(expected_r, rel=1e-3)
        assert xfmr.x_pu_on_own_base == pytest.approx(expected_x, rel=1e-3)
    
    def test_r_x_combine_to_z(self):
        """R and X should combine back to Z."""
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        z_calc = math.sqrt(xfmr.r_pu_on_own_base**2 + xfmr.x_pu_on_own_base**2)
        assert z_calc == pytest.approx(xfmr.z_pu_on_own_base, rel=1e-6)


class TestTransformerImpedanceOnSystemBase:
    """Test impedance conversion to system base."""

    def test_z_pu_on_100mva_base(self):
        """
        Convert to 100 MVA system base.
        
        Z_pu_system = Z_pu_own × (S_base / S_rated)
        
        For 2 MVA transformer, 5.75% Z, 100 MVA base:
            Z_pu = 0.0575 × (100 / 2) = 2.875 pu
        """
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
            system_base_mva=100.0,
        )
        
        assert xfmr.z_pu == pytest.approx(2.875, rel=1e-6)
    
    def test_z_pu_on_10mva_base(self):
        """
        Convert to 10 MVA system base.
        
        For 2 MVA transformer, 5.75% Z, 10 MVA base:
            Z_pu = 0.0575 × (10 / 2) = 0.2875 pu
        """
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
            system_base_mva=10.0,
        )
        
        assert xfmr.z_pu == pytest.approx(0.2875, rel=1e-6)
    
    def test_r_x_scale_proportionally(self):
        """R and X should scale with the same factor as Z."""
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
            system_base_mva=100.0,
        )
        
        scale_factor = 100.0 / 2.0
        
        assert xfmr.r_pu == pytest.approx(xfmr.r_pu_on_own_base * scale_factor, rel=1e-6)
        assert xfmr.x_pu == pytest.approx(xfmr.x_pu_on_own_base * scale_factor, rel=1e-6)


class TestTransformerImpedanceInOhms:
    """Test impedance in ohms referred to secondary."""

    def test_z_base_secondary(self):
        """
        Base impedance at secondary voltage.
        
        Z_base = V² / S = 0.48² / 2.0 = 0.1152 Ω
        """
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        expected_z_base = (0.48 ** 2) / 2.0
        assert xfmr.z_base_secondary_ohms == pytest.approx(expected_z_base, rel=1e-6)
    
    def test_z_ohms_secondary(self):
        """
        Impedance in ohms at secondary.
        
        Z_ohms = Z_pu × Z_base = 0.0575 × 0.1152 = 0.006624 Ω
        """
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        expected_z_ohms = 0.0575 * ((0.48 ** 2) / 2.0)
        assert xfmr.z_ohms_secondary == pytest.approx(expected_z_ohms, rel=1e-3)


class TestTransformerTurnsRatio:
    """Test turns ratio and rated currents."""

    def test_turns_ratio(self):
        """
        Turns ratio = V_primary / V_secondary
        
        For 13.8kV / 0.48kV:
            Turns ratio = 13.8 / 0.48 = 28.75
        """
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        assert xfmr.turns_ratio == pytest.approx(28.75, rel=1e-3)
    
    def test_rated_current_primary(self):
        """
        Rated current on primary.
        
        I = S / (√3 × V) = 2000 kVA / (√3 × 13.8 kV) = 83.67 A
        """
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        expected_i = (2.0 * 1000) / (math.sqrt(3) * 13.8)
        assert xfmr.rated_current_primary_a == pytest.approx(expected_i, rel=1e-3)
    
    def test_rated_current_secondary(self):
        """
        Rated current on secondary.
        
        I = S / (√3 × V) = 2000 kVA / (√3 × 0.48 kV) = 2406 A
        """
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        expected_i = (2.0 * 1000) / (math.sqrt(3) * 0.48)
        assert xfmr.rated_current_secondary_a == pytest.approx(expected_i, rel=1e-3)


class TestTransformerValidation:
    """Test input validation."""

    def test_impedance_too_low(self):
        """Impedance below 1% is unrealistic."""
        with pytest.raises(ValueError):
            Transformer(
                id="TX-001",
                name="Test",
                rated_power_mva=2.0,
                voltage_primary=13.8,
                voltage_secondary=0.48,
                impedance_percent=0.5,  # Too low
                x_r_ratio=8.0,
            )
    
    def test_impedance_too_high(self):
        """Impedance above 20% is unrealistic."""
        with pytest.raises(ValueError):
            Transformer(
                id="TX-001",
                name="Test",
                rated_power_mva=2.0,
                voltage_primary=13.8,
                voltage_secondary=0.48,
                impedance_percent=25.0,  # Too high
                x_r_ratio=8.0,
            )
    
    def test_negative_power_raises_error(self):
        """Power rating must be positive."""
        with pytest.raises(ValueError):
            Transformer(
                id="TX-001",
                name="Test",
                rated_power_mva=-2.0,
                voltage_primary=13.8,
                voltage_secondary=0.48,
                impedance_percent=5.75,
                x_r_ratio=8.0,
            )
    
    def test_x_r_ratio_too_low(self):
        """X/R ratio below 1 is unrealistic for transformers."""
        with pytest.raises(ValueError):
            Transformer(
                id="TX-001",
                name="Test",
                rated_power_mva=2.0,
                voltage_primary=13.8,
                voltage_secondary=0.48,
                impedance_percent=5.75,
                x_r_ratio=0.5,  # Too low
            )


class TestTransformerComplexImpedance:
    """Test complex impedance methods."""

    def test_complex_impedance_pu(self):
        """Get complex impedance in per-unit."""
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
            system_base_mva=100.0,
        )
        
        z_complex = xfmr.get_impedance_complex_pu()
        
        assert z_complex.real == pytest.approx(xfmr.r_pu, rel=1e-6)
        assert z_complex.imag == pytest.approx(xfmr.x_pu, rel=1e-6)
    
    def test_complex_impedance_ohms_secondary(self):
        """Get complex impedance in ohms referred to secondary."""
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        z_complex = xfmr.get_impedance_complex_ohms(referred_to="secondary")
        
        assert z_complex.real == pytest.approx(xfmr.r_ohms_secondary, rel=1e-6)
        assert z_complex.imag == pytest.approx(xfmr.x_ohms_secondary, rel=1e-6)


class TestTransformerJSONSerialization:
    """Test Pydantic JSON serialization."""

    def test_export_to_json(self):
        """Transformer can be exported to JSON."""
        xfmr = Transformer(
            id="TX-001",
            name="Test",
            rated_power_mva=2.0,
            voltage_primary=13.8,
            voltage_secondary=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0,
        )
        
        json_str = xfmr.model_dump_json()
        assert "TX-001" in json_str
        assert "5.75" in json_str
    
    def test_import_from_json(self):
        """Transformer can be created from JSON."""
        json_str = '''
        {
            "id": "TX-002",
            "name": "From JSON",
            "rated_power_mva": 1.5,
            "voltage_primary": 4.16,
            "voltage_secondary": 0.48,
            "impedance_percent": 6.0,
            "x_r_ratio": 10.0
        }
        '''
        xfmr = Transformer.model_validate_json(json_str)
        
        assert xfmr.id == "TX-002"
        assert xfmr.rated_power_mva == 1.5
        assert xfmr.impedance_percent == 6.0