import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./styles/tailwind.css";
import "./styles/globals.css";


import AOS from "aos";
import "aos/dist/aos.css";
import { AuthProvider } from "./features/auth/AuthContext";

AOS.init({
  duration: 900,
  easing: "ease-out",
  once: true,
  offset: 90,
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
