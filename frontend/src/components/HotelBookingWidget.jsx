import React, { useState } from "react";
import { Hotel, ExternalLink, Star, MapPin, Tag, ArrowRight, ShieldCheck, Sparkles, Filter, CheckCircle2, DollarSign, Info } from "lucide-react";

export default function HotelBookingWidget({ hotelData, onSelectHotel, selectedHotel }) {
  const [filter, setFilter] = useState("all"); // all, best_price, luxury, heritage

  if (!hotelData || !hotelData.hotels || hotelData.hotels.length === 0) {
    return null;
  }

  const { city, hotels, provider = "Makcorps Free API", currency = "INR" } = hotelData;

  // Compute stats
  const validPrices = hotels.map(h => h.lowest_price_inr || h.indicative_price_inr).filter(p => typeof p === "number" && p > 0);
  const minPrice = validPrices.length > 0 ? Math.min(...validPrices) : null;

  // Filter & sort
  let displayedHotels = [...hotels];
  if (filter === "best_price") {
    displayedHotels.sort((a, b) => (a.lowest_price_inr || 999999) - (b.lowest_price_inr || 999999));
  } else if (filter === "luxury") {
    displayedHotels = displayedHotels.filter(h => (h.lowest_price_inr || 0) >= 10000 || (h.rating && h.rating >= 4.7));
    if (displayedHotels.length === 0) displayedHotels = [...hotels].sort((a, b) => (b.lowest_price_inr || 0) - (a.lowest_price_inr || 0));
  } else if (filter === "heritage") {
    displayedHotels = displayedHotels.filter(h => 
      h.hotel_name.toLowerCase().includes("palace") ||
      h.hotel_name.toLowerCase().includes("haveli") ||
      h.hotel_name.toLowerCase().includes("heritage") ||
      h.hotel_name.toLowerCase().includes("resort") ||
      h.hotel_name.toLowerCase().includes("grand")
    );
    if (displayedHotels.length === 0) displayedHotels = [...hotels];
  }

  const getSafeVendorSearchUrl = (hotelName, cityName, vendorName) => {
    const q = encodeURIComponent(`${hotelName} ${cityName}`);
    const vLower = (vendorName || "").toLowerCase();
    if (vLower.includes("booking")) {
      return `https://www.booking.com/searchresults.html?ss=${q}`;
    } else if (vLower.includes("agoda")) {
      return `https://www.agoda.com/search?city=${encodeURIComponent(cityName)}&keywords=${encodeURIComponent(hotelName)}`;
    } else if (vLower.includes("hotels.com")) {
      return `https://www.hotels.com/Hotel-Search?q=${q}`;
    } else if (vLower.includes("makemytrip") || vLower.includes("mmt")) {
      return `https://www.makemytrip.com/hotels/hotel-listing/?city=${encodeURIComponent(cityName)}&searchText=${encodeURIComponent(hotelName)}`;
    } else if (vLower.includes("trip.com")) {
      return `https://www.trip.com/hotels/list?keyword=${q}`;
    } else if (vLower.includes("priceline")) {
      return `https://www.priceline.com/hotel-search/${q}`;
    }
    return `https://www.google.com/travel/hotels?q=${q}`;
  };

  return (
    <div className="mt-4 vercel-card p-4 sm:p-5 text-left w-full bg-gradient-to-br from-emerald-50/70 via-white to-teal-50/40 dark:from-[#0d1f17] dark:via-[#111827] dark:to-[#0a1612] border-emerald-200/80 dark:border-emerald-900/50 shadow-sm rounded-[14px]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-emerald-100 dark:border-emerald-900/40">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 dark:bg-emerald-400/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">
            <Hotel className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-sm text-[#171717] dark:text-white">
                Stays in {city}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-semibold">
                Multi-Vendor Comparison
              </span>
            </div>
            <p className="text-[11px] text-[#71717a] dark:text-[#a1a1aa] flex items-center mt-0.5">
              <Info className="w-3 h-3 mr-1 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <span>Indicative reference rates • Powered by Makcorps Multi-Vendor API</span>
            </p>
          </div>
        </div>

        {/* External Provider Search Link */}
        <a
          href={`https://www.booking.com/searchresults.html?ss=${encodeURIComponent(city)}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white transition-all shrink-0 self-start sm:self-auto shadow-sm"
        >
          <span>Search All in {city}</span>
          <ExternalLink className="w-3 h-3 ml-0.5" />
        </a>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-1.5 mt-3 mb-3 overflow-x-auto pb-1 text-xs">
        <span className="text-[11px] text-[#71717a] dark:text-[#a1a1aa] font-medium mr-1 flex items-center">
          <Filter className="w-3 h-3 mr-1" /> Filter:
        </span>
        {[
          { id: "all", label: `All (${hotels.length})` },
          { id: "best_price", label: "Best Value" },
          { id: "luxury", label: "Luxury / 5-Star" },
          { id: "heritage", label: "Palace & Heritage" },
        ].map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setFilter(tab.id)}
            className={`px-2.5 py-1 rounded-[6px] font-medium transition-all cursor-pointer ${
              filter === tab.id
                ? "bg-emerald-600 text-white shadow-xs font-semibold"
                : "bg-black/5 dark:bg-white/5 text-[#52525b] dark:text-[#d4d4d8] hover:bg-black/10 dark:hover:bg-white/10"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Hotel Cards List */}
      <div className="space-y-3">
        {displayedHotels.map((h, idx) => {
          const hotelPrice = h.lowest_price_inr || h.indicative_price_inr || 0;
          const isCheapest = minPrice && hotelPrice === minPrice;
          const isSelected = selectedHotel && selectedHotel.hotel_name === h.hotel_name;
          const primaryVendor = h.best_vendor || "Booking.com";
          const vendorUrl = getSafeVendorSearchUrl(h.hotel_name, city, primaryVendor);

          return (
            <div
              key={`${h.hotel_name}-${idx}`}
              className={`p-3.5 sm:p-4 rounded-[12px] bg-white/95 dark:bg-[#15231c]/90 border transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-xs ${
                isSelected
                  ? "border-emerald-500 ring-2 ring-emerald-500/20 bg-emerald-50/40 dark:bg-emerald-950/30"
                  : "border-black/5 dark:border-white/10 hover:border-emerald-400 dark:hover:border-emerald-600"
              }`}
            >
              {/* Hotel Details */}
              <div className="space-y-1.5 flex-1 min-w-[200px]">
                <div className="flex items-center space-x-2">
                  <h4 className="font-bold text-sm text-[#171717] dark:text-white leading-snug">
                    {h.hotel_name}
                  </h4>
                  {isSelected && (
                    <span className="inline-flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-600 text-white shadow-xs shrink-0">
                      <CheckCircle2 className="w-3 h-3 mr-1" /> Selected
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-2 text-xs text-[#71717a] dark:text-[#a1a1aa]">
                  <span className="flex items-center">
                    <MapPin className="w-3 h-3 mr-0.5 text-emerald-600 dark:text-emerald-400" />
                    {h.city || city}
                  </span>
                  {h.rating && (
                    <span className="flex items-center font-semibold text-amber-600 dark:text-amber-400">
                      <Star className="w-3 h-3 fill-amber-400 mr-0.5" />
                      {h.rating} / 5.0
                    </span>
                  )}
                  <span className="text-[11px] font-mono text-[#8f8f8f]">
                    Best on: <strong className="text-[#171717] dark:text-white">{primaryVendor}</strong>
                  </span>
                </div>

                {/* Multi-Vendor Comparison Pills */}
                {h.vendor_offers && h.vendor_offers.length > 0 && (
                  <div className="pt-1 flex flex-wrap items-center gap-1.5 text-[10px]">
                    <span className="text-[#8f8f8f] font-medium mr-0.5">Rates:</span>
                    {h.vendor_offers.slice(0, 4).map((offer, oIdx) => (
                      <a
                        key={oIdx}
                        href={getSafeVendorSearchUrl(h.hotel_name, city, offer.vendor)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`px-2 py-0.5 rounded border transition-all flex items-center space-x-1 ${
                          offer.vendor === primaryVendor
                            ? "bg-emerald-100 dark:bg-emerald-950/80 border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 font-semibold"
                            : "bg-black/5 dark:bg-white/5 border-transparent text-[#52525b] dark:text-[#d4d4d8] hover:border-black/20"
                        }`}
                        title={`View on ${offer.vendor}`}
                      >
                        <span>{offer.vendor}:</span>
                        <span className="font-mono font-bold">₹{offer.price_inr ? offer.price_inr.toLocaleString("en-IN") : `${offer.price_usd}$`}</span>
                      </a>
                    ))}
                  </div>
                )}
              </div>

              {/* Price & Booking Actions */}
              <div className="flex items-center justify-between md:justify-end space-x-3 pt-2 md:pt-0 border-t md:border-t-0 border-black/5 dark:border-white/5 shrink-0">
                <div className="text-left md:text-right">
                  <div className="flex items-center md:justify-end space-x-1">
                    <span className="font-bold text-base text-emerald-700 dark:text-emerald-400">
                      ₹{hotelPrice.toLocaleString("en-IN")}
                    </span>
                    <span className="text-[10px] text-[#71717a] dark:text-[#a1a1aa]">/night</span>
                  </div>
                  <div className="text-[10px] text-[#8f8f8f] font-mono">
                    Indicative Price
                  </div>
                  {isCheapest && (
                    <span className="inline-flex items-center text-[9px] font-bold px-1.5 py-0.2 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 mt-0.5">
                      <Sparkles className="w-2.5 h-2.5 mr-0.5" /> Best Deal
                    </span>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center space-x-1.5">
                  {/* Select Stay Button */}
                  {onSelectHotel && (
                    <button
                      type="button"
                      onClick={() => onSelectHotel({
                        hotel_name: h.hotel_name,
                        city: h.city || city,
                        price_inr: hotelPrice,
                        price_usd: h.lowest_price_usd || h.indicative_price_usd,
                        best_vendor: primaryVendor,
                        booking_url: vendorUrl,
                        status: "selected",
                        price_type: "indicative"
                      })}
                      className={`px-3 py-1.5 rounded-[6px] text-xs font-semibold transition-all cursor-pointer flex items-center space-x-1 ${
                        isSelected
                          ? "bg-emerald-700 text-white shadow-xs"
                          : "bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs"
                      }`}
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{isSelected ? "Selected" : "Select Stay"}</span>
                    </button>
                  )}

                  {/* View on Vendor External Link */}
                  <a
                    href={vendorUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-2.5 py-1.5 rounded-[6px] text-xs font-medium bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-[#3f3f46] dark:text-[#e4e4e7] transition-all flex items-center space-x-1"
                    title={`View on ${primaryVendor}`}
                  >
                    <span>View on {primaryVendor}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer / Disclaimer */}
      <div className="mt-3 pt-2.5 border-t border-emerald-100 dark:border-emerald-900/30 flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#71717a] dark:text-[#a1a1aa] gap-1">
        <div className="flex items-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
          <span>Rates are indicative reference prices from Makcorps. Exact pricing and room availability depend on selected dates on the provider platform.</span>
        </div>
        <div className="flex items-center space-x-2 text-[10px] font-medium text-emerald-700 dark:text-emerald-400 shrink-0">
          <a href={`https://www.booking.com/searchresults.html?ss=${encodeURIComponent(city)}`} target="_blank" rel="noopener noreferrer" className="hover:underline">Booking.com</a>
          <span>•</span>
          <a href={`https://www.agoda.com/search?city=${encodeURIComponent(city)}`} target="_blank" rel="noopener noreferrer" className="hover:underline">Agoda</a>
          <span>•</span>
          <a href={`https://www.makemytrip.com/hotels/`} target="_blank" rel="noopener noreferrer" className="hover:underline">MakeMyTrip</a>
        </div>
      </div>
    </div>
  );
}
