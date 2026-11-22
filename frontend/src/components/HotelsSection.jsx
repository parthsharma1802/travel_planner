import React from "react";
import { Star, MapPin, Check, Wifi, Sparkles, Coffee, Shield } from "lucide-react";
import { LUXURY_HOTELS } from "../data/travelProductData";

export default function HotelsSection() {
  return (
    <section className="py-12 bg-[#f5f5f7] dark:bg-[#1c1c1e]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-[#0066cc] dark:text-[#2997ff]">
              Stays & Accommodation
            </span>
            <h2 className="text-3xl font-semibold text-[#1d1d1f] dark:text-white tracking-tight mt-1">
              Handpicked Royal Palaces & Luxury Stays
            </h2>
          </div>
          <p className="text-xs text-[#7a7a7a] dark:text-zinc-400 mt-2 md:mt-0">
            Exclusive heritage properties near landmark monuments
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {LUXURY_HOTELS.map((hotel) => (
            <div
              key={hotel.id}
              className="apple-card overflow-hidden border border-gray-200 dark:border-zinc-800 flex flex-col justify-between"
            >
              <div>
                <div className="relative h-60 w-full overflow-hidden">
                  <img src={hotel.image_url} alt={hotel.name} className="w-full h-full object-cover" />
                  <div className="absolute top-3 right-3 bg-white/90 dark:bg-black/80 backdrop-blur-md px-3 py-1 rounded-full text-xs font-semibold text-[#1d1d1f] dark:text-white flex items-center space-x-1">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    <span>{hotel.rating}</span>
                  </div>
                </div>

                <div className="p-6">
                  <div className="flex items-center space-x-1.5 text-xs text-[#7a7a7a] dark:text-zinc-400">
                    <MapPin className="w-3.5 h-3.5 text-[#0066cc]" />
                    <span>{hotel.city}, {hotel.state}</span>
                  </div>
                  <h3 className="text-xl font-semibold text-[#1d1d1f] dark:text-white mt-1">{hotel.name}</h3>
                  <p className="text-xs text-[#7a7a7a] dark:text-zinc-400 mt-1 italic">"{hotel.tagline}"</p>

                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {hotel.amenities.map((am) => (
                      <span key={am} className="px-2.5 py-1 rounded-full bg-[#f5f5f7] dark:bg-zinc-800 text-[11px] text-[#1d1d1f] dark:text-white font-medium border border-gray-200 dark:border-zinc-700 flex items-center space-x-1">
                        <Check className="w-3 h-3 text-emerald-600" />
                        <span>{am}</span>
                      </span>
                    ))}
                  </div>

                  <p className="text-xs text-[#0066cc] dark:text-[#2997ff] font-medium mt-4">
                    📍 {hotel.distance_to_monument}
                  </p>
                </div>
              </div>

              <div className="p-6 pt-0 border-t border-gray-100 dark:border-zinc-800 mt-4 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-[#7a7a7a] uppercase font-semibold">Starting From</span>
                  <p className="text-lg font-bold text-[#1d1d1f] dark:text-white">{hotel.price_per_night} <span className="text-xs font-normal text-gray-500">/ night</span></p>
                </div>

                <button className="apple-btn-primary text-xs py-2 px-5">
                  Check Availability
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
