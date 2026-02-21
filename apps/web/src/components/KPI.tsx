export default function KPI({
  label,
  value,
  sub,
}:{
  label:string;
  value:string;
  sub?:string;
}){
  return(
    <div
    style={{
      border:"1px solid #ddd",
      borderRadius:12,
      padding:12,
      minWidth:160,
    }}>
      <div style={{fontSize:12,opacity:0.7}}>{label}</div>
      <div style={{ fontSize:22,fontWeight:600,marginTop:6}}>{value}</div>
      {sub && <div style={{fontSize:12,opacity:0.7,marginTop:4}}>{sub}</div>}
    </div>
  );
}