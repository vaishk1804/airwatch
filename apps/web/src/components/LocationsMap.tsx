import { useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import { Link } from "react-router-dom";

export type MapPoint = {
  id: number;
  name: string;
  state: string | null;
  country: string;
  lat: number;
  lon: number;
  pm25: number | null;
  aqi: number | null;
  band: string;
  color: string;
};

/** Pan/zoom the map to fit all points whenever the dataset changes. */
function FitBounds({ points }: { points: MapPoint[] }) {
  const map = useMap();
  useEffect(() => {
    if (points.length === 0) return;
    if (points.length === 1) {
      map.setView([points[0].lat, points[0].lon], 8);
      return;
    }
    const bounds = points.map((p) => [p.lat, p.lon] as [number, number]);
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 7 });
  }, [points, map]);
  return null;
}

export default function LocationsMap({ points }: { points: MapPoint[] }) {
  if (points.length === 0) {
    return (
      <div className="card" style={{ padding: 20 }}>
        <p className="muted">No locations to display.</p>
      </div>
    );
  }

  // Initial center/zoom — FitBounds will override once mounted.
  const center: [number, number] = [points[0].lat, points[0].lon];

  return (
    <div
      className="card"
      style={{ padding: 0, overflow: "hidden", height: 420 }}
    >
      <MapContainer
        center={center}
        zoom={4}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%", background: "var(--surface-2)" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <FitBounds points={points} />
        {points.map((p) => (
          <CircleMarker
            key={p.id}
            center={[p.lat, p.lon]}
            radius={p.aqi != null ? 12 : 8}
            pathOptions={{
              color: p.color,
              fillColor: p.color,
              fillOpacity: p.aqi != null ? 0.7 : 0.35,
              weight: 2,
            }}
          >
            <Popup>
              <div style={{ minWidth: 180 }}>
                <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
                  {p.name}
                  {p.state ? <span style={{ fontWeight: 400, color: "#666" }}>, {p.state}</span> : null}
                </div>
                {p.aqi != null ? (
                  <>
                    <div
                      style={{
                        display: "inline-block",
                        padding: "2px 8px",
                        borderRadius: 999,
                        background: p.color,
                        color: p.aqi >= 150 ? "#fff" : "#000",
                        fontWeight: 700,
                        fontSize: 12,
                        marginBottom: 6,
                      }}
                    >
                      AQI {p.aqi} · {p.band}
                    </div>
                    <div style={{ fontSize: 12, color: "#555" }}>
                      PM2.5: {p.pm25?.toFixed(1)} µg/m³
                    </div>
                  </>
                ) : (
                  <div style={{ fontSize: 12, color: "#888" }}>No recent readings</div>
                )}
                <div style={{ marginTop: 8 }}>
                  <Link to={`/location/${p.id}`} style={{ fontSize: 12 }}>
                    View dashboard →
                  </Link>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}