import { Route,Routes,Link } from "react-router-dom";
import Home from "./pages/Home";
import LocationDashboard from "./pages/LocationDashboard";
import Summary from "./pages/Summary";
import Subscriptions from "./pages/Subscriptions";

export default function App(){
  return(
<div style={{padding:16,fontFamily: "system-ui, sans-serif"}}>
  <header style={{display:"flex", gap: 12, marginBottom: 16}}>
    <Link to="/">Home</Link>
    <Link to="/location">Location (placeholder)</Link>
    <Link to="/summary">Summary</Link>
    <Link to="/alerts">Alerts</Link>
  </header>
  <Routes>
    <Route path="/" element={<Home/>}/>
    <Route path="/location/:id" element={<LocationDashboard/>}/>
    <Route path="/summary" element = {<Summary/>}/>
    <Route path="/alerts" element={<Subscriptions/>}/>
  </Routes>
</div>
  );
}