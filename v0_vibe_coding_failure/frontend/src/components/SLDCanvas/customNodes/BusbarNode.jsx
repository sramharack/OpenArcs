import { Handle, Position } from 'reactflow';

export default function BusbarNode({ data }) {
  return (
    <div
      onClick={data.onClick} 
      className="px-4 py-2 border-2 rounded bg-white shadow-md text-center"
    >
      <strong>{data.label || "Bus"}</strong>
      <div style={{ fontSize: 10 }}>{data.kv ? `${data.kv} kV` : ""}</div>

      <Handle type="source" position={Position.Bottom} />
      <Handle type="target" position={Position.Top} />
    </div>
  );
}
