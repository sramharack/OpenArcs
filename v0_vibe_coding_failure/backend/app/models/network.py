"""
Power system network models for multi-equipment arc flash analysis.

This module defines the component types and network structure needed
for proper arc flash studies that account for upstream impedance.
"""

from enum import Enum
from typing import Dict, List, Tuple, Any, Optional
from pydantic import BaseModel, Field
from app.models.equipment import EnclosureType


class ComponentType(str, Enum):
    """Types of power system components"""
    SOURCE = "source"
    TRANSFORMER = "transformer"
    BUS = "bus"
    BREAKER = "breaker"
    CABLE = "cable"
    BUSDUCT = "busduct"
    PANEL = "panel"
    SWITCHBOARD = "switchboard"
    MCC = "mcc"
    EV_CHARGER = "ev_charger"
    MOTOR = "motor"


class Source(BaseModel):
    """Utility source or generator"""
    id: str
    name: str
    type: ComponentType = ComponentType.SOURCE
    voltage_kv: float = Field(..., description="Source voltage in kV")
    fault_mva: float = Field(..., description="Available fault MVA")
    x_r_ratio: float = Field(default=6.0, description="X/R ratio at source")
    
    # Visual position
    x: float = 0
    y: float = 0


class Transformer(BaseModel):
    """Power transformer"""
    id: str
    name: str
    type: ComponentType = ComponentType.TRANSFORMER
    
    # Electrical params
    primary_voltage_kv: float
    secondary_voltage_kv: float
    mva_rating: float
    impedance_percent: float = Field(..., description="% impedance on base")
    x_r_ratio: float = 6.0
    
    # Connection
    primary_grounding: str = "solidly_grounded"
    secondary_grounding: str = "solidly_grounded"
    
    # Visual
    x: float = 0
    y: float = 0


class Bus(BaseModel):
    """Bus - can be panel, switchboard, or MCC"""
    id: str
    name: str
    type: ComponentType  # PANEL, SWITCHBOARD, MCC
    
    # Electrical
    voltage_v: float
    rated_current_a: float = 100
    
    # Arc flash params
    enclosure_type: EnclosureType
    electrode_gap: float
    working_distance: float
    
    # Visual
    x: float = 0
    y: float = 0


class Breaker(BaseModel):
    """Circuit breaker or fuse"""
    id: str
    name: str
    type: ComponentType = ComponentType.BREAKER
    
    # Ratings
    frame_rating_a: float
    trip_rating_a: float
    interrupt_rating_ka: float
    
    # Timing (from TCC curve or spec sheet)
    instantaneous_pickup_a: Optional[float] = None
    short_time_pickup_a: Optional[float] = None
    clearing_time_at_fault: float = Field(
        ..., 
        description="Clearing time in seconds at expected fault level"
    )
    
    # Visual
    x: float = 0
    y: float = 0


class Cable(BaseModel):
    """Cable or conductor"""
    id: str
    name: str
    type: ComponentType = ComponentType.CABLE
    
    # Physical
    length_ft: float
    size_awg_kcmil: str = Field(..., description="e.g., '500 kcmil', '2/0 AWG'")
    conductor_material: str = "copper"  # copper or aluminum
    num_parallel: int = 1
    conduit_material: str = "steel"  # for impedance calculation
    
    # Calculated impedance (Ω/1000ft)
    resistance_per_1000ft: Optional[float] = None
    reactance_per_1000ft: Optional[float] = None
    
    # Visual
    x: float = 0
    y: float = 0


class EVCharger(BaseModel):
    """EV Charging station"""
    id: str
    name: str
    type: ComponentType = ComponentType.EV_CHARGER
    
    # Electrical
    voltage_v: float
    rated_power_kw: float
    current_rating_a: float
    num_ports: int = 1
    
    # Arc flash
    enclosure_type: EnclosureType = EnclosureType.VCB
    electrode_gap: float = 25
    working_distance: float = 18
    
    # Visual
    x: float = 0
    y: float = 0


class Connection(BaseModel):
    """Connection between components"""
    id: str
    from_component_id: str
    to_component_id: str
    cable_id: Optional[str] = None  # If connection is through a cable


class NetworkModel(BaseModel):
    """Complete power system network"""
    id: str
    name: str
    description: Optional[str] = None
    
    # Components
    sources: Dict[str, Source] = {}
    transformers: Dict[str, Transformer] = {}
    buses: Dict[str, Bus] = {}
    breakers: Dict[str, Breaker] = {}
    cables: Dict[str, Cable] = {}
    ev_chargers: Dict[str, EVCharger] = {}
    
    # Connections (defines topology)
    connections: List[Connection] = []
    
    def add_component(self, component: Any):
        """Add a component to the network"""
        if component.type == ComponentType.SOURCE:
            self.sources[component.id] = component
        elif component.type == ComponentType.TRANSFORMER:
            self.transformers[component.id] = component
        elif component.type in [ComponentType.BUS, ComponentType.PANEL, 
                                ComponentType.SWITCHBOARD, ComponentType.MCC]:
            self.buses[component.id] = component
        elif component.type == ComponentType.BREAKER:
            self.breakers[component.id] = component
        elif component.type in [ComponentType.CABLE, ComponentType.BUSDUCT]:
            self.cables[component.id] = component
        elif component.type == ComponentType.EV_CHARGER:
            self.ev_chargers[component.id] = component
    
    def get_all_components(self) -> Dict[str, Any]:
        """Get all components as a flat dict"""
        components = {}
        components.update(self.sources)
        components.update(self.transformers)
        components.update(self.buses)
        components.update(self.breakers)
        components.update(self.cables)
        components.update(self.ev_chargers)
        return components
    
    def get_component(self, component_id: str) -> Optional[Any]:
        """Get a component by ID"""
        return self.get_all_components().get(component_id)
    
    def get_downstream_components(self, component_id: str) -> List[str]:
        """Get IDs of components connected downstream"""
        downstream = []
        for conn in self.connections:
            if conn.from_component_id == component_id:
                downstream.append(conn.to_component_id)
        return downstream
    
    def get_upstream_component(self, component_id: str) -> Optional[str]:
        """Get ID of component connected upstream"""
        for conn in self.connections:
            if conn.to_component_id == component_id:
                return conn.from_component_id
        return None


class ArcFlashAnalysisResult(BaseModel):
    """Results for entire network analysis"""
    network_id: str
    network_name: str
    
    # Results for each bus/equipment location
    bus_results: Dict[str, Any]  # bus_id -> CalculationResult
    
    # Summary statistics
    max_incident_energy: float
    max_incident_energy_location: str
    num_high_hazard_locations: int  # PPE Cat 3 or 4
    
    # Warnings
    warnings: List[str] = []