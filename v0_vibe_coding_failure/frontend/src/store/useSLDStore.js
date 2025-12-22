import { create } from "zustand";

export const useSLDStore = create((set) => ({
  nodes: [],
  edges: [],
  placementType: null,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  setPlacement: (type) => set({ placementType: type }),

  updateNodeData: (id, newData) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === id ? { ...n, data: { ...n.data, ...newData } } : n
      ),
    })),
}));
