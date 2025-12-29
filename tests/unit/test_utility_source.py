"""
Unit Tests for UtilitySource
============================

Tests for the UtilitySource component (grid connection).

Traceability:
    - REQ-COMP-FUNC-7: Utility source with short-circuit parameters
"""

import pytest
from arc_flash_studio.components import UtilitySource


class TestUtilitySourceCreation:
    """Tests for creating UtilitySource instances."""
    
    def test_create_utility_source(self):
        """Create a valid utility source."""
        util = UtilitySource(
            id="UTIL-1",
            name="Grid Connection",
            bus_id="MAIN-BUS",
            short_circuit_mva=500,
            x_r_ratio=15
        )
        assert util.id == "UTIL-1"
        assert util.name == "Grid Connection"
        assert util.bus_id == "MAIN-BUS"
        assert util.short_circuit_mva == 500
        assert util.x_r_ratio == 15


class TestUtilitySourceValidation:
    """Tests for UtilitySource validation."""
    
    def test_empty_id_raises_error(self):
        """Empty ID raises validation error."""
        with pytest.raises(ValueError):
            UtilitySource(
                id="", name="Test", bus_id="B1",
                short_circuit_mva=500, x_r_ratio=15
            )
    
    def test_negative_mva_raises_error(self):
        """Negative short-circuit MVA raises error."""
        with pytest.raises(ValueError):
            UtilitySource(
                id="U1", name="Test", bus_id="B1",
                short_circuit_mva=-500, x_r_ratio=15
            )
    
    def test_zero_mva_raises_error(self):
        """Zero short-circuit MVA raises error."""
        with pytest.raises(ValueError):
            UtilitySource(
                id="U1", name="Test", bus_id="B1",
                short_circuit_mva=0, x_r_ratio=15
            )
    
    def test_xr_ratio_below_min_raises_error(self):
        """X/R ratio below 1 raises error."""
        with pytest.raises(ValueError):
            UtilitySource(
                id="U1", name="Test", bus_id="B1",
                short_circuit_mva=500, x_r_ratio=0.5
            )
    
    def test_xr_ratio_above_max_raises_error(self):
        """X/R ratio above 100 raises error."""
        with pytest.raises(ValueError):
            UtilitySource(
                id="U1", name="Test", bus_id="B1",
                short_circuit_mva=500, x_r_ratio=150
            )


class TestUtilitySourceConversions:
    """Tests for computed fields."""
    
    def test_rx_ratio_calculation(self):
        """R/X ratio is reciprocal of X/R ratio."""
        util = UtilitySource(
            id="U1", name="Test", bus_id="B1",
            short_circuit_mva=500, x_r_ratio=15
        )
        expected_rx = 1.0 / 15.0
        assert util.rx_ratio == pytest.approx(expected_rx, rel=1e-6)
    
    def test_rx_ratio_with_different_xr(self):
        """R/X calculation with different X/R values."""
        util = UtilitySource(
            id="U1", name="Test", bus_id="B1",
            short_circuit_mva=500, x_r_ratio=10
        )
        assert util.rx_ratio == pytest.approx(0.1, rel=1e-6)


class TestUtilitySourceSerialization:
    """Tests for JSON serialization."""
    
    def test_export_to_dict(self):
        """UtilitySource exports to dictionary."""
        util = UtilitySource(
            id="U1", name="Test", bus_id="B1",
            short_circuit_mva=500, x_r_ratio=15
        )
        data = util.model_dump()
        assert data["id"] == "U1"
        assert data["short_circuit_mva"] == 500
        assert data["x_r_ratio"] == 15
    
    def test_import_from_dict(self):
        """UtilitySource imports from dictionary."""
        data = {
            "id": "U2",
            "name": "Grid",
            "bus_id": "B1",
            "short_circuit_mva": 750,
            "x_r_ratio": 20
        }
        util = UtilitySource(**data)
        assert util.short_circuit_mva == 750
        assert util.x_r_ratio == 20


class TestUtilitySourceStr:
    """Tests for string representation."""
    
    def test_str_contains_id(self):
        """String contains ID."""
        util = UtilitySource(
            id="UTIL-1", name="Grid", bus_id="B1",
            short_circuit_mva=500, x_r_ratio=15
        )
        assert "UTIL-1" in str(util)
    
    def test_str_contains_mva(self):
        """String contains MVA."""
        util = UtilitySource(
            id="U1", name="Grid", bus_id="B1",
            short_circuit_mva=500, x_r_ratio=15
        )
        assert "500" in str(util)