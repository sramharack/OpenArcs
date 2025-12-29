"""
Unit Tests for Transformer
==========================

Tests for the Transformer component.

Traceability:
    - REQ-COMP-FUNC-8: Transformer with impedance conversion
"""

import pytest
import math
from arc_flash_studio.components import Transformer


class TestTransformerCreation:
    """Tests for creating Transformer instances."""
    
    def test_create_transformer(self):
        """Create a valid transformer."""
        xfmr = Transformer(
            id="TX-1",
            name="Main Transformer",
            hv_bus_id="HV-BUS",
            lv_bus_id="LV-BUS",
            rated_mva=2.0,
            hv_kv=13.8,
            lv_kv=0.48,
            impedance_percent=5.75,
            x_r_ratio=8.0
        )
        assert xfmr.id == "TX-1"
        assert xfmr.rated_mva == 2.0
        assert xfmr.hv_kv == 13.8
        assert xfmr.lv_kv == 0.48
        assert xfmr.impedance_percent == 5.75
        assert xfmr.x_r_ratio == 8.0
    
    def test_default_vector_group(self):
        """Default vector group is Dyn."""
        xfmr = Transformer(
            id="TX-1", name="Test",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=1.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.0, x_r_ratio=8.0
        )
        assert xfmr.vector_group == "Dyn"


class TestTransformerValidation:
    """Tests for Transformer validation."""
    
    def test_empty_id_raises_error(self):
        """Empty ID raises validation error."""
        with pytest.raises(ValueError):
            Transformer(
                id="", name="Test",
                hv_bus_id="HV", lv_bus_id="LV",
                rated_mva=1.0, hv_kv=13.8, lv_kv=0.48,
                impedance_percent=5.0, x_r_ratio=8.0
            )
    
    def test_negative_mva_raises_error(self):
        """Negative MVA raises validation error."""
        with pytest.raises(ValueError):
            Transformer(
                id="TX-1", name="Test",
                hv_bus_id="HV", lv_bus_id="LV",
                rated_mva=-1.0, hv_kv=13.8, lv_kv=0.48,
                impedance_percent=5.0, x_r_ratio=8.0
            )
    
    def test_impedance_below_min_raises_error(self):
        """Impedance below 1% raises validation error."""
        with pytest.raises(ValueError):
            Transformer(
                id="TX-1", name="Test",
                hv_bus_id="HV", lv_bus_id="LV",
                rated_mva=1.0, hv_kv=13.8, lv_kv=0.48,
                impedance_percent=0.5, x_r_ratio=8.0
            )
    
    def test_impedance_above_max_raises_error(self):
        """Impedance above 20% raises validation error."""
        with pytest.raises(ValueError):
            Transformer(
                id="TX-1", name="Test",
                hv_bus_id="HV", lv_bus_id="LV",
                rated_mva=1.0, hv_kv=13.8, lv_kv=0.48,
                impedance_percent=25.0, x_r_ratio=8.0
            )
    
    def test_xr_ratio_below_min_raises_error(self):
        """X/R ratio below 1 raises validation error."""
        with pytest.raises(ValueError):
            Transformer(
                id="TX-1", name="Test",
                hv_bus_id="HV", lv_bus_id="LV",
                rated_mva=1.0, hv_kv=13.8, lv_kv=0.48,
                impedance_percent=5.0, x_r_ratio=0.5
            )
    
    def test_xr_ratio_above_max_raises_error(self):
        """X/R ratio above 50 raises validation error."""
        with pytest.raises(ValueError):
            Transformer(
                id="TX-1", name="Test",
                hv_bus_id="HV", lv_bus_id="LV",
                rated_mva=1.0, hv_kv=13.8, lv_kv=0.48,
                impedance_percent=5.0, x_r_ratio=60.0
            )


class TestTransformerCalculations:
    """Tests for computed fields."""
    
    def test_vkr_percent_calculation(self):
        """
        vkr_percent = vk × (R/Z) = vk / sqrt(1 + (X/R)²)
        
        For vk=5.75%, X/R=8:
            R/Z = 1 / sqrt(1 + 64) = 1 / sqrt(65) = 0.124
            vkr = 5.75 × 0.124 = 0.713%
        """
        xfmr = Transformer(
            id="TX-1", name="Test",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        )
        
        expected_vkr = 5.75 / math.sqrt(1 + 64)
        assert xfmr.vkr_percent == pytest.approx(expected_vkr, rel=1e-6)
    
    def test_vkr_percent_different_values(self):
        """vkr_percent with different impedance and X/R."""
        xfmr = Transformer(
            id="TX-1", name="Test",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=1.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=6.0, x_r_ratio=10.0
        )
        
        expected_vkr = 6.0 / math.sqrt(1 + 100)
        assert xfmr.vkr_percent == pytest.approx(expected_vkr, rel=1e-6)
    
    def test_turns_ratio(self):
        """Turns ratio is HV/LV."""
        xfmr = Transformer(
            id="TX-1", name="Test",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        )
        
        expected_ratio = 13.8 / 0.48
        assert xfmr.turns_ratio == pytest.approx(expected_ratio, rel=1e-6)


class TestTransformerSerialization:
    """Tests for JSON serialization."""
    
    def test_export_to_dict(self):
        """Transformer exports to dictionary."""
        xfmr = Transformer(
            id="TX-1", name="Test",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        )
        data = xfmr.model_dump()
        assert data["id"] == "TX-1"
        assert data["rated_mva"] == 2.0
        assert data["impedance_percent"] == 5.75
    
    def test_import_from_dict(self):
        """Transformer imports from dictionary."""
        data = {
            "id": "TX-2",
            "name": "Test",
            "hv_bus_id": "HV",
            "lv_bus_id": "LV",
            "rated_mva": 5.0,
            "hv_kv": 34.5,
            "lv_kv": 4.16,
            "impedance_percent": 7.5,
            "x_r_ratio": 12.0,
            "vector_group": "Yyn0"
        }
        xfmr = Transformer(**data)
        assert xfmr.rated_mva == 5.0
        assert xfmr.vector_group == "Yyn0"


class TestTransformerStr:
    """Tests for string representation."""
    
    def test_str_contains_id(self):
        """String contains ID."""
        xfmr = Transformer(
            id="TX-1", name="Test",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        )
        assert "TX-1" in str(xfmr)
    
    def test_str_contains_mva(self):
        """String contains MVA rating."""
        xfmr = Transformer(
            id="TX-1", name="Test",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        )
        assert "2" in str(xfmr)