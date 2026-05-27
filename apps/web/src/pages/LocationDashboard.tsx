import { useParams, Link } from "react-router-dom";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getDashboard } from "../lib/api";
import PM25Chart from "../components/PM25Chart";
import WeatherChart from "../components/WeatherChart";
import KPI from "../components/KPI";
import ScatterPlot from "../components/ScatterPlot";

function fmt(n: number | null | undefined, digits = 1) {
  if (n == null) return "—";
  return n.toFixed(digits);
}

function corrLabel(r: number | null) {
  if (r == null) return "n/a";
  const ar = Math.abs(r);
  if (ar >= 0.7) return "strong";
  if (ar >= 0.4) return "moderate";
  if (ar >= 0.2) return "weak";
  return "none";
}

const WINDOW_OPTS: Array<{ label: string; hours: 24 | 48 | 168 }> = [
  { label: "24h", hours: 24 },
  { label: "48h", hours: 48 },
  { label: "7d", hours: 168 },
];

type AQIInfo = { aqi: number; band: string; color: string; advice: string };

function AQIHero({ info, unit }: { info: AQIInfo | null | undefined; unit: string }) {
  if (!info) {
    return (
      <div className="card" style={{ padding: 20, marginBottom: 16 }}>
        <div className="muted">No recent readings — AQI unavailable.</div>
      </div>
    );
  }
  return (
    <div
      style={{
        background: `linear-gradient(135deg, ${info.color}33, ${info.color}11)`,
        border: `1px solid ${info.color}55`,
        borderLeft: `4px solid ${info.color}`,
        borderRadius: "var(--radius-lg)",
        padding: 20,
        marginBottom: 16,
        boxShadow: "var(--shadow-sm)",
      }}
    >
      <div style={{ display: "flex", alignItems: "baseline", gap: 16, flexWrap: "wrap" }}>
        <div
          style={{
            fontSize: 56,
            fontWeight: 800,
            lineHeight: 1,
            color: info.color,
            textShadow: "0 1px 2px rgba(0,0,0,0.15)",
          }}
        >
          {info.aqi}
        </div>
        <div style={{ flex: 1, minWidth: 200 }}>
          <div
            style={{
              fontSize: 11,
              color: "var(--fg-muted)",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
            }}
          >
            Current AQI · PM2.5
          </div>
          <div style={{ fontSize: 22, fontWeight: 700, marginTop: 4, color: "var(--fg)" }}>
            {info.band}
          </div>
          <div style={{ fontSize: 13, color: "var(--fg-muted)", marginTop: 6, maxWidth: 600 }}>
            {info.advice}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LocationDashboard() {
  const { id } = useParams();
  const locationId = Number(id);

  const [hours, setHours] = useState<24 | 48 | 168>(24);
  const [badThreshold, setBadThreshold] = useState(35);

  const q = useQuery({
    queryKey: ["dashboard", locationId, hours, badThreshold],
    queryFn: () => getDashboard(locationId, hours, badThreshold),
    enabled: Number.isFinite(locationId) && locationId > 0,
  });

  const unit = q.data?.pm25?.[0]?.unit ?? "µg/m³";
  const metrics = q.data?.metrics;
  const aqi = q.data?.aqi;

  const bestCorr = useMemo(() => {
    const c = q.data?.correlation;
    if (!c) return null;
    const entries = [
      ["temp_c", c.temp_c.pearson_r],
      ["rh", c.rh.pearson_r],
      ["wind_kmh", c.wind_kmh.pearson_r],
    ] as const;

    type Entry = (typeof entries)[number];
    let best: Entry = entries[0];
    for (const e of entries) {
      if (e[1] != null && best[1] != null) {
        if (Math.abs(e[1]) > Math.abs(best[1])) best = e;
      } else if (best[1] == null && e[1] != null) {
        best = e;
      }
    }
    return best;
  }, [q.data]);

  return (
    <div>
      <Link to="/" className="back-link">← Back to locations</Link>
      <div className="section-title">
        <h1>{q.data?.location?.name ?? "Location"}</h1>
        {q.data?.location?.state && (
          <span className="muted">{q.data.location.state}, {q.data.location.country}</span>
        )}
      </div>

      {/* AQI hero — the headline number */}
      {q.data && <AQIHero info={aqi?.latest as AQIInfo | null | undefined} unit={unit} />}

      <div className="toolbar">
        {WINDOW_OPTS.map((opt) => (
          <button
            key={opt.hours}
            onClick={() => setHours(opt.hours)}
            disabled={hours === opt.hours}
            className={hours === opt.hours ? "primary" : ""}
          >
            {opt.label}
          </button>
        ))}
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
          <label>Bad-air threshold</label>
          <input
            type="number"
            value={badThreshold}
            onChange={(e) => setBadThreshold(Number(e.target.value))}
            style={{ width: 80 }}
          />
          <span className="muted">{unit}</span>
        </div>
      </div>

      {q.isLoading && <p className="muted">Loading dashboard...</p>}
      {q.isError && <p style={{ color: "var(--bad)" }}>Failed to load dashboard.</p>}

      {q.data && metrics && (
        <>
          <div className="kpi-row">
            <KPI label="Latest PM2.5" value={`${fmt(metrics.latest)} ${unit}`} />
            <KPI label="Avg (window)" value={`${fmt(metrics.avg)} ${unit}`} sub={`${metrics.count} samples`} />
            <KPI label="Max (window)" value={`${fmt(metrics.max)} ${unit}`} />
            <KPI
              label="Bad-air hours"
              value={`${metrics.bad_hours}`}
              sub={`≥ ${metrics.threshold} ${unit}`}
              tone={metrics.bad_hours > 0 ? "warn" : "good"}
            />
          </div>

          <div className="section-title"><h3>PM2.5 over time</h3></div>
          <div className="card">
            {q.data.pm25.length === 0 ? (
              <p className="muted">No PM2.5 points found for this window. Try expanding to 7d.</p>
            ) : (
              <PM25Chart data={q.data.pm25.map((p) => ({ t: p.t, v: p.v }))} threshold={badThreshold} />
            )}
          </div>

          <div className="section-title"><h3>Weather</h3></div>
          <div className="card">
            <WeatherChart data={q.data.weather} />
          </div>

          <div className="section-title">
            <h3>Correlation with weather</h3>
            <span className="muted">
              Best signal:{" "}
              <strong>
                {bestCorr
                  ? `${bestCorr[0]} (r=${bestCorr[1]?.toFixed(2) ?? "n/a"}; ${corrLabel(bestCorr[1])})`
                  : "n/a"}
              </strong>
            </span>
          </div>

          <div className="scatter-grid">
            <div className="card">
              <h4>PM2.5 vs Wind</h4>
              <ScatterPlot data={q.data.aligned} xKey="wind_kmh" xLabel="Wind (km/h)" />
              <p className="muted" style={{ marginTop: 4 }}>
                r={q.data.correlation.wind_kmh.pearson_r?.toFixed(2) ?? "n/a"} (n={q.data.correlation.wind_kmh.n})
              </p>
            </div>

            <div className="card">
              <h4>PM2.5 vs Temperature</h4>
              <ScatterPlot data={q.data.aligned} xKey="temp_c" xLabel="Temp (°C)" />
              <p className="muted" style={{ marginTop: 4 }}>
                r={q.data.correlation.temp_c.pearson_r?.toFixed(2) ?? "n/a"} (n={q.data.correlation.temp_c.n})
              </p>
            </div>

            <div className="card">
              <h4>PM2.5 vs Humidity</h4>
              <ScatterPlot data={q.data.aligned} xKey="rh" xLabel="Humidity (%)" />
              <p className="muted" style={{ marginTop: 4 }}>
                r={q.data.correlation.rh.pearson_r?.toFixed(2) ?? "n/a"} (n={q.data.correlation.rh.n})
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}