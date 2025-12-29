"""
Unit Tests for Default Parameters
=================================

Tests that IEEE 1584-2018 Table 8, Table 3, and Table 9 defaults
are correctly implemented.

References:
    - IEEE 1584-2018, Table 3: Working distances
    - IEEE 1584-2018, Table 8: Typical gaps
    - IEEE 1584-2018, Table 9: Enclosure sizes

Traceability:
    - REQ-ARC-DATA-1: Default gap distances
    - REQ-ARC-DATA-2: Default working distances
    - REQ-ARC-DATA-3: Default enclosure sizes
"""

import pytest
from arc_flash_studio.components.enums import EquipmentType, VoltageLevel
from arc_flash_studio.components.defaults import (
    DEFAULT_GAPS_MM,
    DEFAULT_WORKING_DISTANCE_MM,
    DEFAULT_ENCLOSURE_SIZES_MM,
    get_default_gap_mm,
    get_default_working_distance_mm,
    get_default_enclosure_size_mm,
)


class TestDefaultGaps:
    """Tests for default gap distances from IEEE 1584-2018 Table 8."""
    
    def test_lv_switchgear_gap(self):
        """LV switchgear: 32mm gap."""
        gap = get_default_gap_mm(EquipmentType.SWITCHGEAR, VoltageLevel.LV)
        assert gap == 32.0
    
    def test_mv_switchgear_gap(self):
        """MV switchgear: 104mm gap."""
        gap = get_default_gap_mm(EquipmentType.SWITCHGEAR, VoltageLevel.MV)
        assert gap == 104.0
    
    def test_mcc_gap(self):
        """MCC: 25mm gap."""
        gap = get_default_gap_mm(EquipmentType.MCC, VoltageLevel.LV)
        assert gap == 25.0
    
    def test_panelboard_gap(self):
        """Panelboard: 25mm gap."""
        gap = get_default_gap_mm(EquipmentType.PANELBOARD, VoltageLevel.LV)
        assert gap == 25.0
    
    def test_cable_junction_gap(self):
        """Cable junction: 13mm gap."""
        gap = get_default_gap_mm(EquipmentType.CABLE_JUNCTION, VoltageLevel.LV)
        assert gap == 13.0
    
    def test_fallback_gap(self):
        """Unknown combination returns fallback."""
        # HV switchgear not defined - should return fallback
        gap = get_default_gap_mm(EquipmentType.SWITCHGEAR, VoltageLevel.HV)
        assert gap == 32.0  # fallback


class TestDefaultWorkingDistances:
    """Tests for default working distances from IEEE 1584-2018 Table 3."""
    
    def test_switchgear_working_distance(self):
        """Switchgear: 610mm (24 inches)."""
        wd = get_default_working_distance_mm(EquipmentType.SWITCHGEAR)
        assert wd == 610.0
    
    def test_mcc_working_distance(self):
        """MCC: 455mm (18 inches)."""
        wd = get_default_working_distance_mm(EquipmentType.MCC)
        assert wd == 455.0
    
    def test_panelboard_working_distance(self):
        """Panelboard: 455mm (18 inches)."""
        wd = get_default_working_distance_mm(EquipmentType.PANELBOARD)
        assert wd == 455.0
    
    def test_other_working_distance(self):
        """Other/generic: 455mm (18 inches)."""
        wd = get_default_working_distance_mm(EquipmentType.OTHER)
        assert wd == 455.0


class TestDefaultEnclosureSizes:
    """Tests for default enclosure sizes from IEEE 1584-2018 Table 9."""
    
    def test_switchgear_enclosure(self):
        """Switchgear: 914mm cube (36 inches)."""
        h, w, d = get_default_enclosure_size_mm(EquipmentType.SWITCHGEAR)
        assert h == 914.0
        assert w == 914.0
        assert d == 914.0
    
    def test_mcc_enclosure(self):
        """MCC: 660mm cube (26 inches)."""
        h, w, d = get_default_enclosure_size_mm(EquipmentType.MCC)
        assert h == 660.0
        assert w == 660.0
        assert d == 660.0
    
    def test_panelboard_enclosure(self):
        """Panelboard: 508x508x254mm (20x20x10 inches)."""
        h, w, d = get_default_enclosure_size_mm(EquipmentType.PANELBOARD)
        assert h == 508.0
        assert w == 508.0
        assert d == 254.0
    
    def test_cable_junction_enclosure(self):
        """Cable junction: 305x305x203mm (12x12x8 inches)."""
        h, w, d = get_default_enclosure_size_mm(EquipmentType.CABLE_JUNCTION)
        assert h == 305.0
        assert w == 305.0
        assert d == 203.0


class TestDefaultsDataIntegrity:
    """Tests for data integrity of defaults tables."""
    
    def test_all_equipment_types_have_working_distance(self):
        """Every equipment type has a working distance."""
        for eq_type in EquipmentType:
            wd = get_default_working_distance_mm(eq_type)
            assert wd > 0, f"{eq_type} missing working distance"
    
    def test_enclosure_dimensions_positive(self):
        """All enclosure dimensions are positive."""
        for eq_type in EquipmentType:
            if eq_type != EquipmentType.OPEN_AIR:  # Open air has no enclosure
                h, w, d = get_default_enclosure_size_mm(eq_type)
                assert h > 0, f"{eq_type} height not positive"
                assert w > 0, f"{eq_type} width not positive"
                assert d > 0, f"{eq_type} depth not positive"