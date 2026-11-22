import React from "react";
import { Star, MapPin, ArrowUpRight } from "lucide-react";

export default function DestinationGrid({ landmarks, onSelectLandmark }) {
  return (
    <section id="gallery" className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-[#0066cc]">
              Canonical Landmarks Dataset
            </span>
            <h2 className="text-3xl font-semibold text-[#1d1d1f] tracking-tight mt-1">
              Curated Heritage Destinations
            </h2>
          </div>
          <p className="text-xs text-[#7a7a7a] mt-2 md:mt-0">
            Showing {landmarks.length} canonical landmarks • Ground-truth validated
          </p>
        </div>

        {/* Card Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {landmarks.map((landmark) => (
            <div
              key={landmark.id}
              onClick={() => onSelectLandmark(landmark)}
              className="apple-card cursor-pointer group flex flex-col overflow-hidden border border-gray-100"
            >
              {/* Image Tile */}
              <div className="relative h-64 w-full overflow-hidden bg-gray-100">
                <img
                  src={landmark.image_url}
                  alt={landmark.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-md px-2.5 py-1 rounded-full text-[11px] font-semibold text-[#1d1d1f] shadow-sm">
                  {landmark.category}
                </div>
                <div className="absolute top-3 right-3 bg-black/60 backdrop-blur-md text-white px-2.5 py-1 rounded-full text-xs font-semibold flex items-center space-x-1">
                  <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                  <span>{landmark.rating}</span>
                </div>
              </div>

              {/* Content Box */}
              <div className="p-6 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold text-[#1d1d1f] group-hover:text-[#0066cc] transition-colors">
                      {landmark.name}
                    </h3>
                    <ArrowUpRight className="w-4 h-4 text-[#7a7a7a] group-hover:text-[#0066cc] transition-colors" />
                  </div>
                  <div className="flex items-center space-x-1.5 text-xs text-[#7a7a7a] mt-1">
                    <MapPin className="w-3.5 h-3.5 text-[#0066cc]" />
                    <span>{landmark.city}, {landmark.state}</span>
                  </div>
                  <p className="mt-3 text-xs text-[#7a7a7a] line-clamp-2 leading-relaxed">
                    {landmark.description}
                  </p>
                </div>

                <div className="mt-5 pt-4 border-t border-[#f0f0f0] flex items-center justify-between text-xs">
                  <span className="text-[#7a7a7a] font-medium">{landmark.reviews_count.toLocaleString()} reviews</span>
                  <span className="font-mono text-[11px] text-[#0066cc] font-semibold">{landmark.id}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
