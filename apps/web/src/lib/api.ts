import type { Location } from "../types/location";

export const API_URL = import.meta.env.VITE_API_URL

export type PM25Point = { t: string; v:number;unit:string}

export type WeatherPoint = {t:string; temp_c:number|null;rh:number|null;wind_kmh:number|null}

export type Metrics = {
 latest: number | null;
 avg: number | null;
 max:number| null;
 bad_hours: number;
 count:number,
 threshold:number;
};

export type AlignedPoint = {
  t:string;
  pm25:number|null,
  temp_c: number|null;
  rh: number|null;
  wind_kmh: number|null;
};

export type CorrelationStat = {
  n:number;
  pearson_r:number|null;
};

export type DashboardResponse={
  location:Location;
  hours:number;
  pm25:PM25Point[];
  weather:WeatherPoint[];
  metrics: Metrics;
  aligned:AlignedPoint[];
  correlation:{
    temp_c: CorrelationStat;
    rh: CorrelationStat;
    wind_kmh:CorrelationStat;
  };
};

export type BadDaysRow = {
  location_id: number;
  name: string;
  state?: string | null;
  bad_days: number;
  max_pm25: number | null;
  window_days: number;
}

export type BadDayTrendRow= {day:string;bad_day:number; pm25_max:number|null};

export async function getHealth() {
  try {
    const res = await fetch(`${API_URL}/healthz`);
    if (!res.ok) throw new Error(`Health failed: ${res.status}`);
    return (await res.json()) as { status: string };
  } catch (e) {
    console.error("getHealth error:", e);
    throw e;
  }
}

export async function getReady() {
  const res = await fetch(`${API_URL}/readyz`);
  if (!res.ok) throw new Error(`Ready failed: ${res.status}`);
  return (await res.json()) as Promise<{ status: string; db: boolean }>;
}

export async function getLocations() {
  const res = await fetch(`${API_URL}/locations`);
  if(!res.ok) throw new Error('Locations failed: ${res.status}');
  return (await res.json()) as Location[];
}

export async function triggerAirIngest(hours = 24) {
  const res = await fetch(`${API_URL}/admin/ingest/air?hours=${hours}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Ingest failed: ${res.status}`);
  return res.json();
}

export async function getDashboard(locationId:number,hours: number, bad_threshold=25){
  const res = await fetch(`${API_URL}/dashboard/location/${locationId}?hours=${hours}&bad_threshold=${bad_threshold}`);
  if (!res.ok) throw new Error(`Dashboard failed: ${res.status}`);
  return (await res.json()) as DashboardResponse;
}

export async function getBadDays(days = 30){
  const res = await fetch(`${API_URL}/summary/bad-days?days=${days}`);
  if(!res.ok) throw new Error(`Bad-Days failed: ${res.status}`);
  return( await res.json()) as BadDaysRow[];
}

export async function getBadDaysTrend(locationId:number,days = 90){
  const res = await fetch(`${API_URL}/summary/bad-days-trend?location_id=${locationId}&days=${days}`);
  if(!res.ok) throw new Error(`Trend failed: ${res.status}`);
  return( await res.json()) as BadDayTrendRow[];
}