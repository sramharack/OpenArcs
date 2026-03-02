"""
IEEE 1584-2018 Annex D.1 Validation Tests
=========================================

Validates calculations against the worked example in Annex D.1 (4160V MV Example).

Reference: IEEE 1584-2018, Annex D.1, pages 58-62

Test Case Inputs (D.1-D.7):
    - Ibf = 15 kA (bolted fault current)
    - Voc = 4.16 kV (open circuit voltage)
    - Gap = 104 mm
    - Working distance = 914.4 mm (36")
    - Arc duration = 197 ms
    - Enclosure: 762mm W × 1143mm H
    - Configuration: VCB

Status:
    ✅ Step 1: Intermediate arcing currents (Equations D.8-D.14)
    ✅ Step 2: Final arcing current interpolation (Equations D.15-D.17)  
    ✅ Step 3: Enclosure size correction factor (Equations D.20-D.23)
    🔲 Step 4: Incident energy (Equations D.24-D.34) - TODO
    🔲 Step 5: Arc flash boundary (Equations D.35-D.42) - TODO
"""

import pytest
import math

from arc_flash_studio.calculations.ieee_1584_2018 import (
    ElectrodeConfig,
    equation_1_intermediate_arcing_current,
    equations_16_17_18_mv_interpolation,
    equation_13_equivalent_enclosure_size,
    calculate_arcing_current,
)


# =============================================================================
# Test Case Constants from Annex D.1
# =============================================================================

# Inputs (D.1-D.7)
ANNEX_D1_IBF_KA = 15.0          # Bolted fault current (kA)
ANNEX_D1_VOC_KV = 4.16          # Open circuit voltage (kV)
ANNEX_D1_GAP_MM = 104.0         # Gap between electrodes (mm)
ANNEX_D1_DISTANCE_MM = 914.4    # Working distance (mm) = 36"
ANNEX_D1_DURATION_MS = 197.0    # Arc duration (ms)
ANNEX_D1_ENC_WIDTH_MM = 762.0   # Enclosure width (mm)
ANNEX_D1_ENC_HEIGHT_MM = 1143.0 # Enclosure height (mm)
ANNEX_D1_CONFIG = ElectrodeConfig.VCB

# Expected intermediate arcing currents (D.8-D.14)
EXPECTED_IARC_600 = 11.117      # kA (D.9)
EXPECTED_IARC_2700 = 12.816     # kA (D.12)
EXPECTED_IARC_14300 = 14.116    # kA (D.14)

# Expected final arcing current (D.15-D.17)
EXPECTED_IARC_FINAL = 12.979    # kA (D.17)

# Expected enclosure correction (D.20-D.23) - all in mm
EXPECTED_ADJ_WIDTH_MM = 701.85  # mm (D.20) - 27.632 inches × 25.4
EXPECTED_ADJ_HEIGHT_MM = 1143.0 # mm (D.21) - height unchanged for VCB
EXPECTED_EES_MM = 922.43        # mm (D.22) - 36.316 inches × 25.4
EXPECTED_CF = 1.284             # dimensionless (D.23)

# Expected incident energy (D.24-D.34) - TODO
EXPECTED_E_600 = 8.652          # J/cm² (D.24)
EXPECTED_E_2700 = 11.977        # J/cm² (D.26)
EXPECTED_E_14300 = 13.367       # J/cm² (D.28)
EXPECTED_E_FINAL = 12.152       # J/cm² (D.34)


