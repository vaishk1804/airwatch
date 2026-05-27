import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getHealth, getReady, getLocations, triggerAirIngest } from "../lib/api";

function StatusPill({ ok, label, loading }: { ok: boolean | undefined; label: string; loading: boolean }) {
  if (loading) return <span className="badge">checking...</span>;
  const cls = ok ? "badge good" : "badge bad";
  return <span className={cls}>{label}: {ok ? "ok" : "down"}</span>;
}

export default function Home() {
  const qc = useQueryClient();

  const health = useQuery({ queryKey: ["health"], queryFn: getHealth });
  const ready = useQuery({ queryKey: ["ready"], queryFn: getReady });
  const locations = useQuery({ queryKey: ["locations"], queryFn: getLocations });

  const ingest = useMutation({
    mutationFn: () => triggerAirIngest(24),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["locations"] });
    },
  });

  return (
    <div>
      <div style={{ marginBottom: 8 }}>
        <h1>Air quality, monitored in real time</h1>
        <p className="muted">
          Hourly PM2.5 from OpenAQ stations, merged with Open-Meteo weather,
          aggregated nightly into a bad-air leaderboard. Subscribe by email to get
          threshold-based alerts.
        </p>
      </div>

      <div className="row" style={{ margin: "12px 0 20px 0" }}>
        <StatusPill ok={health.data?.status === "ok"} label="api" loading={health.isLoading} />
        <StatusPill ok={ready.data?.db === true} label="db" loading={ready.isLoading} />
        <button
          className="primary"
          onClick={() => ingest.mutate()}
          disabled={ingest.isPending}
          style={{ marginLeft: "auto" }}
        >
          {ingest.isPending ? "Ingesting..." : "Trigger ingest (24h)"}
        </button>
      </div>
      {ingest.isError && <p style={{ color: "var(--bad)" }}>Ingest failed — check API logs.</p>}
      {ingest.isSuccess && <p className="muted">Ingest run completed.</p>}

      <div className="section-title">
        <h2>Monitored locations</h2>
        <span className="muted">{locations.data?.length ?? 0} sites</span>
      </div>

      {locations.isLoading && <p className="muted">Loading locations...</p>}
      {locations.isError && <p style={{ color: "var(--bad)" }}>Failed to load locations</p>}

      {locations.data && locations.data.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <table>
            <thead>
              <tr>
                <th>Location</th>
                <th>State</th>
                <th style={{ textAlign: "right" }}>Lat, Lon</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {locations.data.map((loc) => (
                <tr key={loc.id}>
                  <td><strong>{loc.name}</strong></td>
                  <td>{loc.state ?? "—"}</td>
                  <td style={{ textAlign: "right", fontFamily: "ui-monospace, monospace", fontSize: "0.85rem" }}>
                    {loc.lat.toFixed(3)}, {loc.lon.toFixed(3)}
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <Link to={`/location/${loc.id}`}>View dashboard →</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
