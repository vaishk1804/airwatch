import { LineChart,Line,XAxis,YAxis,Tooltip,ResponsiveContainer } from "recharts";

export default function PM25Chart({data}:{data:{t:string;v:number}[]}){
return(
<div style={{width:"100%",height: 280}}>
<ResponsiveContainer>
  <LineChart data={data}>
<XAxis dataKey="t" hide></XAxis>
<YAxis/>
<Tooltip/>
<Line type="monotone" dataKey="v" dot={false}/>
  </LineChart>
</ResponsiveContainer>
</div>
);
}