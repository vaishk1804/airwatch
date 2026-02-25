import { useState } from "react";
import { useQuery,useMutation } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getLocations,subscribe,listSubscriptions } from "../lib/api";

export default function Subscriptions(){
  const [email,setEmail] = useState("");
  const [ locationId,setLocationId] = useState<number>(1);
  const [ threshold,setThreshold] = useState<number>(35);

  const locations = useQuery({queryKey:["locations"],queryFn:getLocations});

  const subs = useQuery({
    queryKey: ["subs",email],
    queryFn:()=>listSubscriptions(email),
    enabled:email.length>3,
  });

  const m = useMutation({
    mutationFn:()=> subscribe(email,locationId,threshold),
    onSuccess:()=>subs.refetch(),
  });

  return (
    <div>
      <Link to="/">Back</Link>
      <h2>Alerts</h2>

      <div style = {{display:"grid",gap:8,maxWidth:420}}>
        <label>Email</label>
 <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@email.com" />

        <label>Location</label>
        <select value={locationId} onChange={(e) => setLocationId(Number(e.target.value))}>
          {(locations.data ?? []).map((l) => (
            <option key={l.id} value={l.id}>{l.name}{l.state ? `, ${l.state}` : ""}</option>
          ))}
        </select>

        <label>Threshold (PM2.5)</label>
        <input type="number" value={threshold} onChange={(e) => setThreshold(Number(e.target.value))} />

        <button onClick={() => m.mutate()} disabled={m.isPending || !email}>
          {m.isPending ? "Saving..." : "Save subscription"}
        </button>

        {m.isError && <p style={{ color: "crimson" }}>Failed to subscribe</p>}
        {m.isSuccess && <p>Saved ✅</p>}
      </div>

      <hr style={{ margin: "16px 0" }} />

      <h3>Your subscriptions</h3>
      {subs.isLoading && <p>Loading...</p>}
      {subs.data && (
        <ul>
          {subs.data.map((s) => (
            <li key={s.id}>
              location_id={s.location_id} • threshold={s.threshold} • active={String(s.is_active)}
            </li>
          ))}
        </ul>
      )}    
    </div>
  )

}