class TestAnnexD1IntermediateArcingCurrent:
    """
    Step 1: Intermediate Arcing Current Calculations
    
    Reference: IEEE 1584-2018, Annex D.1, Equations D.8-D.14
    """
    
    def test_iarc_600v(self):
        """D.8-D.9: Intermediate arcing current at 600V reference."""
        iarc_600 = equation_1_intermediate_arcing_current(
            ibf_ka=ANNEX_D1_IBF_KA,
            gap_mm=ANNEX_D1_GAP_MM,
            config=ANNEX_D1_CONFIG,
            voltage_ref=600
        )
        assert iarc_600 == pytest.approx(EXPECTED_IARC_600, rel=0.01), \
            f"Iarc_600 = {iarc_600:.3f} kA, expected {EXPECTED_IARC_600} kA"
    
    def test_iarc_2700v(self):
        """D.10-D.12: Intermediate arcing current at 2700V reference."""
        iarc_2700 = equation_1_intermediate_arcing_current(
            ibf_ka=ANNEX_D1_IBF_KA,
            gap_mm=ANNEX_D1_GAP_MM,
            config=ANNEX_D1_CONFIG,
            voltage_ref=2700
        )
        assert iarc_2700 == pytest.approx(EXPECTED_IARC_2700, rel=0.01), \
            f"Iarc_2700 = {iarc_2700:.3f} kA, expected {EXPECTED_IARC_2700} kA"
    
    def test_iarc_14300v(self):
        """D.13-D.14: Intermediate arcing current at 14300V reference."""
        iarc_14300 = equation_1_intermediate_arcing_current(
            ibf_ka=ANNEX_D1_IBF_KA,
            gap_mm=ANNEX_D1_GAP_MM,
            config=ANNEX_D1_CONFIG,
            voltage_ref=14300
        )
        assert iarc_14300 == pytest.approx(EXPECTED_IARC_14300, rel=0.01), \
            f"Iarc_14300 = {iarc_14300:.3f} kA, expected {EXPECTED_IARC_14300} kA"


class TestAnnexD1FinalArcingCurrent:
    """
    Step 2: Final Arcing Current Interpolation
    
    Reference: IEEE 1584-2018, Annex D.1, Equations D.15-D.17
    """
    
    def test_final_arcing_current_interpolation(self):
        """D.15-D.17: Final arcing current via interpolation."""
        # First get intermediate values
        iarc_600 = equation_1_intermediate_arcing_current(
            ANNEX_D1_IBF_KA, ANNEX_D1_GAP_MM, ANNEX_D1_CONFIG, 600
        )
        iarc_2700 = equation_1_intermediate_arcing_current(
            ANNEX_D1_IBF_KA, ANNEX_D1_GAP_MM, ANNEX_D1_CONFIG, 2700
        )
        iarc_14300 = equation_1_intermediate_arcing_current(
            ANNEX_D1_IBF_KA, ANNEX_D1_GAP_MM, ANNEX_D1_CONFIG, 14300
        )
        
        # Interpolate
        iarc_final = equations_16_17_18_mv_interpolation(
            iarc_600, iarc_2700, iarc_14300, ANNEX_D1_VOC_KV
        )
        
        assert iarc_final == pytest.approx(EXPECTED_IARC_FINAL, rel=0.01), \
            f"Iarc_final = {iarc_final:.3f} kA, expected {EXPECTED_IARC_FINAL} kA"
    
    def test_voltage_above_2700v_uses_iarc_2(self):
        """When Voc > 2.7 kV, final Iarc should use Iarc_2 (Eq 17)."""
        iarc_600 = equation_1_intermediate_arcing_current(
            ANNEX_D1_IBF_KA, ANNEX_D1_GAP_MM, ANNEX_D1_CONFIG, 600
        )
        iarc_2700 = equation_1_intermediate_arcing_current(
            ANNEX_D1_IBF_KA, ANNEX_D1_GAP_MM, ANNEX_D1_CONFIG, 2700
        )
        iarc_14300 = equation_1_intermediate_arcing_current(
            ANNEX_D1_IBF_KA, ANNEX_D1_GAP_MM, ANNEX_D1_CONFIG, 14300
        )
        
        # Calculate Iarc_2 directly (Equation 17)
        iarc_2 = ((iarc_14300 - iarc_2700) / 11.6) * (ANNEX_D1_VOC_KV - 14.3) + iarc_14300
        
        iarc_final = equations_16_17_18_mv_interpolation(
            iarc_600, iarc_2700, iarc_14300, ANNEX_D1_VOC_KV
        )
        
        # Since Voc > 2.7, final should equal Iarc_2
        assert iarc_final == pytest.approx(iarc_2, rel=0.001)


