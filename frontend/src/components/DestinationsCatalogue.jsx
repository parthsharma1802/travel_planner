import React, { useState } from "react";
import { Star, MapPin, Heart, ArrowUpRight, Clock, Calendar } from "lucide-react";

export default function DestinationsCatalogue({ destinations, onSelectDestination }) {
  const [favorites, setFavorites] = useState({});

  const toggleFavorite = (e, id) => {
    e.stopPropagation();
    setFavorites((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <section className="py-12 bg-white dark:bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-[#0066cc] dark:text-[#2997ff]">
              Explore India
            </span>
            <h2 className="text-3xl font-semibold text-[#1d1d1f] dark:text-white tracking-tight mt-1">
              Popular Destinations & Heritage Spots
            </h2>
          </div>
          <p className="text-xs text-[#7a7a7a] dark:text-zinc-400 mt-2 md:mt-0">
            Handpicked cultural landmarks • Rated 4.5+ by travelers
          </p>
        </div>

        {/* Photography Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {destinations.map((dest) => {
            const isFav = favorites[dest.id];
            return (
              <div
                key={dest.id}
                onClick={() => onSelectDestination(dest)}
                className="apple-card cursor-pointer group flex flex-col overflow-hidden border border-gray-200/80 dark:border-zinc-800"
              >
                {/* Image Tile */}
                <div className="relative h-64 w-full overflow-hidden bg-gray-100 dark:bg-zinc-800">
                  <img
                    src={dest.image_url}
                    alt={dest.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-3 left-3 bg-white/90 dark:bg-black/80 backdrop-blur-md px-3 py-1 rounded-full text-[11px] font-semibold text-[#1d1d1f] dark:text-white shadow-sm">
                    {dest.category}
                  </div>
                  
                  {/* Wishlist Heart */}
                  <button
                    onClick={(e) => toggleFavorite(e, dest.id)}
                    className="absolute top-3 right-3 w-9 h-9 rounded-full bg-white/80 dark:bg-black/70 backdrop-blur-md flex items-center justify-center text-gray-700 dark:text-gray-200 hover:scale-110 transition-transform"
                  >
                    <Heart className={`w-4 h-4 ${isFav ? "fill-red-500 text-red-500" : ""}`} />
                  </button>

                  <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-md text-white px-2.5 py-1 rounded-full text-xs font-semibold flex items-center space-x-1">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    <span>{dest.rating} ({dest.reviews_count.toLocaleString()})</span>
                  </div>
                </div>

                {/* Card Content */}
                <div className="p-6 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between">
                      <h3 className="text-xl font-semibold text-[#1d1d1f] dark:text-white group-hover:text-[#0066cc] dark:group-hover:text-[#2997ff] transition-colors">
                        {dest.name}
                      </h3>
                      <ArrowUpRight className="w-4 h-4 text-[#7a7a7a] group-hover:text-[#0066cc] transition-colors" />
                    </div>
                    <div className="flex items-center space-x-1.5 text-xs text-[#7a7a7a] dark:text-zinc-400 mt-1">
                      <MapPin className="w-3.5 h-3.5 text-[#0066cc]" />
                      <span>{dest.city}, {dest.state}</span>
                    </div>
                    <p className="mt-3 text-xs text-[#7a7a7a] dark:text-zinc-400 line-clamp-2 leading-relaxed">
                      {dest.description}
                    </p>
                  </div>

                  <div className="mt-5 pt-4 border-t border-[#f0f0f0] dark:border-zinc-800 flex items-center justify-between text-xs text-[#7a7a7a] dark:text-zinc-400">
                    <span className="flex items-center space-x-1">
                      <Calendar className="w-3.5 h-3.5 text-[#0066cc]" />
                      <span>{dest.best_time}</span>
                    </span>
                    <span className="font-semibold text-[#1d1d1f] dark:text-white">{dest.price_per_person}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
