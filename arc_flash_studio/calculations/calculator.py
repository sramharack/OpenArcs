"""
IEEE 1584-2018 Arc Flash Calculator
===================================

Main orchestration module that combines all calculation modules.

Usage:
    from arc_flash_studio.ieee1584 import calculate_arc_flash, ElectrodeConfig
    
    result = calculate_arc_flash(
        ibf_ka=30.0,
        voc_kv=13.8,
        gap_mm=152.0,
        working_distance_mm=914.4,
        arc_duration_ms=100.0,
        height_mm=660.4,
        width_mm=660.4,
        depth_mm=660.4,
        config=ElectrodeConfig.VCB
    )
    
    print(f"Incident Energy: {result.incident_energy_cal_cm2:.1f} cal/cm²")
    print(f"Arc Flash Boundary: {result.afb_inches:.0f} inches")

Reference: IEEE 1584-2018
"""

from dataclasses import dataclass
from typing import Optional

from .constants import ElectrodeConfig, JOULES_PER_CAL, INCHES_TO_MM
from .arcing_current import calculate_arcing_current, ArcingCurrentResult
from .enclosure import calculate_correction_factor
from .incident_energy import calculate_incident_energy
from .arc_flash_boundary import calculate_arc_flash_boundary


@dataclass
class ArcFlashResult:
    """Complete arc flash calculation results."""
    
    # Input parameters
    ibf_ka: float
    voc_kv: float
    gap_mm: float
    working_distance_mm: float
    arc_duration_ms: float
    electrode_config: ElectrodeConfig
    
    # Enclosure parameters
    height_mm: float
    width_mm: float
    depth_mm: float
    
    # Arcing current results
    iarc_600_ka: float
    iarc_2700_ka: float
    iarc_14300_ka: float
    iarc_ka: float
    iarc_min_ka: float
    variation_factor: float
    
    # Enclosure correction results
    correction_factor: float
    ees_inches: float
    is_shallow_enclosure: bool
    
    # Incident energy results (using normal arcing current)
    incident_energy_j_cm2: float
    incident_energy_cal_cm2: float
    
    # Arc flash boundary results (using normal arcing current)
    afb_mm: float
    afb_inches: float
    
    # Results with reduced arcing current
    incident_energy_min_j_cm2: float
    incident_energy_min_cal_cm2: float
    afb_min_mm: float
    afb_min_inches: float
    
    # Final results (max of normal and reduced)
    final_incident_energy_j_cm2: float
    final_incident_energy_cal_cm2: float
    final_afb_mm: float
    final_afb_inches: float
    governing_current: str  # "normal" or "reduced"


