import { useSLDStore } from "../../store/useSLDStore";

const components = [
  { type: "busbar", label: "Busbar" },
  { type: "breaker", label: "Breaker" },
  { type: "transformer", label: "Transformer" },
  { type: "load", label: "Load" },
  { type: "motor", label: "Motor" },
  { type: "cable", label: "Cable" },
];

export default function ComponentSidebar() {
  const setPlacement = useSLDStore((s) => s.setPlacement);

  return (
    <div className="w-48 bg-white border-r p-2 overflow-y-auto">
      <h2 className="font-bold mb-2">Components</h2>

      {components.map((c) => (
        <button
          key={c.type}
          onClick={() => setPlacement(c.type)}
          className="w-full bg-gray-200 hover:bg-gray-300 text-left px-3 py-2 rounded mb-1"
        >
          {c.label}
        </button>
      ))}
    </div>
  );
}
