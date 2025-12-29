"""
Unit Tests for Enumeration Types
================================

Tests for VoltageLevel, ElectrodeConfig, and EquipmentType enums.

Traceability:
    - REQ-ARC-VAL-33: Electrode configuration validation
"""

import pytest
from arc_flash_studio.components.enums import (
    VoltageLevel,
    ElectrodeConfig,
    EquipmentType,
)


class TestVoltageLevel:
    """Tests for VoltageLevel enum."""
    
    def test_voltage_level_values(self):
        """VoltageLevel has correct string values."""
        assert VoltageLevel.LV.value == "LV"
        assert VoltageLevel.MV.value == "MV"
        assert VoltageLevel.HV.value == "HV"
    
    def test_voltage_level_string_enum(self):
        """VoltageLevel can be compared to strings."""
        assert VoltageLevel.LV == "LV"
        assert VoltageLevel.MV == "MV"
        assert VoltageLevel.HV == "HV"
    
    def test_voltage_level_from_string(self):
        """VoltageLevel can be created from string."""
        assert VoltageLevel("LV") == VoltageLevel.LV
        assert VoltageLevel("MV") == VoltageLevel.MV


class TestElectrodeConfig:
    """Tests for ElectrodeConfig enum."""
    
    def test_all_configs_exist(self):
        """All five IEEE 1584-2018 configurations exist."""
        configs = [e.value for e in ElectrodeConfig]
        assert "VCB" in configs
        assert "VCBB" in configs
        assert "HCB" in configs
        assert "VOA" in configs
        assert "HOA" in configs
    
    def test_config_count(self):
        """Exactly five configurations defined."""
        assert len(ElectrodeConfig) == 5
    
    def test_config_string_enum(self):
        """ElectrodeConfig is a string enum."""
        assert ElectrodeConfig.VCB == "VCB"
        assert isinstance(ElectrodeConfig.VCB.value, str)


class TestEquipmentType:
    """Tests for EquipmentType enum."""
    
    def test_all_types_exist(self):
        """All equipment types exist."""
        types = [e.value for e in EquipmentType]
        assert "switchgear" in types
        assert "mcc" in types
        assert "panelboard" in types
        assert "cable_junction" in types
        assert "open_air" in types
        assert "other" in types
    
    def test_type_count(self):
        """Six equipment types defined."""
        assert len(EquipmentType) == 6