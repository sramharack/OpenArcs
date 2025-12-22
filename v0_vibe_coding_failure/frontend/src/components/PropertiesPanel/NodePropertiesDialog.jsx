import { useState } from "react";
import { useSLDStore } from "../../store/useSLDStore";

export default function NodePropertiesDialog({ node, open, onClose }) {
  const updateNodeData = useSLDStore((s) => s.updateNodeData);
  const [form, setForm] = useState(node.data || {});

  if (!open) return null;

  const save = () => {
    updateNodeData(node.id, form);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-96">
        <h2 className="font-bold mb-4">Properties – {node.type}</h2>

        <label>Label</label>
        <input
          className="border p-1 w-full mb-3"
          value={form.label || ""}
          onChange={(e) => setForm({ ...form, label: e.target.value })}
        />

        <label>Voltage (kV)</label>
        <input
          className="border p-1 w-full mb-3"
          value={form.kv || ""}
          onChange={(e) => setForm({ ...form, kv: e.target.value })}
        />

        <button
          onClick={save}
          className="bg-blue-600 text-white px-4 py-2 rounded mr-2"
        >
          Save
        </button>

        <button
          onClick={onClose}
          className="bg-gray-400 text-white px-4 py-2 rounded"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
