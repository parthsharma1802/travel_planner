import React, { useState, useEffect } from "react";
import {
  Calendar, Clock, MapPin, ArrowRight, CheckCircle2, Bookmark,
  Trash2, Edit3, Check, X, Hotel, Plane, Train, DollarSign, Sparkles, FolderHeart, Plus, Compass
} from "lucide-react";
import { CURATED_TRIPS } from "../data/travelProductData";

export default function TripsSection({ onOpenTrip, onNewTrip, onConvertToJournal }) {
  const [savedTrips, setSavedTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingTripId, setEditingTripId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [activeSubTab, setActiveSubTab] = useState("saved"); // saved, curated

  // Fetch saved trips from backend API
  const fetchSavedTrips = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/trips");
      if (res.ok) {
        const data = await res.json();
        setSavedTrips(data.trips || []);
      }
    } catch (err) {
      console.warn("Could not fetch saved trips:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSavedTrips();
  }, []);

  const handleRename = async (tripId) => {
    if (!editTitle.trim()) {
      setEditingTripId(null);
      return;
    }
    try {
      const res = await fetch(`/api/trips/${tripId}/rename`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: editTitle.trim() })
      });
      if (res.ok) {
        setSavedTrips(prev => prev.map(t => t.id === tripId ? { ...t, title: editTitle.trim() } : t));
      }
    } catch (err) {
      console.error("Failed to rename trip:", err);
    } finally {
      setEditingTripId(null);
      setEditTitle("");
    }
  };

  const handleDelete = async (tripId, e) => {
    if (e) e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this saved trip?")) return;

    try {
      const res = await fetch(`/api/trips/${tripId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        setSavedTrips(prev => prev.filter(t => t.id !== tripId));
      }
    } catch (err) {
      console.error("Failed to delete trip:", err);
    }
  };

  const handleOpen = (trip) => {
    if (typeof onOpenTrip === "function") {
      onOpenTrip(trip);
    }
  };

  return (
    <div className="w-full space-y-6 text-left">
      {/* Tab Switcher & Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#ebebeb] dark:border-[#222222]">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#0066cc] dark:text-[#2997ff] flex items-center">
              <FolderHeart className="w-3.5 h-3.5 mr-1" />
              Saved Itineraries & Trips
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 font-bold">
              {savedTrips.length} Saved
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#171717] dark:text-white tracking-tight mt-1">
            Your Personal Travel Portfolio
          </h2>
          <p className="text-xs text-[#71717a] dark:text-[#a1a1aa] mt-1">
            Review, rename, open in chat, or delete your customized AI travel plans.
          </p>
        </div>

        <div className="flex items-center space-x-2 self-start sm:self-auto">
          {/* Subtabs */}
          <div className="flex items-center p-0.5 rounded-[8px] bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/10 text-xs">
            <button
              onClick={() => setActiveSubTab("saved")}
              className={`px-3 py-1.5 rounded-[6px] font-medium transition-all ${
                activeSubTab === "saved"
                  ? "bg-white dark:bg-[#1f1f23] text-[#171717] dark:text-white shadow-xs font-semibold"
                  : "text-[#71717a] dark:text-[#a1a1aa] hover:text-[#171717]"
              }`}
            >
              My Saved Trips ({savedTrips.length})
            </button>
            <button
              onClick={() => setActiveSubTab("curated")}
              className={`px-3 py-1.5 rounded-[6px] font-medium transition-all ${
                activeSubTab === "curated"
                  ? "bg-white dark:bg-[#1f1f23] text-[#171717] dark:text-white shadow-xs font-semibold"
                  : "text-[#71717a] dark:text-[#a1a1aa] hover:text-[#171717]"
              }`}
            >
              Curated Tours ({CURATED_TRIPS.length})
            </button>
          </div>

          {onNewTrip && (
            <button
              onClick={onNewTrip}
              className="px-3.5 py-1.5 rounded-[8px] bg-[#0066cc] hover:bg-[#0055b3] text-white text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition-all"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Plan New Trip</span>
            </button>
          )}
        </div>
      </div>

      {/* SUBTAB 1: SAVED TRIPS */}
      {activeSubTab === "saved" && (
        <div>
          {loading ? (
            <div className="py-12 text-center text-xs text-[#8f8f8f]">
              <Sparkles className="w-6 h-6 mx-auto mb-2 text-[#0066cc] animate-spin" />
              Loading saved trips...
            </div>
          ) : savedTrips.length === 0 ? (
            <div className="py-16 text-center max-w-md mx-auto p-6 rounded-[16px] border border-dashed border-[#ebebeb] dark:border-[#27272a] bg-black/2 dark:bg-white/2">
              <div className="w-12 h-12 rounded-full bg-[#0066cc]/10 dark:bg-[#2997ff]/20 text-[#0066cc] dark:text-[#2997ff] flex items-center justify-center mx-auto mb-3">
                <Bookmark className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-base text-[#171717] dark:text-white">
                No saved trips yet
              </h3>
              <p className="text-xs text-[#71717a] dark:text-[#a1a1aa] mt-1.5 leading-relaxed">
                When you generate an itinerary in the Dora AI Chatbot, click the <strong>"Save Trip"</strong> button to store and manage it here.
              </p>
              {onNewTrip && (
                <button
                  onClick={onNewTrip}
                  className="mt-4 px-4 py-2 rounded-[8px] bg-[#171717] dark:bg-white text-white dark:text-black text-xs font-semibold hover:bg-black transition-all inline-flex items-center space-x-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Start Planning in Chatbot</span>
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {savedTrips.map((trip) => {
                const isEditing = editingTripId === trip.id;
                const stayName = trip.hotel?.hotel_name || trip.itinerary?.days?.[0]?.stay_area || null;
                const transportSummary = trip.transport?.name || (trip.transport?.airline ? `${trip.transport.airline} ${trip.transport.flight_number || ''}` : null) || trip.itinerary?.overview?.transport || null;
                const daysCount = trip.itinerary?.days?.length || trip.duration || "3 Days";

                return (
                  <div
                    key={trip.id}
                    className="p-5 rounded-[14px] bg-white dark:bg-[#17171a] border border-[#ebebeb] dark:border-[#27272a] hover:border-[#0066cc]/50 dark:hover:border-[#2997ff]/50 shadow-xs hover:shadow-md transition-all flex flex-col justify-between group"
                  >
                    <div>
                      {/* Top Action Bar */}
                      <div className="flex items-start justify-between gap-2 mb-2">
                        {isEditing ? (
                          <div className="flex items-center space-x-1.5 flex-1 mr-2">
                            <input
                              type="text"
                              value={editTitle}
                              onChange={(e) => setEditTitle(e.target.value)}
                              onKeyDown={(e) => e.key === "Enter" && handleRename(trip.id)}
                              className="w-full bg-[#fafafa] dark:bg-[#222222] border border-[#0066cc] rounded-[6px] px-2.5 py-1 text-xs text-[#171717] dark:text-white font-semibold focus:outline-none"
                              autoFocus
                            />
                            <button
                              onClick={() => handleRename(trip.id)}
                              className="p-1 text-emerald-600 hover:text-emerald-700"
                              title="Save title"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => setEditingTripId(null)}
                              className="p-1 text-gray-400 hover:text-gray-600"
                              title="Cancel"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-2 flex-1 min-w-0">
                            <h3 className="font-bold text-sm text-[#171717] dark:text-white truncate">
                              {trip.title}
                            </h3>
                            <button
                              onClick={() => {
                                setEditingTripId(trip.id);
                                setEditTitle(trip.title);
                              }}
                              className="opacity-0 group-hover:opacity-100 p-1 text-[#8f8f8f] hover:text-[#0066cc] dark:hover:text-[#2997ff] transition-opacity"
                              title="Rename trip"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}

                        <button
                          onClick={(e) => handleDelete(trip.id, e)}
                          className="p-1 text-gray-400 hover:text-rose-600 transition-colors shrink-0"
                          title="Delete saved trip"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Destination & Specs */}
                      <div className="flex flex-wrap items-center gap-2 text-xs text-[#71717a] dark:text-[#a1a1aa] mb-3">
                        <span className="flex items-center font-medium text-[#171717] dark:text-white">
                          <MapPin className="w-3.5 h-3.5 mr-1 text-[#0066cc]" />
                          {trip.destination || "Heritage Circuit"}
                        </span>
                        {trip.dates && (
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            {trip.dates}
                          </span>
                        )}
                        <span className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {typeof daysCount === "number" ? `${daysCount} Days` : daysCount}
                        </span>
                      </div>

                      {/* Selected Hotel & Transport Summary */}
                      <div className="space-y-1.5 p-3 rounded-[8px] bg-black/3 dark:bg-white/3 border border-black/5 dark:border-white/5 text-xs mb-4">
                        {stayName && (
                          <div className="flex items-center justify-between text-[#4d4d4d] dark:text-[#a1a1a1]">
                            <span className="flex items-center">
                              <Hotel className="w-3.5 h-3.5 mr-1.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                              <span className="truncate max-w-[180px]">{stayName}</span>
                            </span>
                            {trip.hotel?.price_inr && (
                              <span className="font-mono text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                                ₹{trip.hotel.price_inr.toLocaleString("en-IN")}/night
                              </span>
                            )}
                          </div>
                        )}

                        {transportSummary && (
                          <div className="flex items-center justify-between text-[#4d4d4d] dark:text-[#a1a1a1]">
                            <span className="flex items-center">
                              <Plane className="w-3.5 h-3.5 mr-1.5 text-sky-600 dark:text-sky-400 shrink-0" />
                              <span className="truncate max-w-[180px]">{transportSummary}</span>
                            </span>
                            {trip.transport?.price && (
                              <span className="font-mono text-[11px] font-semibold text-sky-600 dark:text-sky-400">
                                ₹{trip.transport.price.toLocaleString("en-IN")}
                              </span>
                            )}
                          </div>
                        )}

                        {trip.budget && (
                          <div className="flex items-center justify-between text-[#4d4d4d] dark:text-[#a1a1a1]">
                            <span className="flex items-center">
                              <DollarSign className="w-3.5 h-3.5 mr-1.5 text-amber-600 dark:text-amber-400 shrink-0" />
                              <span>Allocated Budget:</span>
                            </span>
                            <span className="font-mono text-[11px] font-semibold text-[#171717] dark:text-white">
                              {trip.budget}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Card Footer: Open in Chatbot & Write Story */}
                    <div className="pt-3 border-t border-black/5 dark:border-white/5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                      <span className="text-[11px] text-[#8f8f8f]">
                        Saved {new Date(trip.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
                      </span>

                      <div className="flex items-center space-x-1.5 self-end sm:self-auto">
                        {onConvertToJournal && (
                          <button
                            type="button"
                            onClick={() => onConvertToJournal(trip)}
                            className="px-2.5 py-1.5 rounded-[6px] text-xs font-medium bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-[#171717] dark:text-white transition-all flex items-center space-x-1"
                            title="Convert into Travel Journal story"
                          >
                            <BookOpen className="w-3.5 h-3.5 text-[#0066cc] dark:text-[#2997ff]" />
                            <span>Write Story</span>
                          </button>
                        )}
                        <button
                          onClick={() => handleOpen(trip)}
                          className="px-3 py-1.5 rounded-[6px] text-xs font-semibold bg-[#0066cc] hover:bg-[#0055b3] text-white transition-all flex items-center space-x-1 shadow-xs"
                        >
                          <span>Open & Restore</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* SUBTAB 2: CURATED MULTI-DAY TOURS */}
      {activeSubTab === "curated" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {CURATED_TRIPS.map((trip) => (
            <div
              key={trip.id}
              className="apple-card overflow-hidden border border-[#ebebeb] dark:border-[#222222] flex flex-col md:flex-row bg-white dark:bg-[#17171a] shadow-xs"
            >
              <div className="md:w-5/12 h-56 md:h-auto relative">
                <img src={trip.image_url} alt={trip.title} className="w-full h-full object-cover" />
                <div className="absolute top-3 left-3 bg-black/70 backdrop-blur-md text-white px-2.5 py-1 rounded-full text-xs font-semibold flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{trip.days}</span>
                </div>
              </div>

              <div className="p-5 md:w-7/12 flex flex-col justify-between">
                <div>
                  <div className="flex items-center space-x-2 text-xs text-[#0066cc] dark:text-[#2997ff] font-semibold">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{trip.cities.join(" → ")}</span>
                  </div>
                  <h3 className="text-base font-bold text-[#171717] dark:text-white mt-1">{trip.title}</h3>

                  <div className="mt-3 space-y-1.5">
                    <p className="text-[10px] font-mono text-[#71717a] dark:text-[#a1a1aa] uppercase tracking-wider">Highlights:</p>
                    {trip.highlights.slice(0, 3).map((hl) => (
                      <div key={hl} className="flex items-center space-x-2 text-xs text-[#4d4d4d] dark:text-[#d4d4d8]">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                        <span className="truncate">{hl}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-5 pt-3 border-t border-[#ebebeb] dark:border-[#222222] flex items-center justify-between">
                  <div>
                    <span className="text-[10px] text-[#8f8f8f] uppercase">Indicative Fare</span>
                    <p className="text-sm font-bold text-[#171717] dark:text-white">{trip.price_start}</p>
                  </div>
                  <button
                    onClick={() => {
                      if (onNewTrip) {
                        onNewTrip();
                      }
                    }}
                    className="px-3.5 py-1.5 rounded-[6px] text-xs font-semibold bg-[#0066cc] hover:bg-[#0055b3] text-white transition-all flex items-center space-x-1"
                  >
                    <span>Plan Similar</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
