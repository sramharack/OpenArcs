import React, { useState, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { 
  Zap, 
  Box, 
  Activity, 
  Power,
  Cpu,
  Battery,
  Save,
  Play,
  Upload,
  Info
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';

// Custom node components
const SourceNode = ({ data }) => (
  <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg shadow-lg p-4 border-2 border-red-700 min-w-[120px]">
    <div className="flex items-center gap-2 mb-2">
      <Power className="w-5 h-5" />
      <div className="font-semibold text-sm">Source</div>
    </div>
    <div className="text-xs opacity-90">{data.label}</div>
    {data.voltage_kv && (
      <div className="text-xs mt-1 font-mono">{data.voltage_kv} kV</div>
    )}
  </div>
);

const TransformerNode = ({ data }) => (
  <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg shadow-lg p-4 border-2 border-blue-700 min-w-[140px]">
    <div className="flex items-center gap-2 mb-2">
      <Cpu className="w-5 h-5" />
      <div className="font-semibold text-sm">Transformer</div>
    </div>
    <div className="text-xs opacity-90">{data.label}</div>
    {data.mva_rating && (
      <div className="text-xs mt-1 font-mono">{data.mva_rating} MVA</div>
    )}
  </div>
);

const BusNode = ({ data }) => {
  const bgColor = data.type === 'switchboard' 
    ? 'from-purple-500 to-purple-600 border-purple-700'
    : data.type === 'mcc'
    ? 'from-orange-500 to-orange-600 border-orange-700'
    : 'from-green-500 to-green-600 border-green-700';
  
  return (
    <div className={`bg-gradient-to-br ${bgColor} text-white rounded-lg shadow-lg p-4 border-2 min-w-[140px]`}>
      <div className="flex items-center gap-2 mb-2">
        <Box className="w-5 h-5" />
        <div className="font-semibold text-sm capitalize">{data.type || 'Bus'}</div>
      </div>
      <div className="text-xs opacity-90">{data.label}</div>
      {data.voltage_v && (
        <div className="text-xs mt-1 font-mono">{data.voltage_v}V</div>
      )}
    </div>
  );
};

const BreakerNode = ({ data }) => (
  <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white rounded-lg shadow-lg p-3 border-2 border-yellow-700 min-w-[100px]">
    <div className="flex items-center gap-2 mb-1">
      <Activity className="w-4 h-4" />
      <div className="font-semibold text-xs">Breaker</div>
    </div>
    <div className="text-xs opacity-90">{data.label}</div>
    {data.rating_a && (
      <div className="text-xs mt-1 font-mono">{data.rating_a}A</div>
    )}
  </div>
);

const EVChargerNode = ({ data }) => (
  <div className="bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-lg shadow-lg p-4 border-2 border-teal-700 min-w-[120px]">
    <div className="flex items-center gap-2 mb-2">
      <Battery className="w-5 h-5" />
      <div className="font-semibold text-sm">EV Charger</div>
    </div>
    <div className="text-xs opacity-90">{data.label}</div>
    {data.power_kw && (
      <div className="text-xs mt-1 font-mono">{data.power_kw} kW</div>
    )}
  </div>
);

const nodeTypes = {
  source: SourceNode,
  transformer: TransformerNode,
  bus: BusNode,
  breaker: BreakerNode,
  evcharger: EVChargerNode,
};

function NetworkCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  const onConnect = useCallback(
    (params) => {
      setEdges((eds) => addEdge({
        ...params,
        animated: true,
        style: { stroke: '#64748b', strokeWidth: 2 }
      }, eds));
      toast.success('Components connected');
    },
    [setEdges]
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const addComponent = (type, subtype = null) => {
    const id = `${type}-${Date.now()}`;
    const position = { 
      x: Math.random() * 400 + 100, 
      y: Math.random() * 300 + 100 
    };

    const baseNode = {
      id,
      position,
      data: { 
        label: `${type.charAt(0).toUpperCase() + type.slice(1)} ${nodes.length + 1}`,
        type: subtype || type,
      },
      type: type,
    };

    // Add default properties
    switch(type) {
      case 'source':
        baseNode.data = { ...baseNode.data, voltage_kv: 13.8, fault_mva: 500 };
        break;
      case 'transformer':
        baseNode.data = { ...baseNode.data, mva_rating: 1.5, impedance_percent: 5.75 };
        break;
      case 'bus':
        baseNode.data = { ...baseNode.data, voltage_v: 480, working_distance: 24 };
        break;
      case 'breaker':
        baseNode.data = { ...baseNode.data, rating_a: 100 };
        break;
      case 'evcharger':
        baseNode.data = { ...baseNode.data, power_kw: 50 };
        break;
    }

    setNodes((nds) => nds.concat(baseNode));
    toast.success(`${type} added`);
  };

  return (
    <div className="w-screen h-screen flex flex-col bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Top Toolbar */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Arc Flash Studio</h1>
              <p className="text-xs text-gray-500">Network Builder</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium">
            <Save className="w-4 h-4" />
            Save
          </button>

          <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg transition-all text-sm font-medium">
            <Play className="w-4 h-4" />
            Run Analysis
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex min-h-0">
        {/* Component Palette */}
        <div className="w-64 bg-white border-r border-gray-200 p-4 overflow-y-auto">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Box className="w-4 h-4" />
            Components
          </h2>

          <div className="space-y-2">
            <ComponentButton
              icon={<Power className="w-4 h-4" />}
              label="Source"
              description="Utility/Generator"
              onClick={() => addComponent('source')}
              color="red"
            />
            
            <ComponentButton
              icon={<Cpu className="w-4 h-4" />}
              label="Transformer"
              description="Power transformer"
              onClick={() => addComponent('transformer')}
              color="blue"
            />
            
            <div className="border-t border-gray-200 pt-2 mt-2">
              <p className="text-xs text-gray-500 mb-2">Distribution Equipment</p>
              
              <ComponentButton
                icon={<Box className="w-4 h-4" />}
                label="Switchboard"
                description="Main switchboard"
                onClick={() => addComponent('bus', 'switchboard')}
                color="purple"
              />
              
              <ComponentButton
                icon={<Box className="w-4 h-4" />}
                label="Panel"
                description="Distribution panel"
                onClick={() => addComponent('bus', 'panel')}
                color="green"
              />
              
              <ComponentButton
                icon={<Box className="w-4 h-4" />}
                label="MCC"
                description="Motor control center"
                onClick={() => addComponent('bus', 'mcc')}
                color="orange"
              />
            </div>

            <div className="border-t border-gray-200 pt-2 mt-2">
              <p className="text-xs text-gray-500 mb-2">Protection & Loads</p>
              
              <ComponentButton
                icon={<Activity className="w-4 h-4" />}
                label="Breaker"
                description="Circuit breaker"
                onClick={() => addComponent('breaker')}
                color="yellow"
              />
              
              <ComponentButton
                icon={<Battery className="w-4 h-4" />}
                label="EV Charger"
                description="Electric vehicle charger"
                onClick={() => addComponent('evcharger')}
                color="teal"
              />
            </div>
          </div>

          <div className="mt-6 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-start gap-2">
              <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-xs text-blue-700">
                <p className="font-medium mb-1">How to use:</p>
                <ol className="list-decimal list-inside space-y-1 text-blue-600">
                  <li>Click to add components</li>
                  <li>Drag to connect them</li>
                  <li>Click node to edit</li>
                  <li>Run analysis</li>
                </ol>
              </div>
            </div>
          </div>
        </div>

        {/* Canvas - CRITICAL: Must have explicit height */}
        <div className="flex-1 relative" style={{ height: '100%' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            className="bg-gray-50"
          >
            <Background color="#e5e7eb" gap={16} />
            <Controls className="bg-white border border-gray-300 rounded-lg shadow-sm" />
            <MiniMap
              className="bg-white border border-gray-300 rounded-lg shadow-sm"
              nodeColor={(node) => {
                const colors = {
                  source: '#ef4444',
                  transformer: '#3b82f6',
                  bus: '#10b981',
                  breaker: '#eab308',
                  evcharger: '#14b8a6',
                };
                return colors[node.type] || '#6b7280';
              }}
            />
            
            {nodes.length === 0 && (
              <Panel position="top-center" className="pointer-events-none">
                <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200 max-w-md">
                  <div className="text-center">
                    <Zap className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Start Building Your Network
                    </h3>
                    <p className="text-sm text-gray-600">
                      Click components on the left to add them to your network
                    </p>
                  </div>
                </div>
              </Panel>
            )}
          </ReactFlow>
        </div>

        {/* Properties Panel */}
        {selectedNode && (
          <div className="w-80 bg-white border-l border-gray-200 p-6 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Properties</h2>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="text-sm text-gray-600">
              Selected: {selectedNode.data.label}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ComponentButton({ icon, label, description, onClick, color }) {
  const colorClasses = {
    red: 'hover:bg-red-50 hover:border-red-200',
    blue: 'hover:bg-blue-50 hover:border-blue-200',
    purple: 'hover:bg-purple-50 hover:border-purple-200',
    green: 'hover:bg-green-50 hover:border-green-200',
    orange: 'hover:bg-orange-50 hover:border-orange-200',
    yellow: 'hover:bg-yellow-50 hover:border-yellow-200',
    teal: 'hover:bg-teal-50 hover:border-teal-200',
  };

  return (
    <button
      onClick={onClick}
      className={`w-full flex items-start gap-3 p-3 border border-gray-200 rounded-lg transition-all ${colorClasses[color]} text-left`}
    >
      <div className="mt-0.5">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-gray-900">{label}</div>
        <div className="text-xs text-gray-500 truncate">{description}</div>
      </div>
    </button>
  );
}

export default NetworkCanvas;