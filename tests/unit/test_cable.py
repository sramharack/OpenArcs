"""
Unit Tests for Cable
====================

Tests for the Cable component and create_cable helper.

Traceability:
    - REQ-COMP-FUNC-9: Cable with impedance parameters
    - REQ-COMP-DATA-4: Cable lookup table from NEC Table 9
"""

import pytest
from arc_flash_studio.components import Cable, create_cable, CABLE_DATA


class TestCableCreation:
    """Tests for creating Cable instances."""
    
    def test_create_cable(self):
        """Create a valid cable with explicit parameters."""
        cable = Cable(
            id="C1",
            name="Feeder",
            from_bus_id="B1",
            to_bus_id="B2",
            length_m=30.0,
            r_ohm_per_km=0.105,
            x_ohm_per_km=0.128
        )
        assert cable.id == "C1"
        assert cable.length_m == 30.0
        assert cable.r_ohm_per_km == 0.105
        assert cable.x_ohm_per_km == 0.128
    
    def test_optional_ampacity(self):
        """Ampacity is optional."""
        cable = Cable(
            id="C1", name="Test",
            from_bus_id="B1", to_bus_id="B2",
            length_m=30.0, r_ohm_per_km=0.1, x_ohm_per_km=0.1,
            ampacity_a=400
        )
        assert cable.ampacity_a == 400
    
    def test_optional_conductor_size(self):
        """Conductor size is optional."""
        cable = Cable(
            id="C1", name="Test",
            from_bus_id="B1", to_bus_id="B2",
            length_m=30.0, r_ohm_per_km=0.1, x_ohm_per_km=0.1,
            conductor_size="500 kcmil"
        )
        assert cable.conductor_size == "500 kcmil"


class TestCableValidation:
    """Tests for Cable validation."""
    
    def test_empty_id_raises_error(self):
        """Empty ID raises validation error."""
        with pytest.raises(ValueError):
            Cable(
                id="", name="Test",
                from_bus_id="B1", to_bus_id="B2",
                length_m=30.0, r_ohm_per_km=0.1, x_ohm_per_km=0.1
            )
    
    def test_negative_length_raises_error(self):
        """Negative length raises validation error."""
        with pytest.raises(ValueError):
            Cable(
                id="C1", name="Test",
                from_bus_id="B1", to_bus_id="B2",
                length_m=-30.0, r_ohm_per_km=0.1, x_ohm_per_km=0.1
            )
    
    def test_zero_length_raises_error(self):
        """Zero length raises validation error."""
        with pytest.raises(ValueError):
            Cable(
                id="C1", name="Test",
                from_bus_id="B1", to_bus_id="B2",
                length_m=0, r_ohm_per_km=0.1, x_ohm_per_km=0.1
            )
    
    def test_negative_resistance_raises_error(self):
        """Negative resistance raises validation error."""
        with pytest.raises(ValueError):
            Cable(
                id="C1", name="Test",
                from_bus_id="B1", to_bus_id="B2",
                length_m=30.0, r_ohm_per_km=-0.1, x_ohm_per_km=0.1
            )


class TestCableCalculations:
    """Tests for computed fields."""
    
    def test_length_km_conversion(self):
        """Length converts to kilometers correctly."""
        cable = Cable(
            id="C1", name="Test",
            from_bus_id="B1", to_bus_id="B2",
            length_m=100.0, r_ohm_per_km=0.1, x_ohm_per_km=0.1
        )
        assert cable.length_km == pytest.approx(0.1, rel=1e-6)
    
    def test_total_resistance(self):
        """Total resistance = R/km × length_km."""
        cable = Cable(
            id="C1", name="Test",
            from_bus_id="B1", to_bus_id="B2",
            length_m=100.0, r_ohm_per_km=0.2, x_ohm_per_km=0.1
        )
        # 0.2 Ω/km × 0.1 km = 0.02 Ω
        assert cable.r_ohms == pytest.approx(0.02, rel=1e-6)
    
    def test_total_reactance(self):
        """Total reactance = X/km × length_km."""
        cable = Cable(
            id="C1", name="Test",
            from_bus_id="B1", to_bus_id="B2",
            length_m=50.0, r_ohm_per_km=0.1, x_ohm_per_km=0.15
        )
        # 0.15 Ω/km × 0.05 km = 0.0075 Ω
        assert cable.x_ohms == pytest.approx(0.0075, rel=1e-6)


