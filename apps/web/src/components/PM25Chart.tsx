import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
} from "recharts";

// EPA AQI breakpoint upper bounds (PM2.5 µg/m³), matched with band colors.
// Each band fills the chart background between [lo, hi].
const AQI_BANDS = [
  { lo: 0,     hi: 12.0,  color: "#00e400", label: "Good" },
  { lo: 12.0,  hi: 35.4,  color: "#ffff00", label: "Moderate" },
  { lo: 35.4,  hi: 55.4,  color: "#ff7e00", label: "USG" },
  { lo: 55.4,  hi: 150.4, color: "#ff0000", label: "Unhealthy" },
  { lo: 150.4, hi: 250.4, color: "#8f3f97", label: "Very Unhealthy" },
  { lo: 250.4, hi: 500.4, color: "#7e0023", label: "Hazardous" },
];

export default function PM25Chart({
  data,
  threshold = 35,
}: {
  data: { t: string; v: number }[];
  threshold?: number;
}) {
  // Chart Y-axis upper bound: snap to just above the data's max, but never lower
  // than 50 (so the Good/Moderate boundary is always visible for context).
  const maxV = data.reduce((m, d) => (d.v > m ? d.v : m), 0);
  const yMax = Math.max(50, Math.ceil(maxV * 1.15));

  // Only draw bands that fall within the visible range — keeps the legend clean.
  const visibleBands = AQI_BANDS.filter((b) => b.lo < yMax);

  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="t" stroke="var(--fg-muted)" fontSize={11} hide />
          <YAxis stroke="var(--fg-muted)" fontSize={11} domain={[0, yMax]} />

          {/* AQI band reference zones, rendered behind the data line */}
          {visibleBands.map((b) => (
            <ReferenceArea
              key={b.label}
              y1={b.lo}
              y2={Math.min(b.hi, yMax)}
              fill={b.color}
              fillOpacity={0.10}
              ifOverflow="hidden"
            />
          ))}

          <Tooltip
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelFormatter={(t) => new Date(t).toLocaleString()}
            formatter={(v) => [`${typeof v === "number" ? v.toFixed(1) : v} µg/m³`, "PM2.5"]}
          />

          {/* User-configurable threshold marker, drawn on top of the bands */}
          <ReferenceLine
            y={threshold}
            stroke="var(--fg)"
            strokeDasharray="4 4"
            strokeOpacity={0.4}
            label={{
              value: `Threshold ${threshold}`,
              fill: "var(--fg-muted)",
              fontSize: 10,
              position: "insideTopRight",
            }}
          />

          <Line
            type="monotone"
            dataKey="v"
            stroke="var(--fg)"
            strokeWidth={2.2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}