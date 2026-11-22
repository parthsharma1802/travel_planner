import React from "react";
import {
  MapPin, Clock, Car, Train, Plane, Navigation, Sun, CloudRain,
  Star, ChevronRight, ArrowDown, Compass, Users, Calendar, DollarSign,
  Coffee, Moon, Sunrise, Sunset, Building, Map, Info, Hotel, ShieldCheck, CheckCircle2
} from "lucide-react";

// Transport icon selector
function TransportIcon({ mode, className = "w-4 h-4" }) {
  if (!mode) return <Car className={className} />;
  const m = mode.toLowerCase();
  if (m.includes("train")) return <Train className={className} />;
  if (m.includes("flight") || m.includes("air")) return <Plane className={className} />;
  return <Car className={className} />;
}

// Route visual spine between stops
function RouteSpine({ legs }) {
  if (!legs || legs.length === 0) return null;
  const stops = legs.length > 0 ? [legs[0].from, ...legs.map(l => l.to)] : [];
  return (
    <div className="flex flex-col items-start space-y-0 text-sm">
      {stops.map((stop, idx) => (
        <React.Fragment key={idx}>
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full border-2 shrink-0 ${idx === 0 ? "bg-[#0070f3] border-[#0070f3]" : idx === stops.length - 1 ? "bg-emerald-500 border-emerald-500" : "bg-white dark:bg-[#171717] border-[#0070f3]"}`} />
            <span className="font-semibold text-[#171717] dark:text-white">{stop}</span>
          </div>
          {idx < legs.length && (
            <div className="flex items-start space-x-3 ml-1.5 py-1">
              <div className="w-0 border-l-2 border-dashed border-[#0070f3]/40 h-8 mx-auto" />
              <div className="text-xs text-[#8f8f8f] pt-1 font-mono">
                {legs[idx].distance_km ? `${legs[idx].distance_km} km` : "—"} · {legs[idx].duration_text || "—"}
              </div>
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

// Single day card
function DayCard({ day }) {
  return (
    <div className="border border-[#ebebeb] dark:border-[#222222] rounded-[12px] overflow-hidden bg-white dark:bg-[#111111]">
      {/* Day Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-[#0070f3]/10 to-blue-50/30 dark:from-[#0070f3]/10 dark:to-blue-900/10 border-b border-[#ebebeb] dark:border-[#222222] flex items-center justify-between">
        <div>
          <span className="text-[11px] font-mono font-semibold text-[#0070f3] uppercase tracking-wider">{day.label || `Day ${day.day}`}</span>
          <h3 className="font-bold text-base text-[#171717] dark:text-white mt-0.5">{day.title}</h3>
        </div>
        {day.drive && (
          <div className="flex items-center space-x-1.5 text-xs bg-white/80 dark:bg-[#1c1c1c]/80 border border-[#ebebeb] dark:border-[#333333] px-3 py-1.5 rounded-full">
            <Car className="w-3.5 h-3.5 text-[#0070f3]" />
            <span className="font-mono text-[#171717] dark:text-white font-medium">
              {day.drive.distance_km ? `${day.drive.distance_km} km` : ""}{day.drive.distance_km && day.drive.duration_text ? " · " : ""}{day.drive.duration_text || ""}
            </span>
          </div>
        )}
      </div>

      <div className="p-4 space-y-3">
        {/* Drive route note */}
        {day.drive?.route_note && (
          <div className="flex items-start space-x-2 text-xs text-[#8f8f8f]">
            <Navigation className="w-3.5 h-3.5 shrink-0 mt-0.5 text-[#0070f3]" />
            <span>{day.drive.route_note}</span>
          </div>
        )}

        {/* Timeline: Morning / Afternoon / Evening */}
        <div className="space-y-2">
          {day.morning && (
            <div className="flex items-start space-x-3">
              <div className="flex items-center space-x-1 shrink-0 w-20">
                <Sunrise className="w-3.5 h-3.5 text-amber-400" />
                <span className="text-[10px] font-mono text-[#8f8f8f] uppercase">Morning</span>
              </div>
              <p className="text-sm text-[#4d4d4d] dark:text-[#a1a1a1] flex-1">{day.morning}</p>
            </div>
          )}
          {day.afternoon && (
            <div className="flex items-start space-x-3">
              <div className="flex items-center space-x-1 shrink-0 w-20">
                <Sun className="w-3.5 h-3.5 text-orange-400" />
                <span className="text-[10px] font-mono text-[#8f8f8f] uppercase">Afternoon</span>
              </div>
              <p className="text-sm text-[#4d4d4d] dark:text-[#a1a1a1] flex-1">{day.afternoon}</p>
            </div>
          )}
          {day.evening && (
            <div className="flex items-start space-x-3">
              <div className="flex items-center space-x-1 shrink-0 w-20">
                <Sunset className="w-3.5 h-3.5 text-purple-400" />
                <span className="text-[10px] font-mono text-[#8f8f8f] uppercase">Evening</span>
              </div>
              <p className="text-sm text-[#4d4d4d] dark:text-[#a1a1a1] flex-1">{day.evening}</p>
            </div>
          )}
        </div>

        {/* Highlights */}
        {day.highlights && day.highlights.length > 0 && (
          <div>
            <p className="text-[10px] font-mono text-[#8f8f8f] uppercase tracking-wider mb-1.5">Explore</p>
            <div className="flex flex-wrap gap-2">
              {day.highlights.map((h, i) => (
                <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-[#fafafa] dark:bg-[#1c1c1c] border border-[#ebebeb] dark:border-[#333333] text-[#171717] dark:text-white font-medium">
                  {h}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Weather note */}
        {day.weather_note && (
          <div className="flex items-start space-x-2 p-2.5 bg-blue-50/60 dark:bg-blue-900/20 rounded-[8px] border border-blue-100 dark:border-blue-900/30 text-xs">
            <CloudRain className="w-3.5 h-3.5 shrink-0 mt-0.5 text-blue-500" />
            <span className="text-[#4d4d4d] dark:text-[#a1a1a1]">{day.weather_note}</span>
          </div>
        )}

        {/* Stay area */}
        {day.stay_area && (
          <div className="pt-2 border-t border-[#ebebeb] dark:border-[#222222]">
            <div className="flex items-start space-x-2">
              <Building className="w-4 h-4 shrink-0 mt-0.5 text-[#8f8f8f]" />
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-semibold text-[#171717] dark:text-white">Recommended Stay Area</span>
                  {day.stay_placeholder && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300 font-mono">Hotels coming soon</span>
                  )}
                </div>
                <p className="text-xs text-[#0070f3] font-semibold mt-0.5">{day.stay_area}</p>
                {day.stay_reason && <p className="text-xs text-[#8f8f8f] mt-0.5">{day.stay_reason}</p>}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ItineraryCard({ itinerary, routeData, selectedHotel, selectedFlight, selectedTrain }) {
  if (!itinerary) return null;

  const { overview, route_summary, days, summary } = itinerary;

  // Build route legs from either itinerary data or OSRM route_data
  const routeLegs = route_summary && route_summary.length > 0
    ? route_summary.map(l => ({ from: l.from, to: l.to, distance_km: l.distance_km, duration_text: l.duration_text }))
    : routeData?.legs?.map(l => ({ from: l.from_name, to: l.to_name, distance_km: l.distance_km, duration_text: l.duration_text })) || [];

  return (
    <div className="mt-4 w-full space-y-4 text-left">
      {/* OVERVIEW CARD */}
      {overview && (
        <div className="vercel-card p-5 bg-gradient-to-br from-[#0070f3]/5 to-indigo-50/30 dark:from-[#0070f3]/10 dark:to-indigo-900/10 border-[#0070f3]/20 dark:border-[#0070f3]/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-[#171717] dark:text-white">{overview.title}</h2>
              <p className="text-sm text-[#8f8f8f] mt-0.5">
                {[overview.origin, overview.destination].filter(Boolean).join(" → ")}
                {overview.dates && ` · ${overview.dates}`}
              </p>
            </div>
            <div className="text-right text-xs font-mono text-[#8f8f8f]">
              {overview.duration && <p className="font-semibold text-[#171717] dark:text-white">{overview.duration}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
            {overview.origin && (
              <div className="flex items-center space-x-2">
                <MapPin className="w-3.5 h-3.5 text-[#0070f3] shrink-0" />
                <div><p className="text-[#8f8f8f]">Starting From</p><p className="font-semibold text-[#171717] dark:text-white">{overview.origin}</p></div>
              </div>
            )}
            {overview.travelers && (
              <div className="flex items-center space-x-2">
                <Users className="w-3.5 h-3.5 text-[#0070f3] shrink-0" />
                <div><p className="text-[#8f8f8f]">Travelers</p><p className="font-semibold text-[#171717] dark:text-white">{overview.travelers}</p></div>
              </div>
            )}
            {overview.transport && (
              <div className="flex items-center space-x-2">
                <TransportIcon mode={overview.transport} className="w-3.5 h-3.5 text-[#0070f3] shrink-0" />
                <div><p className="text-[#8f8f8f]">Transport</p><p className="font-semibold text-[#171717] dark:text-white">{overview.transport}</p></div>
              </div>
            )}
            {overview.budget && (
              <div className="flex items-center space-x-2">
                <DollarSign className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                <div><p className="text-[#8f8f8f]">Budget</p><p className="font-semibold text-[#171717] dark:text-white">{overview.budget}</p></div>
              </div>
            )}
            {overview.style && (
              <div className="flex items-center space-x-2">
                <Compass className="w-3.5 h-3.5 text-purple-500 shrink-0" />
                <div><p className="text-[#8f8f8f]">Style</p><p className="font-semibold text-[#171717] dark:text-white">{overview.style}</p></div>
              </div>
            )}
            {overview.experiences && overview.experiences.length > 0 && (
              <div className="flex items-start space-x-2 col-span-2 sm:col-span-1">
                <Star className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                <div><p className="text-[#8f8f8f]">Experiences</p><p className="font-semibold text-[#171717] dark:text-white">{overview.experiences.join(", ")}</p></div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SELECTED BOOKINGS & COST FLOW INTEGRATION */}
      {(selectedHotel || selectedFlight || selectedTrain) && (
        <div className="vercel-card p-4 bg-gradient-to-br from-emerald-50/50 via-white to-sky-50/40 dark:from-[#0f1d16] dark:via-[#111827] dark:to-[#0f1924] border-emerald-300/70 dark:border-emerald-900/60 shadow-xs">
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-black/5 dark:border-white/10">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <h3 className="font-bold text-sm text-[#171717] dark:text-white">Selected Stay & Transport Integration</h3>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 font-semibold">
              Indicative / Live Fares
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            {selectedHotel && (
              <div className="p-3 rounded-[8px] bg-white dark:bg-[#18231c] border border-emerald-200 dark:border-emerald-800/40">
                <div className="flex items-center space-x-2 text-emerald-700 dark:text-emerald-400 font-semibold mb-1">
                  <Hotel className="w-3.5 h-3.5" />
                  <span>Selected Stay</span>
                </div>
                <p className="font-bold text-[#171717] dark:text-white text-xs">{selectedHotel.hotel_name}</p>
                <div className="mt-1 flex items-center justify-between text-[11px] text-[#71717a] dark:text-[#a1a1aa]">
                  <span>Indicative stay cost:</span>
                  <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">₹{(selectedHotel.price_inr || 0).toLocaleString("en-IN")}/night</span>
                </div>
                <p className="text-[10px] text-[#8f8f8f] mt-0.5">Best vendor: {selectedHotel.best_vendor || "Booking.com"}</p>
              </div>
            )}

            {(selectedFlight || selectedTrain) && (
              <div className="p-3 rounded-[8px] bg-white dark:bg-[#18202b] border border-sky-200 dark:border-sky-800/40">
                <div className="flex items-center space-x-2 text-sky-700 dark:text-sky-400 font-semibold mb-1">
                  {selectedFlight ? <Plane className="w-3.5 h-3.5" /> : <Train className="w-3.5 h-3.5" />}
                  <span>Selected Transport</span>
                </div>
                <p className="font-bold text-[#171717] dark:text-white text-xs">
                  {selectedFlight ? `${selectedFlight.airline} ${selectedFlight.flight_number}` : `${selectedTrain.train_name} (#${selectedTrain.train_number})`}
                </p>
                <div className="mt-1 flex items-center justify-between text-[11px] text-[#71717a] dark:text-[#a1a1aa]">
                  <span>{selectedFlight ? "Verified flight fare:" : "Estimated rail fare:"}</span>
                  <span className="font-mono font-bold text-sky-600 dark:text-sky-400">
                    ₹{(selectedFlight?.price || selectedTrain?.fare_inr || 850).toLocaleString("en-IN")}
                  </span>
                </div>
                <p className="text-[10px] text-[#8f8f8f] mt-0.5">
                  {selectedFlight ? `Dep: ${selectedFlight.departure_time} (${selectedFlight.departure_airport_code})` : `Dep: ${selectedTrain.departure_time} (${selectedTrain.from_station_code})`}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ROUTE SPINE */}
      {routeLegs.length > 0 && (
        <div className="vercel-card p-4">
          <div className="flex items-center space-x-2 mb-3">
            <Map className="w-4 h-4 text-[#0070f3]" />
            <h3 className="font-semibold text-sm text-[#171717] dark:text-white">Route Overview</h3>
          </div>
          <RouteSpine legs={routeLegs} />
        </div>
      )}

      {/* DAY-BY-DAY ITINERARY */}
      {days && days.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-[#0070f3]" />
            <h3 className="font-semibold text-sm text-[#171717] dark:text-white">Day-by-Day Plan</h3>
          </div>
          {days.map((day) => (
            <DayCard key={day.day} day={day} />
          ))}
        </div>
      )}

      {/* SUMMARY */}
      {summary && (
        <div className="vercel-card p-4 bg-gradient-to-r from-emerald-50/50 to-teal-50/30 dark:from-emerald-900/10 dark:to-teal-900/10 border-emerald-200/50 dark:border-emerald-900/30">
          <h3 className="font-semibold text-sm text-[#171717] dark:text-white mb-3">Trip at a Glance</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs mb-3">
            {summary.total_distance_km && (
              <div className="text-center p-2 bg-white/70 dark:bg-[#111111]/70 rounded-[8px]">
                <p className="font-bold text-base text-[#0070f3]">{summary.total_distance_km} km</p>
                <p className="text-[#8f8f8f] mt-0.5">Total Distance</p>
              </div>
            )}
            {summary.total_drive_time && (
              <div className="text-center p-2 bg-white/70 dark:bg-[#111111]/70 rounded-[8px]">
                <p className="font-bold text-base text-[#0070f3]">{summary.total_drive_time}</p>
                <p className="text-[#8f8f8f] mt-0.5">Driving Time</p>
              </div>
            )}
            {summary.overnight_stops !== undefined && (
              <div className="text-center p-2 bg-white/70 dark:bg-[#111111]/70 rounded-[8px]">
                <p className="font-bold text-base text-[#0070f3]">{summary.overnight_stops}</p>
                <p className="text-[#8f8f8f] mt-0.5">Overnight Stops</p>
              </div>
            )}
            {summary.major_destinations && (
              <div className="text-center p-2 bg-white/70 dark:bg-[#111111]/70 rounded-[8px] col-span-2 sm:col-span-1">
                <p className="font-bold text-sm text-[#0070f3] truncate">{summary.major_destinations.join(" · ")}</p>
                <p className="text-[#8f8f8f] mt-0.5">Key Destinations</p>
              </div>
            )}
          </div>
          {summary.highlights && summary.highlights.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {summary.highlights.map((h, i) => (
                <span key={i} className="text-xs px-2.5 py-1 bg-emerald-100/70 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-200 rounded-full font-medium">{h}</span>
              ))}
            </div>
          )}
          {summary.closing_note && (
            <p className="text-sm text-[#4d4d4d] dark:text-[#a1a1a1] italic border-t border-emerald-200/40 dark:border-emerald-900/30 pt-3 mt-2">
              {summary.closing_note}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
