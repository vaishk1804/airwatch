import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

export default function ScatterPlot({
  data,
  xKey,
  xLabel,
}:{
  data:any[];
  xKey:"temp_c"|"rh"|"wind_kmh";
  xLabel:string;
}){
  const points = data.filter((d)=>d.pm25!=null &&d[xKey]!=null).map((d)=>({x:d[xKey],y:d.pm25}));

  return(
    <div style={{width:"100%",height:200}}>
      <ResponsiveContainer>
        <ScatterChart>
          <XAxis dataKey="x" name={xLabel}></XAxis>
          <YAxis dataKey="y" name="PM2.5"/>
          <Tooltip cursor={{strokeDasharray:"3 3"}}/>
          <Scatter data={points}/>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}