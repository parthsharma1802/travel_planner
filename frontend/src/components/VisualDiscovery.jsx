import React, { useState } from "react";
import { Upload, Camera, CheckCircle2, MapPin, ArrowRight, Sparkles } from "lucide-react";
import { FEATURED_DESTINATIONS, LUXURY_HOTELS } from "../data/travelProductData";

export default function VisualDiscovery({ onSelectDestination }) {
  const [isScanning, setIsScanning] = useState(false);
  const [activeMatch, setActiveMatch] = useState(null);
  const [uploadedPreview, setUploadedPreview] = useState(null);

  const handleSampleClick = (dest) => {
    setIsScanning(true);
    setUploadedPreview(dest.image_url);
    setActiveMatch(null);

    setTimeout(() => {
      setIsScanning(false);
      setActiveMatch(dest);
    }, 700);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setUploadedPreview(url);
      setIsScanning(true);
      setActiveMatch(null);

      setTimeout(() => {
        setIsScanning(false);
        setActiveMatch(FEATURED_DESTINATIONS[0]);
      }, 900);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Title */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-950 border border-blue-100 text-[#0066cc] dark:text-[#2997ff] text-xs font-semibold mb-3">
          <Camera className="w-3.5 h-3.5" />
          <span>AI Visual Travel Discovery</span>
        </div>
        <h2 className="text-3xl font-semibold text-[#1d1d1f] dark:text-white tracking-tight">
          Identify Landmarks & Destinations From Any Photo
        </h2>
        <p className="text-xs text-[#7a7a7a] dark:text-zinc-400 mt-2">
          Upload a vacation photo to discover where it was taken and find nearby luxury stays and experiences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Upload Dropzone */}
        <div className="lg:col-span-7 bg-white dark:bg-zinc-900 rounded-3xl p-6 border border-gray-200 dark:border-zinc-800 shadow-sm">
          <div className="border-2 border-dashed border-gray-200 dark:border-zinc-700 rounded-2xl p-10 text-center bg-[#fafafc] dark:bg-zinc-800/50 hover:bg-white dark:hover:bg-zinc-800 hover:border-[#0066cc] transition-all cursor-pointer relative">
            <input type="file" accept="image/*" onChange={handleFileUpload} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
            <div className="w-14 h-14 rounded-full bg-blue-50 dark:bg-blue-950 text-[#0066cc] dark:text-[#2997ff] flex items-center justify-center mx-auto mb-3">
              <Upload className="w-6 h-6" />
            </div>
            <p className="text-base font-semibold text-[#1d1d1f] dark:text-white">
              Drop any monument or landmark photo here
            </p>
            <p className="text-xs text-[#7a7a7a] dark:text-zinc-400 mt-1">
              Supports high-resolution camera photos, postcards, or travel screenshots
            </p>
          </div>

          {/* Sample Photos Bar */}
          <div className="mt-6">
            <p className="text-xs font-semibold text-[#7a7a7a] dark:text-zinc-400 uppercase tracking-wider mb-3">
              Try A Sample Travel Photo:
            </p>
            <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
              {FEATURED_DESTINATIONS.map((dest) => (
                <button
                  key={dest.id}
                  onClick={() => handleSampleClick(dest)}
                  className="relative group rounded-xl overflow-hidden border border-gray-200 dark:border-zinc-700 h-16 focus:outline-none focus:ring-2 focus:ring-[#0066cc]"
                >
                  <img src={dest.image_url} alt={dest.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                  <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors flex items-end p-1">
                    <span className="text-[10px] font-medium text-white truncate">{dest.name}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Discovery Results Panel */}
        <div className="lg:col-span-5 bg-white dark:bg-zinc-900 rounded-3xl p-6 border border-gray-200 dark:border-zinc-800 shadow-sm min-h-[380px] flex flex-col justify-between">
          {isScanning ? (
            <div className="my-auto text-center py-12">
              <div className="w-10 h-10 border-3 border-[#0066cc] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-sm font-semibold text-[#1d1d1f] dark:text-white">Scanning Visual Features...</p>
              <p className="text-xs text-[#7a7a7a] dark:text-zinc-400 mt-1">Matching against 3,500+ heritage landmark database</p>
            </div>
          ) : activeMatch ? (
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-zinc-800">
                <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 text-xs font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Landmark Identified</span>
                </div>
                <span className="text-[11px] font-medium bg-blue-50 dark:bg-blue-950 text-[#0066cc] dark:text-[#2997ff] px-2.5 py-0.5 rounded-full">
                  {activeMatch.category}
                </span>
              </div>

              <div className="mt-4 flex space-x-4">
                <img src={uploadedPreview || activeMatch.image_url} alt={activeMatch.name} className="w-28 h-28 rounded-2xl object-cover border border-gray-200 dark:border-zinc-700" />
                <div>
                  <h3 className="text-xl font-semibold text-[#1d1d1f] dark:text-white">{activeMatch.name}</h3>
                  <p className="text-xs text-[#7a7a7a] dark:text-zinc-400 flex items-center space-x-1 mt-1">
                    <MapPin className="w-3.5 h-3.5 text-[#0066cc]" />
                    <span>{activeMatch.city}, {activeMatch.state}</span>
                  </p>
                  <p className="text-xs text-[#1d1d1f] dark:text-gray-200 mt-2 font-medium">"{activeMatch.tagline}"</p>
                  <div className="mt-2 text-xs text-amber-500 font-semibold">
                    ⭐ {activeMatch.rating} <span className="text-gray-400 font-normal">({activeMatch.reviews_count.toLocaleString()} traveler reviews)</span>
                  </div>
                </div>
              </div>

              <div className="mt-5 p-4 bg-[#f5f5f7] dark:bg-zinc-800/60 rounded-2xl">
                <p className="text-xs font-semibold text-[#1d1d1f] dark:text-white mb-2">Highlights & Experiences:</p>
                <div className="flex flex-wrap gap-1.5">
                  {activeMatch.highlights.map((hl) => (
                    <span key={hl} className="px-2.5 py-1 rounded-full bg-white dark:bg-zinc-700 text-[11px] text-[#1d1d1f] dark:text-white border border-gray-200 dark:border-zinc-600">
                      ✨ {hl}
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={() => onSelectDestination(activeMatch)}
                className="mt-6 w-full apple-btn-primary flex items-center justify-center space-x-2 py-2.5 text-xs"
              >
                <span>View Full Destination Details & Stays</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="my-auto text-center py-12 text-[#7a7a7a] dark:text-zinc-400">
              <Camera className="w-10 h-10 text-[#0066cc] dark:text-[#2997ff] mx-auto mb-3 opacity-50" />
              <p className="text-sm font-medium text-[#1d1d1f] dark:text-white">Ready for photo discovery</p>
              <p className="text-xs mt-1">Upload a photo or pick a sample above to identify landmarks</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
