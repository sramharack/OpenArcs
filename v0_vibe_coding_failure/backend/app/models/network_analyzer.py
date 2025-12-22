# app/services/network_analyzer.py

class NetworkAnalyzer:
    """Analyzes complete power system network"""
    
    def analyze(self, network: NetworkModel) -> Dict[str, ArcFlashResult]:
        """
        Analyze entire network:
        1. Build impedance model
        2. Calculate fault at each bus
        3. Run arc flash at each location
        """
        results = {}
        
        # Step 1: Calculate fault currents using PandaPower
        fault_currents = self._calculate_fault_currents(network)
        
        # Step 2: For each bus, calculate arc flash
        for bus_id, bus in network.get_buses():
            fault_current = fault_currents[bus_id]
            clearing_time = self._get_clearing_time(bus_id, network)
            
            result = self.arc_flash_calc.calculate(
                bus, fault_current, clearing_time
            )
            results[bus_id] = result
        
        return results
    
    def _calculate_fault_currents(self, network):
        """Use PandaPower for short circuit analysis"""
        # Build PandaPower network
        pp_net = self._build_pandapower_network(network)
        
        # Run short circuit
        import pandapower.shortcircuit as sc
        sc.calc_sc(pp_net, fault="3ph")
        
        # Extract fault currents at each bus
        return pp_net.res_bus_sc
