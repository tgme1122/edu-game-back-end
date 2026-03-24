import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import AOS from "aos";

import AppRoutes from "./routes/AppRoutes";
import CursorGlow from "./components/ui/CursorGlow";

export default function App() {
  const location = useLocation();

  useEffect(() => {
    AOS.refreshHard();
  }, [location.pathname]);

  return (
    <div style={{ minHeight: "100vh", overflowX: "hidden" }}>
      <CursorGlow />
      <AppRoutes />
    </div>
  );
}