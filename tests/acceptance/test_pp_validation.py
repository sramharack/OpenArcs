"""
Acceptance Tests: PandaPower Cross-Validation
=============================================

These tests build identical networks in Arc Flash Studio and
directly in PandaPower, then compare short-circuit results.

This validates that our PandaPower wrapper correctly:
1. Converts component parameters
2. Builds the network
3. Extracts results

Reference:
    - PandaPower has been validated against DIgSILENT PowerFactory
    - PandaPower implements IEC 60909

Traceability:
    - REQ-SYS-QUAL-1: Calculation accuracy validation
"""

import pytest
import math

# PandaPower for direct comparison
import pandapower as pp
import pandapower.shortcircuit as sc

from arc_flash_studio import (
    Network,
    Switchgear, Bus,
    UtilitySource, Transformer, Cable,
)


class TestUtilityOnlyCrossValidation:
    """
    Cross-validate: Utility → Bus → FAULT
    
    Build same network in AFS and PandaPower, compare results.
    """
    
    def test_utility_fault_matches_pandapower(self):
        """AFS fault current matches PandaPower."""
        
        # =========================================================
        # BUILD IN ARC FLASH STUDIO
        # =========================================================
        afs_net = Network()
        afs_net.add_bus(Switchgear(id="MAIN", name="Main", voltage_kv=13.8))
        afs_net.add_utility(UtilitySource(
            id="UTIL", name="Grid", bus_id="MAIN",
            short_circuit_mva=500, x_r_ratio=15
        ))
        
        afs_results = afs_net.calculate_short_circuit()
        afs_ikss = afs_results["MAIN"].ikss_ka
        
        # =========================================================
        # BUILD DIRECTLY IN PANDAPOWER
        # =========================================================
        pp_net = pp.create_empty_network()
        pp_bus = pp.create_bus(pp_net, vn_kv=13.8, name="Main")
        pp.create_ext_grid(
            pp_net, bus=pp_bus, vm_pu=1.0,
            s_sc_max_mva=500, rx_max=1/15,
            x0x_max=1.0, r0x0_max=1.0
        )
        
        sc.calc_sc(pp_net, bus=pp_bus)
        pp_ikss = pp_net.res_bus_sc.at[pp_bus, 'ikss_ka']
        
        # =========================================================
        # COMPARE
        # =========================================================
        # Should match within 0.1% (numerical precision)
        assert afs_ikss == pytest.approx(pp_ikss, rel=0.001), \
            f"AFS={afs_ikss:.4f}, PP={pp_ikss:.4f}"


class TestTransformerCrossValidation:
    """
    Cross-validate: Utility → Transformer → LV Bus → FAULT
    """
    
    def test_transformer_fault_matches_pandapower(self):
        """AFS fault current through transformer matches PandaPower."""
        
        # =========================================================
        # BUILD IN ARC FLASH STUDIO
        # =========================================================
        afs_net = Network()
        afs_net.add_bus(Switchgear(id="HV", name="HV", voltage_kv=13.8))
        afs_net.add_bus(Switchgear(id="LV", name="LV", voltage_kv=0.48))
        afs_net.add_utility(UtilitySource(
            id="UTIL", name="Grid", bus_id="HV",
            short_circuit_mva=500, x_r_ratio=15
        ))
        afs_net.add_transformer(Transformer(
            id="TX", name="Main",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        ))
        
        afs_results = afs_net.calculate_short_circuit()
        afs_ikss = afs_results["LV"].ikss_ka
        
        # =========================================================
        # BUILD DIRECTLY IN PANDAPOWER
        # =========================================================
        pp_net = pp.create_empty_network()
        pp_hv = pp.create_bus(pp_net, vn_kv=13.8, name="HV")
        pp_lv = pp.create_bus(pp_net, vn_kv=0.48, name="LV")
        
        pp.create_ext_grid(
            pp_net, bus=pp_hv, vm_pu=1.0,
            s_sc_max_mva=500, rx_max=1/15,
            x0x_max=1.0, r0x0_max=1.0
        )
        
        # Calculate vkr_percent same way as our Transformer
        vk = 5.75
        xr = 8.0
        vkr = vk / math.sqrt(1 + xr**2)
        
        pp.create_transformer_from_parameters(
            pp_net,
            hv_bus=pp_hv, lv_bus=pp_lv,
            sn_mva=2.0, vn_hv_kv=13.8, vn_lv_kv=0.48,
            vk_percent=vk, vkr_percent=vkr,
            pfe_kw=0, i0_percent=0,
            vector_group="Dyn"
        )
        
        sc.calc_sc(pp_net, bus=pp_lv)
        pp_ikss = pp_net.res_bus_sc.at[pp_lv, 'ikss_ka']
        
        # =========================================================
        # COMPARE
        # =========================================================
        assert afs_ikss == pytest.approx(pp_ikss, rel=0.001), \
            f"AFS={afs_ikss:.4f}, PP={pp_ikss:.4f}"


