"""
Arc Flash Studio Network - PandaPower Integration
=================================================

The Network class wraps PandaPower to provide:
1. Pydantic-validated component input
2. Convenient API for building networks
3. Short-circuit results formatted for arc flash calculations

The actual short-circuit calculations are delegated to PandaPower,
which implements IEC 60909 and has been validated against commercial
software (DIgSILENT PowerFactory, PSS Sincal).

References:
    - PandaPower: https://pandapower.readthedocs.io/
    - IEC 60909-0: Short-circuit currents in three-phase a.c. systems

Traceability:
    - REQ-COMP-FUNC-10: Network topology support
    - REQ-COMP-FUNC-12: Short-circuit calculation via PandaPower
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandapower as pp
import pandapower.shortcircuit as sc

# Import components from the components package
from arc_flash_studio.components import (
    # Enums
    VoltageLevel,
    ElectrodeConfig,
    EquipmentType,
    # Node types (all become buses in PandaPower)
    NetworkNode,
    Bus,
    Switchgear,
    Panelboard,
    MCC,
    CableJunction,
    OpenAir,
    # Sources
    UtilitySource,
    # Branches
    Transformer,
    Cable,
    # Helpers
    EnclosureInfo,
    create_cable,
)


# =============================================================================
# Network Class - Wraps PandaPower
# =============================================================================

@dataclass
class ShortCircuitResult:
    """Results from short-circuit calculation at a bus."""
    bus_id: str
    bus_name: str
    voltage_kv: float
    ikss_ka: float          # Initial symmetrical short-circuit current
    ip_ka: float            # Peak short-circuit current
    ith_ka: float           # Thermal equivalent current
    skss_mva: float         # Short-circuit power
    
    # For arc flash calculations
    equipment_type: EquipmentType = EquipmentType.OTHER
    electrode_config: ElectrodeConfig = ElectrodeConfig.VCB
    gap_mm: float = 32.0
    working_distance_mm: float = 455.0
    enclosure: Optional[EnclosureInfo] = None


class Network:
    """
    Electrical network for short-circuit and arc flash analysis.
    
    This class wraps PandaPower to provide:
    - Pydantic-validated component input
    - Convenient API for building networks
    - Short-circuit results formatted for arc flash calculations
    
    Example:
        >>> net = Network()
        >>> net.add_bus(Bus(id="B1", name="Main", voltage_kv=0.48))
        >>> net.add_utility(UtilitySource(
        ...     id="U1", name="Grid", bus_id="B1",
        ...     short_circuit_mva=500, x_r_ratio=15
        ... ))
        >>> results = net.calculate_short_circuit()
        >>> print(results["B1"].ikss_ka)
    """
    
    def __init__(self, name: str = "network", frequency_hz: float = 60.0):
        """Create a new network."""
        self.name = name
        self.frequency_hz = frequency_hz
        
        # Component storage (our validated models)
        # All node types stored in _nodes (they all become buses in PandaPower)
        self._nodes: Dict[str, NetworkNode] = {}
        self._utilities: Dict[str, UtilitySource] = {}
        self._transformers: Dict[str, Transformer] = {}
        self._cables: Dict[str, Cable] = {}
        
        # PandaPower network (built on demand)
        self._pp_net: Optional[pp.pandapowerNet] = None
        self._bus_id_map: Dict[str, int] = {}  # our ID -> pandapower index
        self._dirty: bool = True  # Need to rebuild PP network?
    
    # -------------------------------------------------------------------------
    # Add Components
    # -------------------------------------------------------------------------
    
    def add_bus(self, node: NetworkNode) -> None:
        """
        Add a network node (bus, switchgear, panel, etc.) to the network.
        
        All NetworkNode subclasses (Bus, Switchgear, Panelboard, MCC, etc.)
        become buses in PandaPower. The equipment type affects arc flash
        parameters but not short-circuit calculations.
        """
        if node.id in self._nodes:
            raise ValueError(f"Node '{node.id}' already exists")
        self._nodes[node.id] = node
        self._dirty = True
    
    # Convenience aliases for specific equipment types
    add_switchgear = add_bus
    add_panel = add_bus
    add_mcc = add_bus
    
    def add_utility(self, utility: UtilitySource) -> None:
        """Add a utility source (external grid)."""
        if utility.bus_id not in self._nodes:
            raise ValueError(f"Bus '{utility.bus_id}' not found")
        self._utilities[utility.id] = utility
        self._dirty = True
    
    def add_transformer(self, transformer: Transformer) -> None:
        """Add a transformer."""
        for bus_id in [transformer.hv_bus_id, transformer.lv_bus_id]:
            if bus_id not in self._nodes:
                raise ValueError(f"Bus '{bus_id}' not found")
        self._transformers[transformer.id] = transformer
        self._dirty = True
    
    def add_cable(self, cable: Cable) -> None:
        """Add a cable (line)."""
        for bus_id in [cable.from_bus_id, cable.to_bus_id]:
            if bus_id not in self._nodes:
                raise ValueError(f"Bus '{bus_id}' not found")
        self._cables[cable.id] = cable
        self._dirty = True
    
    # -------------------------------------------------------------------------
    # Build PandaPower Network
    # -------------------------------------------------------------------------
    
    def _build_pp_network(self) -> None:
        """Convert our components to a PandaPower network."""
        self._pp_net = pp.create_empty_network(
            name=self.name,
            f_hz=self.frequency_hz
        )
        self._bus_id_map = {}
        
        # Create buses (all node types become buses)
        for node_id, node in self._nodes.items():
            pp_idx = pp.create_bus(
                self._pp_net,
                vn_kv=node.voltage_kv,
                name=node.name
            )
            self._bus_id_map[node_id] = pp_idx
        
        # Create external grids (utilities)
        for util in self._utilities.values():
            pp_bus = self._bus_id_map[util.bus_id]
            pp.create_ext_grid(
                self._pp_net,
                bus=pp_bus,
                vm_pu=1.0,
                name=util.name,
                s_sc_max_mva=util.short_circuit_mva,
                rx_max=1.0 / util.x_r_ratio,  # PandaPower uses R/X
                x0x_max=1.0,
                r0x0_max=1.0,
            )
        
        # Create transformers
        for xfmr in self._transformers.values():
            pp_hv_bus = self._bus_id_map[xfmr.hv_bus_id]
            pp_lv_bus = self._bus_id_map[xfmr.lv_bus_id]
            
            pp.create_transformer_from_parameters(
                self._pp_net,
                hv_bus=pp_hv_bus,
                lv_bus=pp_lv_bus,
                name=xfmr.name,
                sn_mva=xfmr.rated_mva,
                vn_hv_kv=xfmr.hv_kv,
                vn_lv_kv=xfmr.lv_kv,
                vk_percent=xfmr.impedance_percent,
                vkr_percent=xfmr.vkr_percent,
                pfe_kw=0,
                i0_percent=0,
                vector_group=xfmr.vector_group,
            )
        
        # Create lines (cables)
        for cable in self._cables.values():
            pp_from = self._bus_id_map[cable.from_bus_id]
            pp_to = self._bus_id_map[cable.to_bus_id]
            
            pp.create_line_from_parameters(
                self._pp_net,
                from_bus=pp_from,
                to_bus=pp_to,
                length_km=cable.length_km,
                name=cable.name,
                r_ohm_per_km=cable.r_ohm_per_km,
                x_ohm_per_km=cable.x_ohm_per_km,
                c_nf_per_km=0,
                max_i_ka=10.0,  # Placeholder
            )
        
        self._dirty = False
    
    # -------------------------------------------------------------------------
    # Short-Circuit Calculation
    # -------------------------------------------------------------------------
    
    def calculate_short_circuit(
        self,
        bus_ids: Optional[List[str]] = None
    ) -> Dict[str, ShortCircuitResult]:
        """
        Calculate short-circuit currents using PandaPower (IEC 60909).
        
        Args:
            bus_ids: List of bus IDs to calculate. If None, calculates all.
        
        Returns:
            Dictionary mapping bus ID to ShortCircuitResult
        """
        # Rebuild PP network if needed
        if self._dirty or self._pp_net is None:
            self._build_pp_network()
        
        # Determine which buses to calculate
        if bus_ids is None:
            target_buses = list(self._nodes.keys())
        else:
            target_buses = bus_ids
        
        # Run short-circuit for each bus
        results = {}
        for bus_id in target_buses:
            if bus_id not in self._bus_id_map:
                raise ValueError(f"Bus '{bus_id}' not found")
            
            pp_bus_idx = self._bus_id_map[bus_id]
            node = self._nodes[bus_id]
            
            # Run IEC 60909 short-circuit calculation
            sc.calc_sc(
                self._pp_net,
                bus=pp_bus_idx,
                branch_results=False,
                return_all_currents=False,
            )
            
            # Extract results
            res = self._pp_net.res_bus_sc.loc[pp_bus_idx]
            
            # Get arc flash parameters from the node
            gap_mm = node.get_gap_mm()
            working_distance = node.get_working_distance_mm()
            enclosure = node.get_enclosure()
            
            results[bus_id] = ShortCircuitResult(
                bus_id=bus_id,
                bus_name=node.name,
                voltage_kv=node.voltage_kv,
                ikss_ka=res['ikss_ka'],
                ip_ka=res.get('ip_ka', res['ikss_ka'] * 2.5),  # Approximate if not available
                ith_ka=res.get('ith_ka', res['ikss_ka']),
                skss_mva=res.get('skss_mw', res['ikss_ka'] * node.voltage_kv * math.sqrt(3)),
                equipment_type=node.equipment_type,
                electrode_config=enclosure.electrode_config,
                gap_mm=gap_mm,
                working_distance_mm=working_distance,
                enclosure=enclosure,
            )
        
        return results
    
    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------
    
    def get_bus(self, bus_id: str) -> NetworkNode:
        """Get a bus/node by ID."""
        if bus_id not in self._nodes:
            raise KeyError(f"Bus '{bus_id}' not found")
        return self._nodes[bus_id]
    
    def list_buses(self) -> List[str]:
        """List all bus/node IDs."""
        return list(self._nodes.keys())
    
    @property
    def pp_network(self) -> pp.pandapowerNet:
        """Access the underlying PandaPower network (for advanced use)."""
        if self._dirty or self._pp_net is None:
            self._build_pp_network()
        return self._pp_net
    
    def __repr__(self) -> str:
        return (
            f"Network('{self.name}', "
            f"buses={len(self._nodes)}, "
            f"transformers={len(self._transformers)}, "
            f"cables={len(self._cables)})"
        )