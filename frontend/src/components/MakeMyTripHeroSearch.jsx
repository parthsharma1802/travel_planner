import React, { useState } from "react";
import { Hotel, Plane, Calendar, MapPin, Search, Users, Car, Train, Sparkles } from "lucide-react";

export default function MakeMyTripHeroSearch({ onSearch }) {
  const [activeService, setActiveService] = useState("packages");
  const [destination, setDestination] = useState("Delhi & Taj Mahal, Agra");
  const [travelDates, setTravelDates] = useState("Oct 12 - Oct 16, 2026");
  const [guests, setGuests] = useState("2 Adults, 1 Room");

  const services = [
    { id: "packages", label: "Holiday Packages", icon: Sparkles },
    { id: "hotels", label: "Hotels & Stays", icon: Hotel },
    { id: "flights", label: "Flights", icon: Plane },
    { id: "cabs", label: "Outstation Cabs", icon: Car },
    { id: "trains", label: "Trains", icon: Train },
  ];

  return (
    <div className="relative bg-gradient-to-b from-[#004b99] via-[#0066cc] to-[#0055b3] text-white pt-10 pb-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Service Category Bar */}
        <div className="flex items-center justify-center space-x-2 sm:space-x-4 bg-white/10 backdrop-blur-md p-1.5 rounded-full max-w-2xl mx-auto mb-8 border border-white/20">
          {services.map((srv) => {
            const Icon = srv.icon;
            const isActive = activeService === srv.id;
            return (
              <button
                key={srv.id}
                onClick={() => setActiveService(srv.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-white text-[#0066cc] shadow-lg scale-105"
                    : "text-white/80 hover:text-white hover:bg-white/10"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{srv.label}</span>
              </button>
            );
          })}
        </div>

        {/* Hero Heading */}
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-5xl font-semibold tracking-tight leading-tight">
            Book India's Finest Heritage Packages & Luxury Stays
          </h1>
          <p className="text-sm text-white/80 mt-2 max-w-xl mx-auto font-normal">
            AI-curated travel itineraries, landmark photo search, and handpicked palace hotels
          </p>
        </div>

        {/* Commercial Search Bar Card */}
        <div className="bg-white dark:bg-zinc-900 rounded-3xl p-6 shadow-2xl text-[#1d1d1f] dark:text-white border border-white/20">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
            {/* Destination Input */}
            <div className="md:col-span-4 p-3 bg-[#f5f5f7] dark:bg-zinc-800 rounded-2xl hover:bg-gray-200/60 transition-colors">
              <label className="text-[10px] font-bold uppercase tracking-wider text-[#0066cc] dark:text-[#2997ff] flex items-center space-x-1">
                <MapPin className="w-3 h-3" />
                <span>Destination or Monument</span>
              </label>
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="e.g. Qutub Minar, Taj Mahal, Jaipur"
                className="w-full bg-transparent text-sm font-semibold text-[#1d1d1f] dark:text-white focus:outline-none mt-1"
              />
            </div>

            {/* Travel Dates */}
            <div className="md:col-span-3 p-3 bg-[#f5f5f7] dark:bg-zinc-800 rounded-2xl hover:bg-gray-200/60 transition-colors">
              <label className="text-[10px] font-bold uppercase tracking-wider text-[#0066cc] dark:text-[#2997ff] flex items-center space-x-1">
                <Calendar className="w-3 h-3" />
                <span>Travel Dates</span>
              </label>
              <input
                type="text"
                value={travelDates}
                onChange={(e) => setTravelDates(e.target.value)}
                className="w-full bg-transparent text-sm font-semibold text-[#1d1d1f] dark:text-white focus:outline-none mt-1"
              />
            </div>

            {/* Guests & Rooms */}
            <div className="md:col-span-3 p-3 bg-[#f5f5f7] dark:bg-zinc-800 rounded-2xl hover:bg-gray-200/60 transition-colors">
              <label className="text-[10px] font-bold uppercase tracking-wider text-[#0066cc] dark:text-[#2997ff] flex items-center space-x-1">
                <Users className="w-3 h-3" />
                <span>Guests & Rooms</span>
              </label>
              <input
                type="text"
                value={guests}
                onChange={(e) => setGuests(e.target.value)}
                className="w-full bg-transparent text-sm font-semibold text-[#1d1d1f] dark:text-white focus:outline-none mt-1"
              />
            </div>

            {/* Search Button */}
            <div className="md:col-span-2">
              <button
                onClick={() => onSearch({ destination, travelDates, guests })}
                className="w-full py-4 bg-[#0066cc] hover:bg-[#0055b3] text-white rounded-2xl font-semibold text-sm shadow-md hover:scale-105 transition-all flex items-center justify-center space-x-2"
              >
                <Search className="w-4 h-4" />
                <span>SEARCH</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
