import React from "react";
import { Sparkles, ArrowRight, Camera, ShieldCheck } from "lucide-react";
import { MOCK_FILTER_CATEGORIES } from "../data/mockData";

export default function HeroSection({ selectedCategory, setSelectedCategory, onExploreClick }) {
  return (
    <section className="relative bg-white pt-12 pb-16 overflow-hidden">
      <div className="max-w-7xl mx-auto px-6 text-center">
        {/* Apple Sub-headline pill */}
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#f5f5f7] border border-gray-200/60 mb-6">
          <Sparkles className="w-3.5 h-3.5 text-[#0066cc]" />
          <span className="text-xs font-medium text-[#1d1d1f]">
            Apple Silicon M4 Accelerated — 95.39% Retrieval Accuracy
          </span>
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-6xl font-semibold tracking-tight text-[#1d1d1f] max-w-4xl mx-auto leading-[1.08]">
          Explore India's Heritage Through <span className="text-[#0066cc]">Computer Vision</span>
        </h1>

        {/* Subtitle */}
        <p className="mt-5 text-lg sm:text-xl text-[#7a7a7a] max-w-2xl mx-auto font-normal leading-relaxed">
          Upload any monument photo to instantly identify landmarks with ResNet-18 transfer learning and FAISS 512-dimensional vector similarity.
        </p>

        {/* CTA Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <button onClick={onExploreClick} className="apple-btn-primary flex items-center space-x-2 w-full sm:w-auto justify-center">
            <Camera className="w-4 h-4" />
            <span>Try Visual Search</span>
          </button>
          <a href="#gallery" className="apple-btn-secondary flex items-center space-x-2 w-full sm:w-auto justify-center">
            <span>Browse 24 Landmarks</span>
            <ArrowRight className="w-4 h-4 text-[#7a7a7a]" />
          </a>
        </div>

        {/* Hardware Status Strip */}
        <div className="mt-10 flex items-center justify-center space-x-6 text-xs text-[#7a7a7a]">
          <div className="flex items-center space-x-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Apple Silicon MPS</span>
          </div>
          <span className="text-gray-300">•</span>
          <div>24 Canonical Landmark Classes</div>
          <span className="text-gray-300">•</span>
          <div>3,572 L2-Normalized Vectors</div>
        </div>

        {/* Apple Style Filter Chips */}
        <div className="mt-12 flex items-center justify-center gap-2 flex-wrap border-t border-b border-[#f0f0f0] py-4">
          {MOCK_FILTER_CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                  isSelected
                    ? "bg-[#1d1d1f] text-white shadow-sm font-semibold"
                    : "bg-[#f5f5f7] text-[#7a7a7a] hover:text-[#1d1d1f] hover:bg-[#e8e8ed]"
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
