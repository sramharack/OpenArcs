"""
Network Module
==============

The Network class connects components into an electrical system and
provides methods for short-circuit analysis.

For Phase 1, we implement a simplified radial network analysis.
Future phases will integrate with PandaPower for complex networks.

Reference:
    - IEEE 1584-2018, Section 6
    - IEC 60909-0

Traceability:
    - REQ-COMP-FUNC-9: Network topology
    - REQ-COMP-FUNC-12: Short-circuit calculation
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, computed_field, ConfigDict

from arc_flash_studio.components.bus import Bus
from arc_flash_studio.components.utility_source import UtilitySource
from arc_flash_studio.components.transformer import Transformer
from arc_flash_studio.components.cable import Cable


@dataclass
class ShortCircuitResult:
    """Results of a short-circuit calculation at a specific bus."""
    
    bus_id: str
    bus_name: str
    voltage_kv: float
    
    # Fault current
    i_fault_ka: float          # Three-phase fault current magnitude (kA)
    i_fault_a: float           # Three-phase fault current (A)
    
    # Impedance to fault point
    z_total_pu: float          # Total impedance in per-unit
    r_total_pu: float          # Total resistance in per-unit
    x_total_pu: float          # Total reactance in per-unit
    z_total_ohms: float        # Total impedance in ohms at fault voltage
    
    # X/R ratio (important for asymmetry/DC offset)
    x_r_ratio: float
    
    # Contributing components
    impedance_breakdown: Dict[str, complex] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return (
            f"ShortCircuitResult at '{self.bus_id}' ({self.bus_name}):\n"
            f"  Voltage: {self.voltage_kv} kV\n"
            f"  I_fault: {self.i_fault_ka:.2f} kA ({self.i_fault_a:.0f} A)\n"
            f"  Z_total: {self.z_total_pu:.6f} pu ({self.z_total_ohms:.6f} Ω)\n"
            f"  X/R ratio: {self.x_r_ratio:.2f}"
        )


class RadialNetwork:
    """
    A simplified radial network for short-circuit analysis.
    
    This class models a radial (non-looped) network where power flows
    from a single source through a series of components to load buses.
    
    For Phase 1, we assume:
    - Single utility source
    - Radial topology (no loops)
    - Three-phase balanced faults
    - No motor contribution (added in Phase 2)
    
    Example:
        >>> network = RadialNetwork(system_base_mva=100.0)
        >>> 
        >>> # Add source
        >>> network.add_utility_source(utility)
        >>> 
        >>> # Add buses
        >>> network.add_bus(bus_primary)
        >>> network.add_bus(bus_secondary)
        >>> 
        >>> # Add components
        >>> network.add_transformer(transformer, from_bus="BUS-001", to_bus="BUS-002")
        >>> network.add_cable(cable, from_bus="BUS-002", to_bus="BUS-003")
        >>> 
        >>> # Calculate fault
        >>> result = network.calculate_fault_at_bus("BUS-003")
        >>> print(f"Fault current: {result.i_fault_ka:.2f} kA")
    """
    
    def __init__(self, system_base_mva: float = 100.0):
        """
        Initialize an empty radial network.
        
        Args:
            system_base_mva: System base MVA for per-unit calculations
        """
        self.system_base_mva = system_base_mva
        
        # Storage
        self._utility_source: Optional[UtilitySource] = None
        self._source_bus_id: Optional[str] = None
        self._buses: Dict[str, Bus] = {}
        self._transformers: Dict[str, dict] = {}  # id -> {component, from_bus, to_bus}
        self._cables: Dict[str, dict] = {}        # id -> {component, from_bus, to_bus}
        
        # Topology tracking
        self._connections: Dict[str, List[str]] = {}  # bus_id -> [connected_bus_ids]
    
    # -------------------------------------------------------------------------
    # Add Components
    # -------------------------------------------------------------------------
    
    def add_bus(self, bus: Bus) -> None:
        """Add a bus to the network."""
        if bus.id in self._buses:
            raise ValueError(f"Bus '{bus.id}' already exists in network")
        self._buses[bus.id] = bus
        self._connections[bus.id] = []
    
    def add_utility_source(self, source: UtilitySource, bus_id: str) -> None:
        """
        Add a utility source connected to a bus.
        
        Args:
            source: The UtilitySource component
            bus_id: ID of the bus where the source connects
        """
        if self._utility_source is not None:
            raise ValueError("Network already has a utility source (radial network supports one)")
        if bus_id not in self._buses:
            raise ValueError(f"Bus '{bus_id}' not found. Add the bus first.")
        
        self._utility_source = source
        self._source_bus_id = bus_id
    
    def add_transformer(self, transformer: Transformer, from_bus: str, to_bus: str) -> None:
        """
        Add a transformer connecting two buses.
        
        Args:
            transformer: The Transformer component
            from_bus: ID of the primary side bus
            to_bus: ID of the secondary side bus
        """
        for bus_id in [from_bus, to_bus]:
            if bus_id not in self._buses:
                raise ValueError(f"Bus '{bus_id}' not found. Add the bus first.")
        
        self._transformers[transformer.id] = {
            "component": transformer,
            "from_bus": from_bus,
            "to_bus": to_bus,
        }
        
        # Update connections
        self._connections[from_bus].append(to_bus)
        self._connections[to_bus].append(from_bus)
    
    def add_cable(self, cable: Cable, from_bus: str, to_bus: str) -> None:
        """
        Add a cable connecting two buses.
        
        Args:
            cable: The Cable component
            from_bus: ID of the source side bus
            to_bus: ID of the load side bus
        """
        for bus_id in [from_bus, to_bus]:
            if bus_id not in self._buses:
                raise ValueError(f"Bus '{bus_id}' not found. Add the bus first.")
        
        self._cables[cable.id] = {
            "component": cable,
            "from_bus": from_bus,
            "to_bus": to_bus,
        }
        
        # Update connections
        self._connections[from_bus].append(to_bus)
        self._connections[to_bus].append(from_bus)
    
    # -------------------------------------------------------------------------
    # Short-Circuit Calculation
    # -------------------------------------------------------------------------
    
    def calculate_fault_at_bus(self, fault_bus_id: str) -> ShortCircuitResult:
        """
        Calculate three-phase bolted fault current at a bus.
        
        This uses the Thévenin equivalent method:
        1. Find the path from source to fault bus
        2. Sum impedances along the path (in per-unit)
        3. Calculate fault current: I_fault = V / Z_total
        
        Args:
            fault_bus_id: ID of the bus where fault occurs
        
        Returns:
            ShortCircuitResult with fault current and impedance data
        """
        # Validate
        if fault_bus_id not in self._buses:
            raise ValueError(f"Bus '{fault_bus_id}' not found in network")
        if self._utility_source is None:
            raise ValueError("No utility source defined. Add one with add_utility_source()")
        
        fault_bus = self._buses[fault_bus_id]
        
        # Find path from source to fault
        path = self._find_path(self._source_bus_id, fault_bus_id)
        if path is None:
            raise ValueError(f"No path found from source to bus '{fault_bus_id}'")
        
        # Accumulate impedance along path
        z_total_pu = complex(0, 0)
        impedance_breakdown: Dict[str, complex] = {}
        
        # Add utility source impedance
        source_z = self._utility_source.get_impedance_complex()
        z_total_pu += source_z
        impedance_breakdown[f"Utility: {self._utility_source.id}"] = source_z
        
        # Walk through path and add component impedances
        for i in range(len(path) - 1):
            from_bus_id = path[i]
            to_bus_id = path[i + 1]
            
            # Find component connecting these buses
            component_z = self._get_component_impedance(from_bus_id, to_bus_id)
            if component_z is not None:
                comp_id, z_pu = component_z
                z_total_pu += z_pu
                impedance_breakdown[comp_id] = z_pu
        
        # Calculate fault current
        # V = 1.0 pu (assuming nominal voltage)
        # I = V / Z
        v_pu = 1.0
        i_fault_pu = v_pu / abs(z_total_pu)
        
        # Convert to actual values at fault bus voltage
        # I_base = S_base / (sqrt(3) * V_base)
        i_base_ka = self.system_base_mva / (math.sqrt(3) * fault_bus.voltage_nominal)
        i_fault_ka = i_fault_pu * i_base_ka
        i_fault_a = i_fault_ka * 1000
        
        # Z in ohms at fault voltage
        z_base_ohms = (fault_bus.voltage_nominal ** 2) / self.system_base_mva
        z_total_ohms = abs(z_total_pu) * z_base_ohms
        
        # X/R ratio
        if z_total_pu.real == 0:
            x_r_ratio = float('inf')
        else:
            x_r_ratio = z_total_pu.imag / z_total_pu.real
        
        return ShortCircuitResult(
            bus_id=fault_bus_id,
            bus_name=fault_bus.name,
            voltage_kv=fault_bus.voltage_nominal,
            i_fault_ka=i_fault_ka,
            i_fault_a=i_fault_a,
            z_total_pu=abs(z_total_pu),
            r_total_pu=z_total_pu.real,
            x_total_pu=z_total_pu.imag,
            z_total_ohms=z_total_ohms,
            x_r_ratio=x_r_ratio,
            impedance_breakdown=impedance_breakdown,
        )
    
    def _find_path(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find path between two buses using BFS.
        
        Returns list of bus IDs from start to end, or None if no path.
        """
        if start == end:
            return [start]
        
        visited = {start}
        queue = [[start]]
        
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            for neighbor in self._connections.get(current, []):
                if neighbor == end:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        
        return None
    
    def _get_component_impedance(self, from_bus: str, to_bus: str) -> Optional[tuple]:
        """
        Find the component connecting two buses and return its impedance.
        
        Returns tuple of (component_id, complex impedance in pu) or None.
        """
        # Check transformers
        for xfmr_id, data in self._transformers.items():
            if (data["from_bus"] == from_bus and data["to_bus"] == to_bus) or \
               (data["from_bus"] == to_bus and data["to_bus"] == from_bus):
                xfmr: Transformer = data["component"]
                # Convert to system base
                z_pu = complex(xfmr.r_pu, xfmr.x_pu)
                return (f"Transformer: {xfmr_id}", z_pu)
        
        # Check cables
        for cable_id, data in self._cables.items():
            if (data["from_bus"] == from_bus and data["to_bus"] == to_bus) or \
               (data["from_bus"] == to_bus and data["to_bus"] == from_bus):
                cable: Cable = data["component"]
                z_pu = complex(cable.r_pu, cable.x_pu)
                return (f"Cable: {cable_id}", z_pu)
        
        return None
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def get_bus(self, bus_id: str) -> Bus:
        """Get a bus by ID."""
        if bus_id not in self._buses:
            raise KeyError(f"Bus '{bus_id}' not found")
        return self._buses[bus_id]
    
    def list_buses(self) -> List[str]:
        """List all bus IDs in the network."""
        return list(self._buses.keys())
    
    def __str__(self) -> str:
        lines = [
            f"RadialNetwork (Base: {self.system_base_mva} MVA)",
            f"  Buses: {len(self._buses)}",
            f"  Transformers: {len(self._transformers)}",
            f"  Cables: {len(self._cables)}",
            f"  Source: {self._utility_source.id if self._utility_source else 'None'}",
        ]
        return "\n".join(lines)