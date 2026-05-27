import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getBadDays, getBadDaysTrend } from "../lib/api";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  LineChart,
  Line,
  CartesianGrid,
} from "recharts";

export default function Summary() {
  const [windowDays, setWindowDays] = useState<30 | 90>(30);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const leaderboard = useQuery({
    queryKey: ["badDays", windowDays],
    queryFn: () => getBadDays(windowDays),
  });

  const trend = useQuery({
    queryKey: ["badDaysTrend", selectedId],
    queryFn: () => getBadDaysTrend(selectedId!, 90),
    enabled: selectedId != null,
  });

  const top = leaderboard.data?.slice(0, 8) ?? [];

  return (
    <div>
      <Link to="/" className="back-link">← Back</Link>
      <div className="section-title">
        <h1>Executive summary</h1>
        <span className="muted">Ranked by bad-air days</span>
      </div>

      <div className="toolbar">
        <button
          onClick={() => setWindowDays(30)}
          disabled={windowDays === 30}
          className={windowDays === 30 ? "primary" : ""}
        >
          Last 30 days
        </button>
        <button
          onClick={() => setWindowDays(90)}
          disabled={windowDays === 90}
          className={windowDays === 90 ? "primary" : ""}
        >
          Last 90 days
        </button>
      </div>

      {leaderboard.isLoading && <p className="muted">Loading summary...</p>}
      {leaderboard.isError && <p style={{ color: "var(--bad)" }}>Failed to load summary</p>}

      {leaderboard.data && (
        <>
          <div className="section-title"><h3>Bad-air days by location</h3></div>
          <div className="card" style={{ height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={top}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" stroke="var(--fg-muted)" fontSize={12} />
                <YAxis stroke="var(--fg-muted)" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                  }}
                />
                <Bar dataKey="bad_days" fill="var(--accent)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <p className="muted" style={{ marginTop: 12 }}>Click a row to see its 90-day trend.</p>

          <div className="card" style={{ padding: 0, overflow: "hidden", marginTop: 8 }}>
            <table>
              <thead>
                <tr>
                  <th>Location</th>
                  <th style={{ textAlign: "right" }}>Bad days</th>
                  <th style={{ textAlign: "right" }}>Max PM2.5</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.data.map((r) => (
                  <tr
                    key={r.location_id}
                    style={{
                      cursor: "pointer",
                      background: selectedId === r.location_id ? "var(--accent-bg)" : undefined,
                    }}
                    onClick={() => setSelectedId(r.location_id)}
                  >
                    <td>
                      <strong>{r.name}</strong>
                      {r.state ? <span className="muted">, {r.state}</span> : null}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <span className={`badge ${r.bad_days > 5 ? "bad" : r.bad_days > 0 ? "warn" : "good"}`}>
                        {r.bad_days}
                      </span>
                    </td>
                    <td style={{ textAlign: "right", fontFamily: "ui-monospace, monospace" }}>
                      {r.max_pm25?.toFixed(1) ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selectedId && trend.data && (
            <>
              <div className="section-title"><h3>90-day trend</h3></div>
              <div className="card" style={{ height: 280 }}>
                <ResponsiveContainer>
                  <LineChart data={trend.data}>
                    <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="day" stroke="var(--fg-muted)" fontSize={12} hide />
                    <YAxis stroke="var(--fg-muted)" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        background: "var(--surface)",
                        border: "1px solid var(--border)",
                        borderRadius: 8,
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="pm25_max"
                      stroke="var(--accent)"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
