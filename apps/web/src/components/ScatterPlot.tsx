import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function ScatterPlot({
  data,
  xKey,
  xLabel,
}: {
  data: Array<Record<string, number | null | string>>;
  xKey: "temp_c" | "rh" | "wind_kmh";
  xLabel: string;
}) {
  const points = data
    .filter((d) => d.pm25 != null && d[xKey] != null)
    .map((d) => ({ x: d[xKey] as number, y: d.pm25 as number }));

  return (
    <div style={{ width: "100%", height: 200 }}>
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="x"
            name={xLabel}
            stroke="var(--fg-muted)"
            fontSize={11}
            label={{ value: xLabel, position: "insideBottom", offset: -2, fontSize: 11, fill: "var(--fg-muted)" }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="PM2.5"
            stroke="var(--fg-muted)"
            fontSize={11}
          />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Scatter data={points} fill="var(--accent)" fillOpacity={0.7} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
