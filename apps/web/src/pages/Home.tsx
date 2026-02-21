import { useQuery,useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getHealth,getReady,getLocations,triggerAirIngest } from "../lib/api";

export default function Home(){
  const qc = useQueryClient();

  const health = useQuery({queryKey: ["health"],queryFn:getHealth});
  const ready = useQuery({queryKey:["ready"],queryFn: getReady});
  const locations = useQuery({queryKey:["locations"],queryFn:getLocations});
  console.log(locations)
  const ingest = useMutation({
    mutationFn: (() => triggerAirIngest(24)),
    onSuccess: ()=>{
      qc.invalidateQueries({queryKey:["locations"]});
    },
  });

  return(
    <div>
      <h1>AirWatch</h1>
      <p>OpenAQ + Open-Meteo (Day 2)</p>

      <div style={{marginTop:16}}>
        <h3>Backend stats</h3>
        <ul>
          <li>
            /healthz:{" "}
            {health.isLoading
              ? "Loading..."
              : health.isError
              ? "Error"
              : health.data?.status}
          </li>
          <li>
            /readyz (db):{" "}
            {ready.isLoading
              ? "Loading..."
              : ready.isError
              ? "Error"
              : ready.data?.db
              ? "OK"
              : "Not ready"}
          </li>
        </ul>
</div>

         <div style={{ marginTop: 16 }}>
        <button
          onClick={() => ingest.mutate()}
          disabled={ingest.isPending}
          style={{ padding: "8px 12px" }}
        >
          {ingest.isPending ? "Ingesting..." : "Trigger Air Ingestion (24h)"}
        </button>
        {ingest.isError && <p style={{ color: "crimson" }}>Ingest failed</p>}
        {ingest.isSuccess && <p>Ingest triggered ✅</p>}
      </div>

      <hr style={{ margin: "16px 0" }} />

      <h3>Locations</h3>
      {locations.isLoading && <p>Loading locations...</p>}
      {locations.isError && <p>Failed to load locations</p>}

      {locations.data && (
        <ul>
          {locations.data.map((loc) => (
            <li key={loc.id}>
              <Link to={`/location/${loc.id}`}>
                {loc.name}
                {loc.state ? `, ${loc.state}` : ""} ({loc.country})
              </Link>
            </li>
          ))}
        </ul>
      )}
      
    </div>
  );
}