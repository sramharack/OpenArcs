import ReactFlow, { Background, Controls, addEdge, useReactFlow } from "reactflow";
import { useSLDStore } from "../../store/useSLDStore";
import "reactflow/dist/style.css";

import BusbarNode from "./customNodes/BusbarNode";
// Add other nodes later…

const nodeTypes = {
  busbar: BusbarNode,
};

export default function SLDCanvas() {
  const { nodes, edges, setNodes, setEdges, placementType, setPlacement } =
    useSLDStore();
  const reactFlow = useReactFlow();

  const onConnect = (params) => setEdges((eds) => addEdge(params, eds));

  const handleCanvasClick = (evt) => {
    if (!placementType) return;

    const pos = reactFlow.screenToFlowPosition({
      x: evt.clientX,
      y: evt.clientY,
    });

    const newNode = {
      id: `${Date.now()}`,
      type: placementType,
      position: pos,
      data: {
        label: placementType.toUpperCase(),
        onClick: () => setSelectedNode(newNode),
      },
    };

    setNodes([...nodes, newNode]);
    setPlacement(null);
  };

  return (
    <div
      style={{ width: "100%", height: "100%" }}
      onClick={handleCanvasClick}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
