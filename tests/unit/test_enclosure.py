"""
Unit Tests for EnclosureInfo
============================

Tests for the EnclosureInfo Pydantic model.

Traceability:
    - REQ-ARC-CALC-25: Enclosure size correction factor
"""

import pytest
from arc_flash_studio.components.enclosure import EnclosureInfo
from arc_flash_studio.components.enums import ElectrodeConfig


class TestEnclosureCreation:
    """Tests for creating EnclosureInfo instances."""
    
    def test_create_valid_enclosure(self):
        """Create enclosure with valid dimensions."""
        enc = EnclosureInfo(
            height_mm=914,
            width_mm=914,
            depth_mm=914,
            electrode_config=ElectrodeConfig.VCB
        )
        assert enc.height_mm == 914
        assert enc.width_mm == 914
        assert enc.depth_mm == 914
        assert enc.electrode_config == ElectrodeConfig.VCB
    
    def test_default_electrode_config(self):
        """Default electrode config is VCB."""
        enc = EnclosureInfo(height_mm=500, width_mm=500, depth_mm=500)
        assert enc.electrode_config == ElectrodeConfig.VCB


class TestEnclosureValidation:
    """Tests for EnclosureInfo validation."""
    
    def test_negative_height_raises_error(self):
        """Negative height raises validation error."""
        with pytest.raises(ValueError):
            EnclosureInfo(height_mm=-100, width_mm=500, depth_mm=500)
    
    def test_zero_width_raises_error(self):
        """Zero width raises validation error."""
        with pytest.raises(ValueError):
            EnclosureInfo(height_mm=500, width_mm=0, depth_mm=500)
    
    def test_negative_depth_raises_error(self):
        """Negative depth raises validation error."""
        with pytest.raises(ValueError):
            EnclosureInfo(height_mm=500, width_mm=500, depth_mm=-100)


class TestEnclosureConversions:
    """Tests for unit conversion computed fields."""
    
    def test_height_inches_conversion(self):
        """Height converts to inches correctly."""
        enc = EnclosureInfo(height_mm=508, width_mm=500, depth_mm=500)
        assert enc.height_in == pytest.approx(20.0, rel=0.01)
    
    def test_width_inches_conversion(self):
        """Width converts to inches correctly."""
        enc = EnclosureInfo(height_mm=500, width_mm=914.4, depth_mm=500)
        assert enc.width_in == pytest.approx(36.0, rel=0.01)
    
    def test_depth_inches_conversion(self):
        """Depth converts to inches correctly."""
        enc = EnclosureInfo(height_mm=500, width_mm=500, depth_mm=254)
        assert enc.depth_in == pytest.approx(10.0, rel=0.01)


class TestEnclosureStringRepresentation:
    """Tests for string representation."""
    
    def test_str_contains_dimensions(self):
        """String contains dimensions."""
        enc = EnclosureInfo(height_mm=500, width_mm=600, depth_mm=700)
        s = str(enc)
        assert "500" in s
        assert "600" in s
        assert "700" in s
    
    def test_str_contains_config(self):
        """String contains electrode config."""
        enc = EnclosureInfo(
            height_mm=500, width_mm=500, depth_mm=500,
            electrode_config=ElectrodeConfig.HCB
        )
        assert "HCB" in str(enc)


class TestEnclosureSerialization:
    """Tests for JSON serialization."""
    
    def test_export_to_dict(self):
        """Enclosure exports to dictionary."""
        enc = EnclosureInfo(height_mm=500, width_mm=500, depth_mm=500)
        data = enc.model_dump()
        assert data["height_mm"] == 500
        assert data["width_mm"] == 500
        assert data["depth_mm"] == 500
    
    def test_import_from_dict(self):
        """Enclosure imports from dictionary."""
        data = {
            "height_mm": 600,
            "width_mm": 700,
            "depth_mm": 800,
            "electrode_config": "VCBB"
        }
        enc = EnclosureInfo(**data)
        assert enc.height_mm == 600
        assert enc.electrode_config == ElectrodeConfig.VCBB