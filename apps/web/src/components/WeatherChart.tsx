import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
} from "recharts";

export default function WeatherChart({
  data,
}: {
  data: { t: string; temp_c: number | null; rh: number | null; wind_kmh: number | null }[];
}) {
  return (
    <div style={{ width: "100%", height: 240 }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="t" stroke="var(--fg-muted)" fontSize={11} hide />
          <YAxis stroke="var(--fg-muted)" fontSize={11} />
          <Tooltip
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelFormatter={(t) => new Date(t).toLocaleString()}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line type="monotone" dataKey="temp_c" name="Temp (°C)" stroke="#dc2626" strokeWidth={1.5} dot={false} />
          <Line type="monotone" dataKey="rh" name="Humidity (%)" stroke="#2563eb" strokeWidth={1.5} dot={false} />
          <Line type="monotone" dataKey="wind_kmh" name="Wind (km/h)" stroke="#16a34a" strokeWidth={1.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
