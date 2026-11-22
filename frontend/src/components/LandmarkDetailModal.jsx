import React from "react";
import { X, Star, MapPin, Calendar, Tag, Layers, ExternalLink, ShieldCheck } from "lucide-react";

export default function LandmarkDetailModal({ landmark, onClose }) {
  if (!landmark) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-3xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-100 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 w-9 h-9 rounded-full bg-black/60 text-white flex items-center justify-center hover:bg-black transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Hero Image */}
        <div className="relative h-72 w-full bg-gray-100">
          <img src={landmark.image_url} alt={landmark.name} className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent flex items-end p-6">
            <div>
              <span className="px-3 py-1 rounded-full bg-[#0066cc] text-white text-xs font-semibold uppercase tracking-wider">
                {landmark.category}
              </span>
              <h2 className="text-3xl font-semibold text-white mt-2">{landmark.name}</h2>
              <p className="text-sm text-gray-200 flex items-center space-x-1 mt-1">
                <MapPin className="w-4 h-4 text-blue-300" />
                <span>{landmark.city}, {landmark.state}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6">
          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-[#f5f5f7] rounded-2xl text-center">
            <div>
              <p className="text-[11px] font-medium text-[#7a7a7a] uppercase">Rating</p>
              <p className="text-base font-semibold text-[#1d1d1f] flex items-center justify-center space-x-1 mt-0.5">
                <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                <span>{landmark.rating} / 5.0</span>
              </p>
            </div>
            <div>
              <p className="text-[11px] font-medium text-[#7a7a7a] uppercase">Ideal Season</p>
              <p className="text-xs font-semibold text-[#1d1d1f] mt-1">{landmark.ideal_season}</p>
            </div>
            <div>
              <p className="text-[11px] font-medium text-[#7a7a7a] uppercase">Ticket Price</p>
              <p className="text-xs font-semibold text-[#1d1d1f] mt-1">{landmark.price_info}</p>
            </div>
            <div>
              <p className="text-[11px] font-medium text-[#7a7a7a] uppercase">Destination ID</p>
              <p className="text-xs font-mono font-semibold text-[#0066cc] mt-1">{landmark.id}</p>
            </div>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-base font-semibold text-[#1d1d1f]">About Destination</h3>
            <p className="text-sm text-[#7a7a7a] mt-2 leading-relaxed">{landmark.description}</p>
          </div>

          {/* ResNet-18 & FAISS Inspection Card */}
          <div className="border border-blue-100 bg-blue-50/50 p-5 rounded-2xl">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-[#0066cc]" />
                <span className="text-xs font-semibold text-[#1d1d1f]">Computer Vision Classification & Vector Retrieval</span>
              </div>
              <span className="text-[11px] font-mono text-[#0066cc] bg-white px-2 py-0.5 rounded border border-blue-200">
                FAISS Score: {landmark.similarity_score}
              </span>
            </div>

            <div className="space-y-2">
              <p className="text-xs text-[#7a7a7a]">ResNet-18 Top-3 Probabilities:</p>
              {landmark.top_3_classes.map((cls, i) => (
                <div key={cls.name} className="flex items-center justify-between text-xs bg-white p-2.5 rounded-xl border border-gray-100">
                  <span className="font-medium text-[#1d1d1f]">{i + 1}. {cls.name}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-100 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-[#0066cc] h-full rounded-full" style={{ width: `${cls.confidence}%` }}></div>
                    </div>
                    <span className="font-mono text-[#0066cc] font-semibold">{cls.confidence.toFixed(2)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Footer */}
          <div className="pt-4 border-t border-gray-100 flex items-center justify-between">
            <span className="text-xs text-[#7a7a7a]">Integrated with tourism_master.csv metadata</span>
            <button
              onClick={onClose}
              className="apple-btn-primary py-2 px-6 text-xs"
            >
              Done Inspection
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
