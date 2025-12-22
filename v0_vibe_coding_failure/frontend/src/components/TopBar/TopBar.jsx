export default function TopBar() {
    return (
      <div className="w-full h-12 bg-white border-b flex items-center px-4 space-x-4">
        <button className="px-3 py-1 bg-gray-200 rounded">Save</button>
        <button className="px-3 py-1 bg-gray-200 rounded">Undo</button>
        <button className="px-3 py-1 bg-gray-200 rounded">Redo</button>
        <button className="px-3 py-1 bg-gray-200 rounded">Run</button>
      </div>
    );
  }
  