def calculate_arc_flash(
    ibf_ka: float,
    voc_kv: float,
    gap_mm: float,
    working_distance_mm: float,
    arc_duration_ms: float,
    height_mm: float,
    width_mm: float,
    depth_mm: float,
    config: ElectrodeConfig,
    arc_duration_min_ms: Optional[float] = None
) -> ArcFlashResult:
    """
    Calculate arc flash hazard per IEEE 1584-2018.
    
    This is the main entry point for arc flash calculations.
    
    Args:
        ibf_ka: Bolted fault current (kA)
        voc_kv: Open circuit voltage (kV)
        gap_mm: Gap between electrodes (mm)
        working_distance_mm: Working distance (mm)
        arc_duration_ms: Arc duration for normal arcing current (ms)
        height_mm: Internal enclosure height (mm)
        width_mm: Internal enclosure width (mm)
        depth_mm: Internal enclosure depth (mm)
        config: Electrode configuration
        arc_duration_min_ms: Arc duration for reduced current (ms), defaults to same
    
    Returns:
        ArcFlashResult with complete calculation results
    """
    if arc_duration_min_ms is None:
        arc_duration_min_ms = arc_duration_ms
    
    # Step 1: Calculate arcing currents
    arc_current = calculate_arcing_current(ibf_ka, voc_kv, gap_mm, config)
    
    # Step 2: Calculate enclosure correction factor
    cf, ees, is_shallow = calculate_correction_factor(
        height_mm, width_mm, depth_mm, voc_kv, config
    )
    
    # Step 3: Calculate incident energy with normal arcing current
    energy_j, energy_cal = calculate_incident_energy(
        iarc_600_ka=arc_current.iarc_600,
        iarc_2700_ka=arc_current.iarc_2700,
        iarc_14300_ka=arc_current.iarc_14300,
        iarc_final_ka=arc_current.iarc,
        ibf_ka=ibf_ka,
        voc_kv=voc_kv,
        gap_mm=gap_mm,
        distance_mm=working_distance_mm,
        arc_duration_ms=arc_duration_ms,
        correction_factor=cf,
        config=config
    )
    
    # Step 4: Calculate incident energy with reduced arcing current
    energy_min_j, energy_min_cal = calculate_incident_energy(
        iarc_600_ka=arc_current.iarc_600,
        iarc_2700_ka=arc_current.iarc_2700,
        iarc_14300_ka=arc_current.iarc_14300,
        iarc_final_ka=arc_current.iarc_min,
        ibf_ka=ibf_ka,
        voc_kv=voc_kv,
        gap_mm=gap_mm,
        distance_mm=working_distance_mm,
        arc_duration_ms=arc_duration_min_ms,
        correction_factor=cf,
        config=config
    )
    
    # Step 5: Calculate AFB with normal arcing current
    afb_mm, afb_inches = calculate_arc_flash_boundary(
        iarc_600_ka=arc_current.iarc_600,
        iarc_2700_ka=arc_current.iarc_2700,
        iarc_14300_ka=arc_current.iarc_14300,
        iarc_final_ka=arc_current.iarc,
        ibf_ka=ibf_ka,
        voc_kv=voc_kv,
        gap_mm=gap_mm,
        arc_duration_ms=arc_duration_ms,
        correction_factor=cf,
        config=config
    )
    
    # Step 6: Calculate AFB with reduced arcing current
    afb_min_mm, afb_min_inches = calculate_arc_flash_boundary(
        iarc_600_ka=arc_current.iarc_600,
        iarc_2700_ka=arc_current.iarc_2700,
        iarc_14300_ka=arc_current.iarc_14300,
        iarc_final_ka=arc_current.iarc_min,
        ibf_ka=ibf_ka,
        voc_kv=voc_kv,
        gap_mm=gap_mm,
        arc_duration_ms=arc_duration_min_ms,
        correction_factor=cf,
        config=config
    )
    
    # Step 7: Determine final values (max of normal and reduced)
    if energy_min_j > energy_j:
        governing = "reduced"
        final_energy_j = energy_min_j
        final_energy_cal = energy_min_cal
    else:
        governing = "normal"
        final_energy_j = energy_j
        final_energy_cal = energy_cal
    
    final_afb_mm = max(afb_mm, afb_min_mm)
    final_afb_inches = final_afb_mm / INCHES_TO_MM
    
    return ArcFlashResult(
        # Inputs
        ibf_ka=ibf_ka,
        voc_kv=voc_kv,
        gap_mm=gap_mm,
        working_distance_mm=working_distance_mm,
        arc_duration_ms=arc_duration_ms,
        electrode_config=config,
        height_mm=height_mm,
        width_mm=width_mm,
        depth_mm=depth_mm,
        # Arcing current
        iarc_600_ka=arc_current.iarc_600,
        iarc_2700_ka=arc_current.iarc_2700,
        iarc_14300_ka=arc_current.iarc_14300,
        iarc_ka=arc_current.iarc,
        iarc_min_ka=arc_current.iarc_min,
        variation_factor=arc_current.variation_factor,
        # Enclosure
        correction_factor=cf,
        ees_inches=ees,
        is_shallow_enclosure=is_shallow,
        # Normal results
        incident_energy_j_cm2=energy_j,
        incident_energy_cal_cm2=energy_cal,
        afb_mm=afb_mm,
        afb_inches=afb_inches,
        # Reduced results
        incident_energy_min_j_cm2=energy_min_j,
        incident_energy_min_cal_cm2=energy_min_cal,
        afb_min_mm=afb_min_mm,
        afb_min_inches=afb_min_inches,
        # Final results
        final_incident_energy_j_cm2=final_energy_j,
        final_incident_energy_cal_cm2=final_energy_cal,
        final_afb_mm=final_afb_mm,
        final_afb_inches=final_afb_inches,
        governing_current=governing
    )