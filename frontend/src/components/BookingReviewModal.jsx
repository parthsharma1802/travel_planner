import React, { useState } from "react";
import {
  X, ShieldCheck, Hotel, Plane, Train, Car, DollarSign, Calendar, Users, MapPin,
  ExternalLink, CheckCircle2, AlertCircle, Sparkles, ArrowRight, Info
} from "lucide-react";

export default function BookingReviewModal({
  isOpen,
  onClose,
  selectedHotel,
  selectedFlight,
  selectedTrain,
  tripContext = {},
  onConfirmSelection
}) {
  const [bookingStatus, setBookingStatus] = useState("selected"); // recommended, selected, external_booking, booking_confirmed

  if (!isOpen) return null;

  const destination = tripContext.destination || selectedHotel?.city || selectedFlight?.destination_name || "Your Trip Destination";
  const origin = tripContext.origin || selectedFlight?.origin_name || selectedTrain?.from_station_name || "Starting City";
  const dates = tripContext.dates || tripContext.travelDates?.rangeDisplay || "Dates to be finalized";
  const travelers = tripContext.travelers || "2 Adults";
  const targetBudget = tripContext.budget ? parseInt(tripContext.budget.replace(/[^0-9]/g, "") || "15000", 10) : 15000;

  // Calculate dynamic costs
  const hotelCost = selectedHotel ? (selectedHotel.price_inr || 0) * (tripContext.duration_days || 3) : 0;
  const transportCost = selectedFlight ? (selectedFlight.price || 0) : (selectedTrain ? (selectedTrain.fare_inr || 1200) : 0);
  const foodCost = (tripContext.duration_days || 3) * 800;
  const activitiesCost = (tripContext.duration_days || 3) * 500;
  const totalEstimated = hotelCost + transportCost + foodCost + activitiesCost;
  const remainingBudget = targetBudget - totalEstimated;

  const handleExternalBooking = (url) => {
    setBookingStatus("external_booking");
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white dark:bg-[#121214] border border-[#ebebeb] dark:border-[#27272a] rounded-[16px] max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col text-left">
        
        {/* Modal Header */}
        <div className="p-5 border-b border-[#ebebeb] dark:border-[#222222] flex items-center justify-between sticky top-0 bg-white/95 dark:bg-[#121214]/95 backdrop-blur-md z-10">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-[8px] bg-[#0066cc]/10 dark:bg-[#2997ff]/20 text-[#0066cc] dark:text-[#2997ff] flex items-center justify-center font-bold">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-[#171717] dark:text-white">
                  Trip Review & Booking Summary
                </h3>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase ${
                  bookingStatus === "external_booking"
                    ? "bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-400"
                    : "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400"
                }`}>
                  Status: {bookingStatus.replace("_", " ")}
                </span>
              </div>
              <p className="text-xs text-[#71717a] dark:text-[#a1a1aa] mt-0.5">
                Review selections & estimated budget before external booking
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-[6px] hover:bg-black/5 dark:hover:bg-white/10 text-[#8f8f8f] hover:text-[#171717] dark:hover:text-white transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 space-y-5 flex-1">
          
          {/* Trip Context Card */}
          <div className="p-3.5 rounded-[10px] bg-sky-50/60 dark:bg-sky-950/20 border border-sky-200/60 dark:border-sky-900/40 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div>
              <p className="text-[#71717a] dark:text-[#a1a1aa] text-[11px] font-medium flex items-center">
                <MapPin className="w-3 h-3 mr-1 text-sky-600" /> Destination
              </p>
              <p className="font-bold text-[#171717] dark:text-white mt-0.5 truncate">{destination}</p>
            </div>
            <div>
              <p className="text-[#71717a] dark:text-[#a1a1aa] text-[11px] font-medium flex items-center">
                <Calendar className="w-3 h-3 mr-1 text-sky-600" /> Travel Dates
              </p>
              <p className="font-bold text-[#171717] dark:text-white mt-0.5 truncate">{dates}</p>
            </div>
            <div>
              <p className="text-[#71717a] dark:text-[#a1a1aa] text-[11px] font-medium flex items-center">
                <Users className="w-3 h-3 mr-1 text-sky-600" /> Travelers
              </p>
              <p className="font-bold text-[#171717] dark:text-white mt-0.5">{travelers}</p>
            </div>
            <div>
              <p className="text-[#71717a] dark:text-[#a1a1aa] text-[11px] font-medium flex items-center">
                <DollarSign className="w-3 h-3 mr-1 text-emerald-600" /> Budget Goal
              </p>
              <p className="font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">₹{targetBudget.toLocaleString("en-IN")}</p>
            </div>
          </div>

          {/* Selected Hotel Card */}
          <div className="border border-[#ebebeb] dark:border-[#27272a] rounded-[12px] p-4 bg-white dark:bg-[#17171a]">
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-black/5 dark:border-white/5">
              <div className="flex items-center space-x-2">
                <Hotel className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <h4 className="font-bold text-xs uppercase tracking-wider text-[#171717] dark:text-white">
                  Selected Stay / Accommodation
                </h4>
              </div>
              <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded font-semibold">
                Indicative Reference Price
              </span>
            </div>

            {selectedHotel ? (
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                  <p className="font-bold text-sm text-[#171717] dark:text-white">{selectedHotel.hotel_name}</p>
                  <p className="text-[#71717a] dark:text-[#a1a1aa] text-[11px] mt-0.5">
                    {selectedHotel.city} • Best rate via <strong>{selectedHotel.best_vendor || "Booking.com"}</strong>
                  </p>
                </div>
                <div className="flex items-center space-x-3 self-end sm:self-auto">
                  <div className="text-right">
                    <p className="font-bold text-sm text-emerald-600 dark:text-emerald-400">
                      ₹{(selectedHotel.price_inr || 0).toLocaleString("en-IN")}
                      <span className="text-[10px] font-normal text-[#71717a]"> /night</span>
                    </p>
                    <p className="text-[10px] text-[#8f8f8f]">Est. Stay: ₹{hotelCost.toLocaleString("en-IN")}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleExternalBooking(selectedHotel.booking_url)}
                    className="px-2.5 py-1.5 rounded-[6px] text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white transition-all flex items-center space-x-1 shrink-0"
                  >
                    <span>View on Vendor</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-xs text-[#8f8f8f] italic py-2">
                No hotel selected yet. Ask the assistant "Show hotels in {destination}" to compare and select a stay.
              </div>
            )}
          </div>

          {/* Selected Transport Card */}
          <div className="border border-[#ebebeb] dark:border-[#27272a] rounded-[12px] p-4 bg-white dark:bg-[#17171a]">
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-black/5 dark:border-white/5">
              <div className="flex items-center space-x-2">
                {selectedFlight ? (
                  <Plane className="w-4 h-4 text-sky-600 dark:text-sky-400" />
                ) : (
                  <Train className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                )}
                <h4 className="font-bold text-xs uppercase tracking-wider text-[#171717] dark:text-white">
                  Selected Transport
                </h4>
              </div>
              <span className="text-[10px] font-mono text-sky-600 dark:text-sky-400 bg-sky-50 dark:bg-sky-950/60 px-2 py-0.5 rounded font-semibold">
                {selectedFlight ? "Google Flights (Live)" : (selectedTrain ? "RailKit Schedule" : "Transport Option")}
              </span>
            </div>

            {selectedFlight ? (
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                  <p className="font-bold text-sm text-[#171717] dark:text-white">
                    {selectedFlight.airline} {selectedFlight.flight_number}
                  </p>
                  <p className="text-[#71717a] dark:text-[#a1a1aa] text-[11px] mt-0.5">
                    {selectedFlight.departure_time} ({selectedFlight.departure_airport_code}) → {selectedFlight.arrival_time} ({selectedFlight.arrival_airport_code}) • {selectedFlight.duration}
                  </p>
                </div>
                <div className="flex items-center space-x-3 self-end sm:self-auto">
                  <div className="text-right">
                    <p className="font-bold text-sm text-sky-600 dark:text-sky-400">
                      ₹{(selectedFlight.price || 0).toLocaleString("en-IN")}
                    </p>
                    <p className="text-[10px] text-[#8f8f8f]">Verified Fare</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleExternalBooking(selectedFlight.booking_url || `https://www.google.com/travel/flights`)}
                    className="px-2.5 py-1.5 rounded-[6px] text-xs font-semibold bg-sky-600 hover:bg-sky-700 text-white transition-all flex items-center space-x-1 shrink-0"
                  >
                    <span>Book Flight</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ) : selectedTrain ? (
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                  <p className="font-bold text-sm text-[#171717] dark:text-white">
                    {selectedTrain.train_number} {selectedTrain.train_name}
                  </p>
                  <p className="text-[#71717a] dark:text-[#a1a1aa] text-[11px] mt-0.5">
                    {selectedTrain.departure_time} ({selectedTrain.from_station_code}) → {selectedTrain.arrival_time} ({selectedTrain.to_station_code}) • {selectedTrain.duration}
                  </p>
                </div>
                <div className="flex items-center space-x-3 self-end sm:self-auto">
                  <div className="text-right">
                    <p className="font-bold text-sm text-amber-600 dark:text-amber-400">
                      ₹{(selectedTrain.fare_inr || 850).toLocaleString("en-IN")}
                    </p>
                    <p className="text-[10px] text-[#8f8f8f]">Est. Rail Fare</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleExternalBooking(selectedTrain.booking_url || "https://www.irctc.co.in/nget/train-search")}
                    className="px-2.5 py-1.5 rounded-[6px] text-xs font-semibold bg-amber-600 hover:bg-amber-700 text-white transition-all flex items-center space-x-1 shrink-0"
                  >
                    <span>IRCTC Booking</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-xs text-[#8f8f8f] italic py-2">
                No transport selected. Ask the assistant "Find flights from Delhi to {destination}" or "Find trains".
              </div>
            )}
          </div>

          {/* Dynamic Trip Budget Integration */}
          <div className="border border-emerald-200 dark:border-emerald-900/50 rounded-[12px] p-4 bg-gradient-to-br from-emerald-50/40 via-white to-teal-50/20 dark:from-[#0d1e16] dark:via-[#111827] dark:to-[#091510]">
            <h4 className="font-bold text-xs uppercase tracking-wider text-[#171717] dark:text-white mb-3 flex items-center space-x-2">
              <DollarSign className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Trip Budget Breakdown (Internal Estimation)</span>
            </h4>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between text-[#4d4d4d] dark:text-[#a1a1a1]">
                <span>Accommodation ({tripContext.duration_days || 3} nights):</span>
                <span className="font-mono font-semibold text-[#171717] dark:text-white">₹{hotelCost.toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between text-[#4d4d4d] dark:text-[#a1a1a1]">
                <span>Transport (Flight / Train / Fuel):</span>
                <span className="font-mono font-semibold text-[#171717] dark:text-white">₹{transportCost.toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between text-[#4d4d4d] dark:text-[#a1a1a1]">
                <span>Food & Dining (Estimated):</span>
                <span className="font-mono font-semibold text-[#171717] dark:text-white">₹{foodCost.toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between text-[#4d4d4d] dark:text-[#a1a1a1]">
                <span>Sightseeing & Activities:</span>
                <span className="font-mono font-semibold text-[#171717] dark:text-white">₹{activitiesCost.toLocaleString("en-IN")}</span>
              </div>

              <div className="pt-2 border-t border-black/10 dark:border-white/10 flex justify-between font-bold text-sm">
                <span>Estimated Total:</span>
                <span className="font-mono text-emerald-700 dark:text-emerald-400">₹{totalEstimated.toLocaleString("en-IN")}</span>
              </div>

              <div className="flex justify-between text-xs pt-1">
                <span className="text-[#71717a] dark:text-[#a1a1aa]">Allocated Target Budget:</span>
                <span className="font-mono font-medium text-[#171717] dark:text-white">₹{targetBudget.toLocaleString("en-IN")}</span>
              </div>

              <div className={`flex justify-between text-xs font-bold pt-1 ${
                remainingBudget >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"
              }`}>
                <span>{remainingBudget >= 0 ? "Remaining Balance:" : "Budget Deficit:"}</span>
                <span className="font-mono">₹{Math.abs(remainingBudget).toLocaleString("en-IN")}</span>
              </div>
            </div>
          </div>

          {/* Safety & Compliance Notice */}
          <div className="p-3 rounded-[8px] bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 flex items-start space-x-2 text-[11px] text-[#71717a] dark:text-[#a1a1aa]">
            <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
            <div>
              <strong>Secure External Booking Protocol:</strong> Dora AI provides AI itinerary curation and reference rates. When you click "Book", you will be redirected to the verified external provider (Google Flights, IRCTC, Booking.com, Priceline, Agoda). Dora AI never handles transactions or collects sensitive payment information.
            </div>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-[#ebebeb] dark:border-[#222222] bg-[#fafafa] dark:bg-[#0c0c0e] flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-[#71717a] dark:text-[#a1a1aa]">
            {selectedHotel || selectedFlight || selectedTrain ? "Selections saved in active trip session." : "Make selections to finalize itinerary."}
          </div>

          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 sm:flex-none px-4 py-2 rounded-[6px] text-xs font-medium bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-[#171717] dark:text-white transition-all"
            >
              Close Review
            </button>
            {onConfirmSelection && (
              <button
                type="button"
                onClick={() => {
                  onConfirmSelection();
                  onClose();
                }}
                className="flex-1 sm:flex-none px-4 py-2 rounded-[6px] text-xs font-semibold bg-[#0066cc] hover:bg-[#0055b3] text-white transition-all shadow-sm flex items-center justify-center space-x-1.5"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Apply to Itinerary</span>
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
