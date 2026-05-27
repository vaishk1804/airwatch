import { Route, Routes, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import LocationDashboard from "./pages/LocationDashboard";
import Summary from "./pages/Summary";
import Subscriptions from "./pages/Subscriptions";

const navLinkStyle = ({ isActive }: { isActive: boolean }) => ({
  color: isActive ? "var(--accent)" : "var(--fg)",
  textDecoration: "none",
  fontWeight: isActive ? 600 : 500,
  padding: "6px 10px",
  borderRadius: 6,
  background: isActive ? "var(--accent-bg)" : "transparent",
});

export default function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-dot" />
          <span className="brand-name">AirWatch</span>
        </div>
        <nav className="app-nav">
          <NavLink to="/" style={navLinkStyle} end>Home</NavLink>
          <NavLink to="/summary" style={navLinkStyle}>Summary</NavLink>
          <NavLink to="/alerts" style={navLinkStyle}>Alerts</NavLink>
        </nav>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/location/:id" element={<LocationDashboard />} />
          <Route path="/summary" element={<Summary />} />
          <Route path="/alerts" element={<Subscriptions />} />
        </Routes>
      </main>
      <footer className="app-footer">
        <span>
          Data: <a href="https://openaq.org" target="_blank" rel="noreferrer">OpenAQ</a> ·{" "}
          <a href="https://open-meteo.com" target="_blank" rel="noreferrer">Open-Meteo</a>
        </span>
      </footer>
    </div>
  );
}