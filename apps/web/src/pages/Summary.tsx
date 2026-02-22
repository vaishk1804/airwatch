import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getBadDays, getBadDaysTrend } from "../lib/api";
import { ResponsiveContainer,BarChart,Bar,XAxis,YAxis,Tooltip,LineChart,Line } from "recharts";

export default function Summary(){
  const [windowDays,setWindowDays]=useState<30|90>(30)
  const [selectedId,setSelectedId] = useState<number|null>(null);

  const leaderboard = useQuery({
    queryKey:["badDays",windowDays],
    queryFn:()=> getBadDays(windowDays),
  });

  const trend = useQuery({
    queryKey:["badDaysTrend",selectedId],
    queryFn:()=>getBadDaysTrend(selectedId!,90),
    enabled:selectedId!=null,
  });
  const top = leaderboard.data?.slice(0,8)?? []

  return(
    <div>
      <Link to="/">Back</Link>
      <h2> Executive Summary</h2>

      <div style={{ display: "flex", gap: 8, margin: "12px 0" }}>
        <button onClick={() => setWindowDays(30)} disabled={windowDays === 30}>Last 30d</button>
        <button onClick={() => setWindowDays(90)} disabled={windowDays === 90}>Last 90d</button>
      </div>

      {leaderboard.isLoading && <p>Loading summary...</p>}
      {leaderboard.isError && <p style={{ color: "crimson" }}>Failed to load summary</p>}

      {leaderboard.data && (
        <>
          <h3>Bad-air days leaderboard</h3>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={top}>
                <XAxis dataKey="name" hide />
                <YAxis />
                <Tooltip />
                <Bar dataKey="bad_days" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <p style={{ fontSize: 12, opacity: 0.7 }}>
            Click a row below to see trend
          </p>

           <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">Location</th>
                <th align="right">Bad days</th>
                <th align="right">Max PM2.5</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.data.map((r) => (
                <tr
                  key={r.location_id}
                  style={{ cursor: "pointer" }}
                  onClick={() => setSelectedId(r.location_id)}
                >
                  <td>{r.name}{r.state ? `, ${r.state}` : ""}</td>
                  <td align="right">{r.bad_days}</td>
                  <td align="right">{r.max_pm25?.toFixed(1) ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>

{selectedId && trend.data && (
            <>
              <h3 style={{ marginTop: 16 }}>Bad-air trend (last 90 days)</h3>
              <div style={{ width: "100%", height: 280 }}>
                <ResponsiveContainer>
                  <LineChart data={trend.data}>
                    <XAxis dataKey="day" hide />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="bad_day" dot={false} />
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