class TestCableCrossValidation:
    """
    Cross-validate: Utility → Transformer → Cable → Panel → FAULT
    """
    
    def test_cable_fault_matches_pandapower(self):
        """AFS fault current through cable matches PandaPower."""
        
        # =========================================================
        # BUILD IN ARC FLASH STUDIO  
        # =========================================================
        afs_net = Network()
        afs_net.add_bus(Switchgear(id="HV", name="HV", voltage_kv=13.8))
        afs_net.add_bus(Switchgear(id="LV", name="LV", voltage_kv=0.48))
        afs_net.add_bus(Switchgear(id="PANEL", name="Panel", voltage_kv=0.48))
        
        afs_net.add_utility(UtilitySource(
            id="UTIL", name="Grid", bus_id="HV",
            short_circuit_mva=500, x_r_ratio=15
        ))
        afs_net.add_transformer(Transformer(
            id="TX", name="Main",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        ))
        afs_net.add_cable(Cable(
            id="CBL", name="Feeder",
            from_bus_id="LV", to_bus_id="PANEL",
            length_m=30.0,
            r_ohm_per_km=0.105,
            x_ohm_per_km=0.128
        ))
        
        afs_results = afs_net.calculate_short_circuit()
        afs_ikss = afs_results["PANEL"].ikss_ka
        
        # =========================================================
        # BUILD DIRECTLY IN PANDAPOWER
        # =========================================================
        pp_net = pp.create_empty_network()
        pp_hv = pp.create_bus(pp_net, vn_kv=13.8)
        pp_lv = pp.create_bus(pp_net, vn_kv=0.48)
        pp_panel = pp.create_bus(pp_net, vn_kv=0.48)
        
        pp.create_ext_grid(
            pp_net, bus=pp_hv, vm_pu=1.0,
            s_sc_max_mva=500, rx_max=1/15,
            x0x_max=1.0, r0x0_max=1.0
        )
        
        vk = 5.75
        xr = 8.0
        vkr = vk / math.sqrt(1 + xr**2)
        
        pp.create_transformer_from_parameters(
            pp_net,
            hv_bus=pp_hv, lv_bus=pp_lv,
            sn_mva=2.0, vn_hv_kv=13.8, vn_lv_kv=0.48,
            vk_percent=vk, vkr_percent=vkr,
            pfe_kw=0, i0_percent=0,
            vector_group="Dyn"
        )
        
        pp.create_line_from_parameters(
            pp_net,
            from_bus=pp_lv, to_bus=pp_panel,
            length_km=0.030,
            r_ohm_per_km=0.105,
            x_ohm_per_km=0.128,
            c_nf_per_km=0,
            max_i_ka=1.0
        )
        
        sc.calc_sc(pp_net, bus=pp_panel)
        pp_ikss = pp_net.res_bus_sc.at[pp_panel, 'ikss_ka']
        
        # =========================================================
        # COMPARE
        # =========================================================
        assert afs_ikss == pytest.approx(pp_ikss, rel=0.001), \
            f"AFS={afs_ikss:.4f}, PP={pp_ikss:.4f}"


class TestImpedanceConversion:
    """
    Validate that our parameter conversions are correct.
    """
    
    def test_utility_impedance_conversion(self):
        """Utility X/R ratio converts to R/X correctly."""
        util = UtilitySource(
            id="U1", name="Test", bus_id="B1",
            short_circuit_mva=500, x_r_ratio=15
        )
        
        # PandaPower uses rx_max = R/X = 1/(X/R)
        expected_rx = 1.0 / 15.0
        assert util.rx_ratio == pytest.approx(expected_rx, rel=1e-6)
    
    def test_transformer_vkr_conversion(self):
        """Transformer vkr_percent calculated correctly."""
        xfmr = Transformer(
            id="TX", name="Test",
            hv_bus_id="HV", lv_bus_id="LV",
            rated_mva=2.0, hv_kv=13.8, lv_kv=0.48,
            impedance_percent=5.75, x_r_ratio=8.0
        )
        
        # vkr = vk × (R/Z) = vk / sqrt(1 + (X/R)²)
        expected_vkr = 5.75 / math.sqrt(1 + 64)
        assert xfmr.vkr_percent == pytest.approx(expected_vkr, rel=1e-6)
    
    def test_cable_length_conversion(self):
        """Cable length converts m to km correctly."""
        cable = Cable(
            id="C1", name="Test",
            from_bus_id="B1", to_bus_id="B2",
            length_m=30.0,
            r_ohm_per_km=0.1, x_ohm_per_km=0.1
        )
        
        assert cable.length_km == pytest.approx(0.030, rel=1e-6)