import React, { useState } from "react";
import { Plane, ExternalLink, Clock, Tag, ArrowRight, ShieldCheck, Sparkles, Filter } from "lucide-react";

export default function FlightBookingWidget({ flightData, onSelectFlight, selectedFlight }) {
  const [filter, setFilter] = useState("all"); // all, nonstop, cheapest, fastest

  if (!flightData || !flightData.flights || flightData.flights.length === 0) {
    return null;
  }

  const { origin, destination, departure_date, flights, currency = "INR" } = flightData;

  // Compute stats
  const validPrices = flights.map(f => f.price).filter(p => typeof p === "number" && p > 0);
  const minPrice = validPrices.length > 0 ? Math.min(...validPrices) : null;
  const minDuration = Math.min(...flights.map(f => f.duration_minutes || 9999));

  // Filter & sort
  let displayedFlights = [...flights];
  if (filter === "nonstop") {
    displayedFlights = displayedFlights.filter(f => f.is_non_stop);
  } else if (filter === "cheapest") {
    displayedFlights.sort((a, b) => (a.price || 999999) - (b.price || 999999));
  } else if (filter === "fastest") {
    displayedFlights.sort((a, b) => (a.duration_minutes || 9999) - (b.duration_minutes || 9999));
  }

  const origCode = origin?.airport_code || "DEL";
  const destCode = destination?.airport_code || "GOI";
  const depDate = departure_date || "";

  // Booking links
  const googleFlightsUrl = `https://www.google.com/travel/flights?q=Flights%20from%20${origCode}%20to%20${destCode}%20on%20${depDate}`;
  const mmtUrl = `https://www.makemytrip.com/flight/search?itinerary=${origCode}-${destCode}-${depDate}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E`;
  const easeMyTripUrl = `https://www.easemytrip.com/flight-listing/${origCode}-${destCode}-${depDate}`;

  return (
    <div className="mt-4 vercel-card p-4 sm:p-5 text-left w-full bg-gradient-to-br from-sky-50/70 via-white to-blue-50/50 dark:from-[#0b1320] dark:via-[#111827] dark:to-[#0f172a] border-sky-200/80 dark:border-sky-900/50 shadow-sm rounded-[14px]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-sky-100 dark:border-sky-900/40">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-500/10 dark:bg-sky-400/20 text-sky-600 dark:text-sky-400 flex items-center justify-center font-bold">
            <Plane className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-sm text-[#171717] dark:text-white">
                {origin?.query || origCode}
              </span>
              <ArrowRight className="w-3.5 h-3.5 text-[#8f8f8f]" />
              <span className="font-bold text-sm text-[#171717] dark:text-white">
                {destination?.query || destCode}
              </span>
              {depDate && (
                <span className="text-xs text-[#8f8f8f] font-mono ml-1">
                  • {depDate}
                </span>
              )}
            </div>
            <p className="text-[11px] text-[#71717a] dark:text-[#a1a1aa]">
              Live Google Flights options via SerpApi • Verified Real-time Fares
            </p>
          </div>
        </div>

        {/* Global Booking Shortcut */}
        <a
          href={googleFlightsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-600 hover:bg-sky-700 text-white transition-all shrink-0 self-start sm:self-auto shadow-sm"
        >
          <span>Compare on Google Flights</span>
          <ExternalLink className="w-3 h-3 ml-0.5" />
        </a>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-1.5 mt-3 mb-3 overflow-x-auto pb-1 text-xs">
        <span className="text-[11px] text-[#71717a] dark:text-[#a1a1aa] font-medium mr-1 flex items-center">
          <Filter className="w-3 h-3 mr-1" /> Filter:
        </span>
        {[
          { id: "all", label: `All (${flights.length})` },
          { id: "nonstop", label: "Non-stop" },
          { id: "cheapest", label: "Best Price" },
          { id: "fastest", label: "Fastest" },
        ].map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setFilter(tab.id)}
            className={`px-2.5 py-1 rounded-[6px] font-medium transition-all cursor-pointer ${
              filter === tab.id
                ? "bg-sky-600 text-white shadow-xs font-semibold"
                : "bg-black/5 dark:bg-white/5 text-[#52525b] dark:text-[#d4d4d8] hover:bg-black/10 dark:hover:bg-white/10"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Flight Cards List */}
      <div className="space-y-2.5">
        {displayedFlights.map((fl, idx) => {
          const isCheapest = minPrice && fl.price === minPrice;
          const isFastest = fl.duration_minutes === minDuration;

          return (
            <div
              key={`${fl.flight_number}-${idx}`}
              className="p-3 sm:p-3.5 rounded-[10px] bg-white/90 dark:bg-[#181f2e]/90 border border-black/5 dark:border-white/10 hover:border-sky-400 dark:hover:border-sky-600 transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-xs"
            >
              {/* Airline & Flight Number */}
              <div className="flex items-center space-x-3 min-w-[160px]">
                {fl.airline_logo ? (
                  <img
                    src={fl.airline_logo}
                    alt={fl.airline}
                    className="w-7 h-7 object-contain rounded-md bg-white p-0.5 border border-black/5"
                    onError={(e) => { e.target.style.display = 'none'; }}
                  />
                ) : (
                  <div className="w-7 h-7 rounded-md bg-sky-50 dark:bg-sky-950/60 text-sky-600 flex items-center justify-center font-bold text-xs">
                    ✈
                  </div>
                )}
                <div>
                  <div className="font-semibold text-xs text-[#171717] dark:text-white flex items-center space-x-1.5">
                    <span>{fl.airline}</span>
                    {fl.flight_number && (
                      <span className="text-[10px] font-mono text-[#71717a] dark:text-[#a1a1aa]">
                        {fl.flight_number}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-1 text-[11px] text-[#71717a] dark:text-[#a1a1aa]">
                    <span>{fl.travel_class || "Economy"}</span>
                    {fl.airplane && <span>• {fl.airplane}</span>}
                  </div>
                </div>
              </div>

              {/* Timing & Timeline */}
              <div className="flex items-center space-x-4 flex-1 justify-center sm:justify-start md:justify-center">
                <div className="text-right">
                  <div className="font-bold text-sm text-[#171717] dark:text-white">
                    {fl.departure_time}
                  </div>
                  <div className="text-[10px] font-mono text-[#71717a] dark:text-[#a1a1aa]">
                    {fl.departure_airport_code}
                  </div>
                </div>

                <div className="flex flex-col items-center min-w-[90px]">
                  <span className="text-[10px] font-medium text-[#71717a] dark:text-[#a1a1aa] flex items-center">
                    <Clock className="w-2.5 h-2.5 mr-0.5" />
                    {fl.duration}
                  </span>
                  <div className="w-full h-[1.5px] bg-sky-200 dark:bg-sky-800 my-1 relative">
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-sky-500 rounded-full" />
                  </div>
                  <span className={`text-[10px] font-semibold ${fl.is_non_stop ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"}`}>
                    {fl.is_non_stop ? "Non-stop" : `${fl.stops} stop`}
                  </span>
                </div>

                <div className="text-left">
                  <div className="font-bold text-sm text-[#171717] dark:text-white">
                    {fl.arrival_time}
                  </div>
                  <div className="text-[10px] font-mono text-[#71717a] dark:text-[#a1a1aa]">
                    {fl.arrival_airport_code}
                  </div>
                </div>
              </div>

              {/* Price & Booking Actions */}
              <div className="flex items-center justify-between md:justify-end space-x-3 pt-2 md:pt-0 border-t md:border-t-0 border-black/5 dark:border-white/5">
                <div className="text-left md:text-right">
                  <div className="flex items-center md:justify-end space-x-1">
                    <span className="font-bold text-base text-sky-700 dark:text-sky-300">
                      ₹{fl.price ? fl.price.toLocaleString("en-IN") : "Check"}
                    </span>
                  </div>
                  {isCheapest && (
                    <span className="inline-flex items-center text-[9px] font-bold px-1.5 py-0.2 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                      <Sparkles className="w-2.5 h-2.5 mr-0.5" /> Best Price
                    </span>
                  )}
                  {!isCheapest && isFastest && (
                    <span className="inline-flex items-center text-[9px] font-bold px-1.5 py-0.2 rounded bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300">
                      ⚡ Fastest
                    </span>
                  )}
                </div>

                {/* Direct Booking & Selection Links */}
                <div className="flex items-center space-x-1.5">
                  {onSelectFlight && (
                    <button
                      type="button"
                      onClick={() => onSelectFlight({
                        airline: fl.airline,
                        flight_number: fl.flight_number,
                        departure_time: fl.departure_time,
                        departure_airport_code: fl.departure_airport_code,
                        arrival_time: fl.arrival_time,
                        arrival_airport_code: fl.arrival_airport_code,
                        duration: fl.duration,
                        price: fl.price,
                        booking_url: googleFlightsUrl,
                        origin_name: origin?.query || origCode,
                        destination_name: destination?.query || destCode,
                        status: "selected"
                      })}
                      className={`px-2.5 py-1.5 rounded-[6px] text-xs font-semibold transition-all cursor-pointer ${
                        selectedFlight && selectedFlight.flight_number === fl.flight_number
                          ? "bg-sky-700 text-white shadow-xs"
                          : "bg-sky-600 hover:bg-sky-700 text-white shadow-xs"
                      }`}
                    >
                      {selectedFlight && selectedFlight.flight_number === fl.flight_number ? "Selected" : "Select"}
                    </button>
                  )}
                  <a
                    href={googleFlightsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-2.5 py-1.5 rounded-[6px] text-xs font-semibold bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-[#3f3f46] dark:text-[#e4e4e7] transition-all flex items-center space-x-1"
                    title="Book on Google Flights"
                  >
                    <span>Book</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                  <a
                    href={mmtUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-2 py-1.5 rounded-[6px] text-[11px] font-medium bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-[#3f3f46] dark:text-[#e4e4e7] transition-all"
                    title="Compare on MakeMyTrip"
                  >
                    MMT
                  </a>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer / Booking Advice */}
      <div className="mt-3 pt-2.5 border-t border-sky-100 dark:border-sky-900/30 flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#71717a] dark:text-[#a1a1aa] gap-1">
        <div className="flex items-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
          <span>Compare indicative fares with Google Flights, MakeMyTrip & EaseMyTrip before booking.</span>
        </div>
        <div className="flex items-center space-x-2 text-[10px] font-medium text-sky-600 dark:text-sky-400">
          <a href={googleFlightsUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">Google Flights</a>
          <span>•</span>
          <a href={mmtUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">MakeMyTrip</a>
          <span>•</span>
          <a href={easeMyTripUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">EaseMyTrip</a>
        </div>
      </div>
    </div>
  );
}
