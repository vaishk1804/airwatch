import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getLocations, subscribe, listSubscriptions } from "../lib/api";

export default function Subscriptions() {
  const [email, setEmail] = useState("");
  const [locationId, setLocationId] = useState<number>(1);
  const [threshold, setThreshold] = useState<number>(35);

  const locations = useQuery({ queryKey: ["locations"], queryFn: getLocations });

  const subs = useQuery({
    queryKey: ["subs", email],
    queryFn: () => listSubscriptions(email),
    enabled: email.length > 3,
  });

  const m = useMutation({
    mutationFn: () => subscribe(email, locationId, threshold),
    onSuccess: () => subs.refetch(),
  });

  const locationsById = new Map((locations.data ?? []).map((l) => [l.id, l]));

  return (
    <div>
      <Link to="/" className="back-link">← Back</Link>
      <div className="section-title"><h1>Email alerts</h1></div>
      <p className="muted">
        Get an email when your subscribed location crosses a PM2.5 threshold.
        Alerts run as a daily Celery beat task.
      </p>

      <div className="card" style={{ maxWidth: 480, marginTop: 16 }}>
        <div className="grid">
          <div>
            <label>Email</label>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              style={{ width: "100%", marginTop: 4 }}
            />
          </div>

          <div>
            <label>Location</label>
            <select
              value={locationId}
              onChange={(e) => setLocationId(Number(e.target.value))}
              style={{ width: "100%", marginTop: 4 }}
            >
              {(locations.data ?? []).map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}{l.state ? `, ${l.state}` : ""}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label>Threshold (PM2.5 µg/m³)</label>
            <input
              type="number"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              style={{ width: "100%", marginTop: 4 }}
            />
            <p className="muted" style={{ marginTop: 4 }}>
              EPA "unhealthy for sensitive groups" starts at 35.
            </p>
          </div>

          <button
            className="primary"
            onClick={() => m.mutate()}
            disabled={m.isPending || !email}
          >
            {m.isPending ? "Saving..." : "Save subscription"}
          </button>

          {m.isError && <p style={{ color: "var(--bad)" }}>Failed to subscribe.</p>}
          {m.isSuccess && <p style={{ color: "var(--good)" }}>Saved.</p>}
        </div>
      </div>

      <div className="section-title" style={{ marginTop: 24 }}>
        <h3>Your subscriptions</h3>
        {subs.data && <span className="muted">{subs.data.length} active</span>}
      </div>

      {!email && <p className="muted">Enter your email above to see your subscriptions.</p>}
      {subs.isLoading && <p className="muted">Loading...</p>}

      {subs.data && subs.data.length === 0 && email.length > 3 && (
        <p className="muted">No subscriptions yet.</p>
      )}

      {subs.data && subs.data.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <table>
            <thead>
              <tr>
                <th>Location</th>
                <th style={{ textAlign: "right" }}>Threshold</th>
                <th style={{ textAlign: "right" }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {subs.data.map((s) => {
                const loc = locationsById.get(s.location_id);
                return (
                  <tr key={s.id}>
                    <td>
                      <strong>{loc?.name ?? `Location ${s.location_id}`}</strong>
                      {loc?.state && <span className="muted">, {loc.state}</span>}
                    </td>
                    <td style={{ textAlign: "right", fontFamily: "ui-monospace, monospace" }}>
                      {s.threshold} µg/m³
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <span className={`badge ${s.is_active ? "good" : ""}`}>
                        {s.is_active ? "active" : "paused"}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
