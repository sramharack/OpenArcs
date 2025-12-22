import { ReactFlowProvider } from "reactflow";

import ComponentSidebar from "./components/Sidebar/ComponentSidebar";
import SLDCanvas from "./components/SLDCanvas/SLDCanvas";
import TopBar from "./components/TopBar/TopBar";

export default function App() {
  return (
    <div className="w-screen h-screen flex flex-col">
      <TopBar />

      <div className="flex flex-row flex-grow">

        <ComponentSidebar />

        <div className="flex-grow h-full">
          <ReactFlowProvider>
            <SLDCanvas />
          </ReactFlowProvider>
       </div>

      </div>
    </div>
  );
}