class TestCreateCableHelper:
    """Tests for create_cable() helper function."""
    
    def test_create_cable_from_size(self):
        """Create cable using conductor size lookup."""
        cable = create_cable(
            id="C1", name="Test",
            from_bus_id="B1", to_bus_id="B2",
            length_m=30.0, conductor_size="500 kcmil"
        )
        assert cable.r_ohm_per_km == 0.105
        assert cable.x_ohm_per_km == 0.128
        assert cable.ampacity_a == 380
        assert cable.conductor_size == "500 kcmil"
    
    def test_create_cable_unknown_size_raises_error(self):
        """Unknown conductor size raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            create_cable(
                id="C1", name="Test",
                from_bus_id="B1", to_bus_id="B2",
                length_m=30.0, conductor_size="999 kcmil"
            )
        assert "999 kcmil" in str(exc_info.value)
    
    def test_create_cable_various_sizes(self):
        """Various conductor sizes produce correct values."""
        # 4/0 AWG
        cable_4_0 = create_cable(
            id="C1", name="Test",
            from_bus_id="B1", to_bus_id="B2",
            length_m=10.0, conductor_size="4/0 AWG"
        )
        assert cable_4_0.r_ohm_per_km == 0.220
        assert cable_4_0.ampacity_a == 230
        
        # 12 AWG
        cable_12 = create_cable(
            id="C2", name="Test",
            from_bus_id="B1", to_bus_id="B2",
            length_m=10.0, conductor_size="12 AWG"
        )
        assert cable_12.r_ohm_per_km == 6.56
        assert cable_12.ampacity_a == 20


class TestCableData:
    """Tests for CABLE_DATA lookup table."""
    
    def test_cable_data_has_standard_sizes(self):
        """CABLE_DATA contains standard AWG and kcmil sizes."""
        assert "14 AWG" in CABLE_DATA
        assert "12 AWG" in CABLE_DATA
        assert "4/0 AWG" in CABLE_DATA
        assert "500 kcmil" in CABLE_DATA
        assert "750 kcmil" in CABLE_DATA
    
    def test_cable_data_values_positive(self):
        """All CABLE_DATA values are positive."""
        for size, (r, x, amp) in CABLE_DATA.items():
            assert r > 0, f"{size} resistance not positive"
            assert x > 0, f"{size} reactance not positive"
            assert amp > 0, f"{size} ampacity not positive"
    
    def test_cable_data_resistance_decreases_with_size(self):
        """Resistance decreases as conductor size increases."""
        r_14 = CABLE_DATA["14 AWG"][0]
        r_12 = CABLE_DATA["12 AWG"][0]
        r_4_0 = CABLE_DATA["4/0 AWG"][0]
        r_500 = CABLE_DATA["500 kcmil"][0]
        
        assert r_14 > r_12 > r_4_0 > r_500


class TestCableSerialization:
    """Tests for JSON serialization."""
    
    def test_export_to_dict(self):
        """Cable exports to dictionary."""
        cable = Cable(
            id="C1", name="Feeder",
            from_bus_id="B1", to_bus_id="B2",
            length_m=30.0, r_ohm_per_km=0.105, x_ohm_per_km=0.128
        )
        data = cable.model_dump()
        assert data["id"] == "C1"
        assert data["length_m"] == 30.0
    
    def test_import_from_dict(self):
        """Cable imports from dictionary."""
        data = {
            "id": "C2",
            "name": "Branch",
            "from_bus_id": "B1",
            "to_bus_id": "B2",
            "length_m": 50.0,
            "r_ohm_per_km": 0.2,
            "x_ohm_per_km": 0.15
        }
        cable = Cable(**data)
        assert cable.length_m == 50.0