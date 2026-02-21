from __future__ import annotations
from typing import List,Dict,Optional,Tuple
from math import sqrt

def summarize_pm25(pm25: List[dict],bad_threshold: float=35.0)->dict:
  """
  pm25 : [{t,v,unit}]
  """

  values=[p["v"] for p in pm25 if p.get("v") is not None]
  if not values:
    return{
      "latest":None,
      "avg":None,
      "max":None,
      "bad_hours":0,
      "count":0,
      "threshold":bad_threshold,
    }
  
  latest=values[-1]
  avg=sum(values)/len(values)
  mx=max(values)
  bad_hours=sum(1 for v in values if v>=bad_threshold)

  return{
    "latest": float(latest),
    "avg": float(avg),
    "max": float(mx),
    "bad_hours": int(bad_hours),
    "count":int(len(values)),
    "threshold":float(bad_threshold),
  }

def _pearson(xs:List[float],ys:List[float])-> Optional[float]:
  n=len(xs)
  if n<3:
    return None
  
  mean_x=sum(xs)/n
  mean_y=sum(ys)/n
  num=sum((x-mean_x)*(y-mean_y) for x,y in zip(xs,ys))
  den_x=sqrt(sum((x-mean_x)**2 for x in xs))
  den_y=sqrt(sum((y-mean_y)**2 for y in ys))
  if den_x==0 or den_y ==0:
    return None
  return float(num/(den_x*den_y))

def align_series_by_time(
    pm25: List[dict],
    weather: List[dict],
)-> List[dict]:
  w_map: Dict[str,dict] = {w["t"]: w for w in weather if w.get("t")}
  rows=[]
  for p in pm25:
    t= p.get("t")
    if not t or t not in w_map:
      continue
    w = w_map.get(t)
    if not w:
      continue
    
    rows.append({
      "t":t,
      "pm25":p.get("v"),
      "temp_c":w.get("temp_c"),
      "rh":w.get("rh"),
      "wind_kmh":w.get("wind_kmh"),
    })
  return rows

def correlation_insights(rows:List[dict])->dict:

  def extract(key:str)->Tuple[List[float],List[float]]:
    xs,ys=[],[]
    for r in rows:
      pm=r.get("pm25")
      x=r.get(key)
      if pm is None or x is None:
        continue
      ys.append(float(pm))
      xs.append(float(x))
    return xs,ys
  
  out ={}
  for key in ["temp_c","rh","wind_kmh"]:
    xs,ys=extract(key)
    out[key]={
      "n":len(xs),
      "pearson_r"
: _pearson(xs,ys)
    }
  return out