class TestAnnexD1EnclosureCorrection:
    """
    Step 3: Enclosure Size Correction Factor
    
    Reference: IEEE 1584-2018, Annex D.1, Equations D.20-D.23
    """
    
    def test_equivalent_enclosure_size(self):
        """D.20-D.22: Calculate equivalent enclosure size (EES)."""
        ees = equation_13_equivalent_enclosure_size(
            height_mm=ANNEX_D1_ENC_HEIGHT_MM,
            width_mm=ANNEX_D1_ENC_WIDTH_MM,
            voc_kv=ANNEX_D1_VOC_KV,
            config=ANNEX_D1_CONFIG
        )
        
        assert ees == pytest.approx(EXPECTED_EES_MM, rel=0.01), \
            f"EES = {ees:.3f} mm, expected {EXPECTED_EES_MM} mm"
    
    def test_adjusted_width_calculation(self):
        """D.20: Verify adjusted width calculation for width > 660.4mm."""
        # Width = 762mm > 660.4mm, so Equation 11 applies
        # Width1 = 660.4 + (Width - 660.4) × ((Voc + A)/B)
        # For VCB: A = 4, B = 20
        A, B = 4.0, 20.0
        width_mm = ANNEX_D1_ENC_WIDTH_MM
        voc_kv = ANNEX_D1_VOC_KV
        
        adj_width_mm = 660.4 + (width_mm - 660.4) * ((voc_kv + A) / B)
        
        assert adj_width_mm == pytest.approx(EXPECTED_ADJ_WIDTH_MM, rel=0.01), \
            f"Adjusted width = {adj_width_mm:.3f} mm, expected {EXPECTED_ADJ_WIDTH_MM} mm"
    
    def test_adjusted_height_for_vcb(self):
        """D.21: For VCB with height > 660.4mm, use actual dimension."""
        # Per Table 6, VCB height > 660.4mm uses actual dimension
        adj_height_mm = ANNEX_D1_ENC_HEIGHT_MM
        
        assert adj_height_mm == pytest.approx(EXPECTED_ADJ_HEIGHT_MM, rel=0.01), \
            f"Adjusted height = {adj_height_mm:.3f} mm, expected {EXPECTED_ADJ_HEIGHT_MM} mm"


class TestAnnexD1IncidentEnergy:
    """
    Step 4: Incident Energy Calculations
    
    Reference: IEEE 1584-2018, Annex D.1, Equations D.24-D.34
    
    STATUS: TODO - Energy equation not yet validated
    """
    
    @pytest.mark.skip(reason="Incident energy equation not yet validated")
    def test_incident_energy_600v(self):
        """D.24: Intermediate incident energy at 600V."""
        pass
    
    @pytest.mark.skip(reason="Incident energy equation not yet validated")
    def test_incident_energy_2700v(self):
        """D.26: Intermediate incident energy at 2700V."""
        pass
    
    @pytest.mark.skip(reason="Incident energy equation not yet validated")
    def test_incident_energy_final(self):
        """D.34: Final interpolated incident energy."""
        pass


class TestAnnexD1ArcFlashBoundary:
    """
    Step 5: Arc Flash Boundary Calculations
    
    Reference: IEEE 1584-2018, Annex D.1, Equations D.35-D.42
    
    STATUS: TODO
    """
    
    @pytest.mark.skip(reason="Arc flash boundary not yet validated")
    def test_arc_flash_boundary(self):
        """D.42: Final arc flash boundary."""
        pass


# =============================================================================
# Integration Test
# =============================================================================

class TestAnnexD1Integration:
    """Full calculation pipeline test."""
    
    def test_arcing_current_full_pipeline(self):
        """Test complete arcing current calculation matches Annex D.1."""
        result = calculate_arcing_current(
            ibf_ka=ANNEX_D1_IBF_KA,
            voc_kv=ANNEX_D1_VOC_KV,
            gap_mm=ANNEX_D1_GAP_MM,
            config=ANNEX_D1_CONFIG
        )
        
        # Check intermediate values
        assert result.iarc_600 == pytest.approx(EXPECTED_IARC_600, rel=0.01)
        assert result.iarc_2700 == pytest.approx(EXPECTED_IARC_2700, rel=0.01)
        assert result.iarc_14300 == pytest.approx(EXPECTED_IARC_14300, rel=0.01)
        
        # Check final value
        assert result.iarc == pytest.approx(EXPECTED_IARC_FINAL, rel=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])