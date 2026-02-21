import { LineChart,Line,XAxis,YAxis,Tooltip,ResponsiveContainer } from "recharts";

export default function WeatherChart({
data,
} :{
data:{t:string;temp_c:number|null;rh:number|null;wind_kmh:number|null}[];
}){
  return(
    <div style={{width:"100%",height:200}}>
<ResponsiveContainer>
  <LineChart data={data}>
<XAxis dataKey="t" hide/>
<YAxis/>
<Tooltip/>
<Line type="monotone" dataKey="temp_c" dot={false}></Line>
<Line type = "monotone" dataKey="rh" dot={false}/>
<Line type="monotone" dataKey="wind_kmh" dot={false}/>
  </LineChart>
</ResponsiveContainer>
    </div>

  );
}