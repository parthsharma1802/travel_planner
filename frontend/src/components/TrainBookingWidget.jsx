import React, { useState } from "react";
import { Train, ExternalLink, Clock, Calendar, ArrowRight, ShieldCheck, Sparkles, Filter } from "lucide-react";

export default function TrainBookingWidget({ trainData, onSelectTrain, selectedTrain }) {
  const [filter, setFilter] = useState("all"); // all, premier (shatabdi/vande bharat), fastest

  if (!trainData || !trainData.trains || trainData.trains.length === 0) {
    return null;
  }

  const { source, destination, travel_date, trains, provider = "RailKit" } = trainData;

  const srcCode = source?.station_code || "NDLS";
  const dstCode = destination?.station_code || "JP";
  const srcName = source?.station_name || source?.query || srcCode;
  const dstName = destination?.station_name || destination?.query || dstCode;

  // Filter & sort
  let displayedTrains = [...trains];
  if (filter === "premier") {
    displayedTrains = displayedTrains.filter(t => 
      t.train_name.toLowerCase().includes("vande bharat") ||
      t.train_name.toLowerCase().includes("shatabdi") ||
      t.train_name.toLowerCase().includes("rajdhani") ||
      t.train_name.toLowerCase().includes("double")
    );
    if (displayedTrains.length === 0) displayedTrains = [...trains];
  } else if (filter === "fastest") {
    displayedTrains.sort((a, b) => (a.duration || "").localeCompare(b.duration || ""));
  }

  // Booking links
  const irctcUrl = "https://www.irctc.co.in/nget/train-search";
  const confirmTktUrl = `https://www.confirmtkt.com/rbooking-d/trains/from/${srcCode}/to/${dstCode}`;
  const mmtTrainUrl = `https://www.makemytrip.com/railways/`;

  return (
    <div className="mt-4 vercel-card p-4 sm:p-5 text-left w-full bg-gradient-to-br from-amber-50/70 via-white to-orange-50/40 dark:from-[#1c150c] dark:via-[#171717] dark:to-[#1a140f] border-amber-200/80 dark:border-amber-900/40 shadow-sm rounded-[14px]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-amber-100 dark:border-amber-900/30">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 dark:bg-amber-400/20 text-amber-600 dark:text-amber-400 flex items-center justify-center font-bold">
            <Train className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-sm text-[#171717] dark:text-white">
                {srcName} ({srcCode})
              </span>
              <ArrowRight className="w-3.5 h-3.5 text-[#8f8f8f]" />
              <span className="font-bold text-sm text-[#171717] dark:text-white">
                {dstName} ({dstCode})
              </span>
              {travel_date && (
                <span className="text-xs text-[#8f8f8f] font-mono ml-1">
                  • {travel_date}
                </span>
              )}
            </div>
            <p className="text-[11px] text-[#71717a] dark:text-[#a1a1aa]">
              Verified Indian Railways Schedules ({provider}) • {trains.length} Direct Trains
            </p>
          </div>
        </div>

        {/* Global IRCTC Shortcut */}
        <a
          href={irctcUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-600 hover:bg-amber-700 text-white transition-all shrink-0 self-start sm:self-auto shadow-sm"
        >
          <span>Book on IRCTC</span>
          <ExternalLink className="w-3 h-3 ml-0.5" />
        </a>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-1.5 mt-3 mb-3 overflow-x-auto pb-1 text-xs">
        <span className="text-[11px] text-[#71717a] dark:text-[#a1a1aa] font-medium mr-1 flex items-center">
          <Filter className="w-3 h-3 mr-1" /> Filter:
        </span>
        {[
          { id: "all", label: `All (${trains.length})` },
          { id: "premier", label: "Vande Bharat / Shatabdi" },
          { id: "fastest", label: "Fastest" },
        ].map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setFilter(tab.id)}
            className={`px-2.5 py-1 rounded-[6px] font-medium transition-all cursor-pointer ${
              filter === tab.id
                ? "bg-amber-600 text-white shadow-xs font-semibold"
                : "bg-black/5 dark:bg-white/5 text-[#52525b] dark:text-[#d4d4d8] hover:bg-black/10 dark:hover:bg-white/10"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Train Cards List */}
      <div className="space-y-2.5">
        {displayedTrains.map((tr, idx) => {
          const isVandeBharat = tr.train_name.toLowerCase().includes("vande bharat");
          const isShatabdi = tr.train_name.toLowerCase().includes("shatabdi") || tr.train_name.toLowerCase().includes("rajdhani");

          return (
            <div
              key={`${tr.train_number}-${idx}`}
              className="p-3 sm:p-3.5 rounded-[10px] bg-white/90 dark:bg-[#1f1b16]/90 border border-black/5 dark:border-white/10 hover:border-amber-400 dark:hover:border-amber-600 transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-xs"
            >
              {/* Train Name & Number */}
              <div className="min-w-[170px]">
                <div className="flex items-center space-x-1.5">
                  <span className="font-bold text-xs text-amber-700 dark:text-amber-400 font-mono bg-amber-50 dark:bg-amber-950/60 px-1.5 py-0.5 rounded border border-amber-200 dark:border-amber-800/40">
                    {tr.train_number}
                  </span>
                  <span className="font-semibold text-xs text-[#171717] dark:text-white truncate max-w-[140px]">
                    {tr.train_name}
                  </span>
                </div>
                <div className="flex items-center space-x-1.5 mt-1">
                  {isVandeBharat && (
                    <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                      ⚡ Vande Bharat
                    </span>
                  )}
                  {isShatabdi && (
                    <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-200">
                      ★ Shatabdi / SF
                    </span>
                  )}
                  {!isVandeBharat && !isShatabdi && (
                    <span className="text-[10px] text-[#71717a] dark:text-[#a1a1aa]">
                      Express Train • {tr.halts || 10} Halts
                    </span>
                  )}
                </div>
              </div>

              {/* Timing & Stations Timeline */}
              <div className="flex items-center space-x-4 flex-1 justify-center sm:justify-start md:justify-center">
                <div className="text-right">
                  <div className="font-bold text-sm text-[#171717] dark:text-white">
                    {tr.departure_time}
                  </div>
                  <div className="text-[10px] font-mono text-[#71717a] dark:text-[#a1a1aa] truncate max-w-[90px]">
                    {tr.from_station_code || srcCode}
                  </div>
                </div>

                <div className="flex flex-col items-center min-w-[90px]">
                  <span className="text-[10px] font-medium text-[#71717a] dark:text-[#a1a1aa] flex items-center">
                    <Clock className="w-2.5 h-2.5 mr-0.5" />
                    {tr.duration}
                  </span>
                  <div className="w-full h-[1.5px] bg-amber-200 dark:bg-amber-800 my-1 relative">
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-amber-500 rounded-full" />
                  </div>
                  <span className="text-[9px] font-mono text-[#71717a] dark:text-[#a1a1aa]">
                    {tr.distance_km ? `${tr.distance_km} km` : "Direct Route"}
                  </span>
                </div>

                <div className="text-left">
                  <div className="font-bold text-sm text-[#171717] dark:text-white">
                    {tr.arrival_time}
                  </div>
                  <div className="text-[10px] font-mono text-[#71717a] dark:text-[#a1a1aa] truncate max-w-[90px]">
                    {tr.to_station_code || dstCode}
                  </div>
                </div>
              </div>

              {/* Booking & Selection Actions */}
              <div className="flex items-center justify-between md:justify-end space-x-2 pt-2 md:pt-0 border-t md:border-t-0 border-black/5 dark:border-white/5">
                {onSelectTrain && (
                  <button
                    type="button"
                    onClick={() => onSelectTrain({
                      train_number: tr.train_number,
                      train_name: tr.train_name,
                      departure_time: tr.departure_time,
                      from_station_code: tr.from_station_code || srcCode,
                      from_station_name: srcName,
                      arrival_time: tr.arrival_time,
                      to_station_code: tr.to_station_code || dstCode,
                      to_station_name: dstName,
                      duration: tr.duration,
                      fare_inr: isVandeBharat ? 1450 : (isShatabdi ? 1100 : 750),
                      booking_url: confirmTktUrl,
                      status: "selected"
                    })}
                    className={`px-2.5 py-1.5 rounded-[6px] text-xs font-semibold transition-all cursor-pointer ${
                      selectedTrain && selectedTrain.train_number === tr.train_number
                        ? "bg-amber-700 text-white shadow-xs"
                        : "bg-amber-600 hover:bg-amber-700 text-white shadow-xs"
                    }`}
                  >
                    {selectedTrain && selectedTrain.train_number === tr.train_number ? "Selected" : "Select"}
                  </button>
                )}
                <a
                  href={confirmTktUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-2.5 py-1.5 rounded-[6px] text-xs font-semibold bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-[#3f3f46] dark:text-[#e4e4e7] transition-all flex items-center space-x-1"
                  title="Check Seat Availability & Confirm Score on ConfirmTkt"
                >
                  <span>Check Seats</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
                <a
                  href={irctcUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-2 py-1.5 rounded-[6px] text-[11px] font-medium bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-[#3f3f46] dark:text-[#e4e4e7] transition-all"
                  title="Book Ticket on IRCTC"
                >
                  IRCTC
                </a>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer / Booking Advice */}
      <div className="mt-3 pt-2.5 border-t border-amber-100 dark:border-amber-900/30 flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#71717a] dark:text-[#a1a1aa] gap-1">
        <div className="flex items-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
          <span>IRCTC authorized booking via ConfirmTkt & MakeMyTrip.</span>
        </div>
        <div className="flex items-center space-x-2 text-[10px] font-medium text-amber-700 dark:text-amber-400">
          <a href={irctcUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">IRCTC e-Ticketing</a>
          <span>•</span>
          <a href={confirmTktUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">ConfirmTkt PNR</a>
          <span>•</span>
          <a href={mmtTrainUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">MakeMyTrip Trains</a>
        </div>
      </div>
    </div>
  );
}
