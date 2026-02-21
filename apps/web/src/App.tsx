import { Route,Routes,Link } from "react-router-dom";
import Home from "./pages/Home";
import LocationDashboard from "./pages/LocationDashboard";

export default function App(){
  return(
<div style={{padding:16,fontFamily: "system-ui, sans-serif"}}>
  <header style={{display:"flex", gap: 12, marginBottom: 16}}>
    <Link to="/">Home</Link>
    <Link to="/location">Location (placeholder)</Link>
  </header>
  <Routes>
    <Route path="/" element={<Home/>}/>
    <Route path="/location/:id" element={<LocationDashboard/>}/>
  </Routes>
</div>
  );
}