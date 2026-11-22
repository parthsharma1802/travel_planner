import React, { useEffect } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import { Navigation, MapPin, Clock, Route as RouteIcon, ExternalLink } from "lucide-react";
import "leaflet/dist/leaflet.css";

// Helper component to auto-fit map bounds around polyline/markers
function AutoFitBounds({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points && points.length > 0) {
      const bounds = L.latLngBounds(points);
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [points, map]);
  return null;
}

// Create custom numbered Leaflet marker icon
const createNumberedIcon = (number, isOrigin = false) => {
  const bgColor = isOrigin ? "#0070f3" : "#171717";
  const html = `
    <div style="
      background-color: ${bgColor};
      color: white;
      border: 2px solid white;
      border-radius: 50%;
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 12px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
      font-family: sans-serif;
    ">
      ${number}
    </div>
  `;
  return L.divIcon({
    html,
    className: "custom-leaflet-marker",
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });
};

export default function RouteMapWidget({ routeData }) {
  if (!routeData || !routeData.geometry) return null;

  const origin = routeData.origin;
  const stops = routeData.stops || [];
  const legs = routeData.legs || [];
  const polylinePoints = routeData.geometry || [];

  const allMarkers = [origin, ...stops];
  const mapCenter = [origin.lat, origin.lon];

  return (
    <div className="mt-4 vercel-card p-4 text-left w-full bg-white dark:bg-[#111111] border border-[#ebebeb] dark:border-[#222222] rounded-[14px]">
      {/* Widget Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#ebebeb] dark:border-[#222222] mb-3 gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <RouteIcon className="w-5 h-5 text-[#0070f3]" />
            <h4 className="font-semibold text-base text-[#171717] dark:text-white">
              Interactive Road Route & Itinerary Map
            </h4>
          </div>
          <p className="text-xs text-[#8f8f8f] mt-0.5">
            Total Distance: <span className="font-semibold text-[#171717] dark:text-white">{routeData.total_distance_km} km</span> • Total Drive: <span className="font-semibold text-[#171717] dark:text-white">{routeData.total_duration_text}</span>
          </p>
        </div>

        {/* External Google Maps Navigation Action */}
        <a
          href={routeData.google_maps_url}
          target="_blank"
          rel="noopener noreferrer"
          className="vercel-btn-pill flex items-center space-x-2 !py-2 !px-3.5 text-xs text-white shrink-0 self-start sm:self-auto shadow-sm hover:opacity-90 transition-opacity"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          <span>Open in Google Maps</span>
        </a>
      </div>

      {/* Leaflet Interactive Map Canvas */}
      <div className="w-full h-80 sm:h-96 rounded-[12px] overflow-hidden border border-[#ebebeb] dark:border-[#222222] relative z-10">
        <MapContainer
          center={mapCenter}
          zoom={6}
          scrollWheelZoom={false}
          className="w-full h-full"
        >
          {/* OpenStreetMap Tile Layer */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | OSRM Routing'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* OSRM Road Polyline */}
          <Polyline
            positions={polylinePoints}
            pathOptions={{ color: "#0070f3", weight: 4, opacity: 0.85 }}
          />

          {/* Sequential Numbered Location Markers */}
          {allMarkers.map((loc, idx) => (
            <Marker
              key={`${loc.name}-${idx}`}
              position={[loc.lat, loc.lon]}
              icon={createNumberedIcon(idx + 1, idx === 0)}
            >
              <Popup className="custom-leaflet-popup">
                <div className="p-1 font-sans">
                  <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-800">
                    Stop {idx + 1}: {idx === 0 ? "Origin" : "Destination"}
                  </span>
                  <h5 className="font-semibold text-sm mt-1">{loc.name}</h5>
                  <p className="text-xs text-gray-600 mt-0.5">{loc.display_name}</p>
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(loc.display_name)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1 text-xs text-blue-600 hover:underline mt-2 font-medium"
                  >
                    <span>View on Google Maps</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </Popup>
            </Marker>
          ))}

          <AutoFitBounds points={polylinePoints} />
        </MapContainer>
      </div>

      {/* Sequential Route Legs Breakdown */}
      <div className="mt-4 space-y-2">
        <p className="font-mono-eyebrow text-[#8f8f8f]">Driving Legs & Distance Breakdown</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {legs.map((leg, idx) => (
            <div key={idx} className="p-3 bg-[#fafafa] dark:bg-[#171717] rounded-[8px] border border-[#ebebeb] dark:border-[#222222] text-xs">
              <div className="flex items-center space-x-1.5 font-semibold text-[#171717] dark:text-white truncate">
                <MapPin className="w-3.5 h-3.5 text-[#0070f3] shrink-0" />
                <span className="truncate">{leg.from_name} ➔ {leg.to_name}</span>
              </div>
              <div className="flex items-center justify-between mt-2 text-[#4d4d4d] dark:text-[#a1a1a1] text-[11px]">
                <span>Distance: <strong className="text-[#171717] dark:text-white">{leg.distance_km} km</strong></span>
                <span className="flex items-center space-x-1">
                  <Clock className="w-3 h-3 opacity-60" />
                  <strong className="text-[#171717] dark:text-white">{leg.duration_text}</strong>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
