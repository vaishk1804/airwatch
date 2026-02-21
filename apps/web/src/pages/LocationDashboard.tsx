import { useParams ,Link} from "react-router-dom";
import {useMemo,useState} from "react";
import { useQuery } from "@tanstack/react-query";
import { getDashboard } from "../lib/api";
import PM25Chart from "../components/PM25Chart";
import WeatherChart from "../components/WeatherChart";
import KPI from "../components/KPI";
import ScatterPlot from "../components/ScatterPlot";

function fmt(n:number|null,digits=1){
  if(n==null) return -1;
  return n.toFixed(digits);
}

function corrLabel(r:number|null){
  if (r==null) return "n/a";
  const ar = Math.abs(r);
  if(ar>=0.7) return "strong";
  if(ar>=0.4) return "moderate";
  if(ar>=0.2) return "weak";
  return "none";
}

export default function LocationDashboard(){
  const {id} = useParams();
  const locationId = Number(id);

  const [hours,setHours] = useState<24|48|168>(24);
  const[badThreshold,setBadThreshold] = useState(35);

  const q = useQuery({
    queryKey: ["dashboard",locationId, hours,badThreshold],
    queryFn: () => getDashboard(locationId,hours,badThreshold),
    enabled: Number.isFinite(locationId) && locationId>0,
  });

  
  const unit = q.data?.pm25?.[0]?.unit ?? "µg/m³";
  const metrics=q.data?.metrics;

  const bestCorr = useMemo(()=>{
    const c = q.data?.correlation;
    if(!c) return null;
    const entries = [
      ["temp_c",c.temp_c.pearson_r],
      ["rh",c.rh.pearson_r],
      ["wind_kmh",c.wind_kmh.pearson_r]
    ] as const;

    type Entry = (typeof entries)[number];
    let best:Entry = entries[0];
    for (const e of entries){
      if(e[1]!=null && best[1]!=null){
        if(Math.abs(e[1])>Math.abs(best[1])) best = e;
      } else if (best[1]==null && e[1]!=null) {
        best = e;
      }
      }
      return best;
    
  },[q.data]);

  return(
    <div>
         <Link to="/">← Back</Link>
        <h2>
          {q.data?.location?.name ?? "Location"} Dashboard
        </h2>

      <div style={{display:"flex",gap:8,margin:"12px 0",flexWrap:"wrap"}}>
        <button onClick={()=>setHours(24)} disabled={hours === 24}>24h</button>
        <button onClick={()=>setHours(48)} disabled={hours === 48}>48h</button>
        <button onClick={()=>setHours(168)} disabled={hours===168}>7d</button>

        <div style={{marginLeft:12}}>
          <label style={{fontSize:12,opacity:0.7}} >Bad-air threshold(PM2.5)</label>
          <div>
            <input
            type="number"
            value={badThreshold}
            onChange={(e)=>setBadThreshold(Number(e.target.value))}
            />{" "}
            {unit}
          </div>
        </div>
      </div>

      {q.isLoading && <p>Loading Dashboard...</p>}
      {q.isError && <p style={{color: "crimson"}}>Failed to load dashbaord</p>}

      {q.data && metrics && (
        <>
        <div style={{display:"flex",gap:12,flexWrap:"wrap",margin:"12px 0"}}>
          <KPI label="Latest PM2.5" value={`${fmt(metrics.latest)} ${unit}`} />
          <KPI label="Avg (window)" value={`${fmt(metrics.avg)} ${unit}`} sub={`${metrics.count}`}/>
          <KPI label="Max (window)" value={`${fmt(metrics.max)} ${unit}`}/>
          <KPI label="Bad-air hours" value={`${metrics.bad_hours}`} sub={`≥ ${metrics.threshold} ${unit}`}/>
        </div>

        <h3>PM2.5</h3>
        {q.data.pm25.length===0?(
          <p> No PM2.5 points found for this window. (Try 7d or increase OpenAQ radius later.)</p>
        ):(
          <PM25Chart data={q.data.pm25.map((p)=>({t:p.t,v:p.v}))}></PM25Chart>
        )}

        <h3>Weather</h3>
        <WeatherChart data={q.data.weather}></WeatherChart>

        <h3>Correlation</h3>
        <p style={{marginTop:6}}>
          Best signal (by|r|):{" "}
          <b>{bestCorr ? `${bestCorr[0]} (r=${bestCorr[1]?.toFixed(2) ?? "n/a"}; ${corrLabel(bestCorr[1])})` : "n/a"}</b>
        </p>

<div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 16 }}>
            <div>
              <h4>PM2.5 vs Wind</h4>
              <ScatterPlot data={q.data.aligned} xKey="wind_kmh" xLabel="Wind (km/h)" />
              <p style={{ fontSize: 12, opacity: 0.7 }}>
                r={q.data.correlation.wind_kmh.pearson_r?.toFixed(2) ?? "n/a"} (n={q.data.correlation.wind_kmh.n})
              </p>
            </div>

            <div>
              <h4>PM2.5 vs Temperature</h4>
              <ScatterPlot data={q.data.aligned} xKey="temp_c" xLabel="Temp (°C)" />
              <p style={{ fontSize: 12, opacity: 0.7 }}>
                r={q.data.correlation.temp_c.pearson_r?.toFixed(2) ?? "n/a"} (n={q.data.correlation.temp_c.n})
              </p>
            </div>

            <div>
              <h4>PM2.5 vs Humidity</h4>
              <ScatterPlot data={q.data.aligned} xKey="rh" xLabel="Humidity (%)" />
              <p style={{ fontSize: 12, opacity: 0.7 }}>
                r={q.data.correlation.rh.pearson_r?.toFixed(2) ?? "n/a"} (n={q.data.correlation.rh.n})
              </p>
            </div>
          </div>
          
        </>
      )

      }

    </div>
  );
}