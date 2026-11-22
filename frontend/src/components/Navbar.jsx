import React from "react";
import { Camera, Search, Sparkles, Compass, MapPin, Layers } from "lucide-react";

export default function Navbar({ activeTab, setActiveTab, onOpenSearch }) {
  const navItems = [
    { id: "discover", label: "Discover", icon: Compass },
    { id: "visual_search", label: "Visual Search", icon: Camera },
    { id: "monuments", label: "Monuments", icon: MapPin },
    { id: "embeddings", label: "512-d Vectors", icon: Layers },
  ];

  return (
    <header className="sticky top-0 z-50 apple-glass-nav">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab("discover")}>
          <div className="w-8 h-8 rounded-full bg-white p-0.5 border border-pink-300 shadow-sm flex items-center justify-center overflow-hidden">
            <img src="/dora-ai-logo.png" alt="Dora AI" className="w-full h-full object-contain rounded-full" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">Dora AI</span>
            <span className="ml-2 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider bg-pink-50 text-pink-600 rounded-full border border-pink-200">
              Explorer
            </span>
          </div>
        </div>

        {/* Apple Style Nav Pill Group */}
        <nav className="hidden md:flex items-center space-x-1 bg-[#f5f5f7] p-1 rounded-full border border-black/5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                  isActive
                    ? "bg-white text-[#1d1d1f] shadow-sm font-semibold"
                    : "text-[#7a7a7a] hover:text-[#1d1d1f]"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Action Icons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenSearch}
            className="flex items-center space-x-2 bg-[#f5f5f7] hover:bg-[#e8e8ed] text-[#7a7a7a] hover:text-[#1d1d1f] px-3 py-1.5 rounded-full text-xs transition-colors"
          >
            <Search className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Search landmarks...</span>
          </button>

          <div className="hidden lg:flex items-center space-x-1 text-xs text-[#7a7a7a]">
            <Sparkles className="w-3.5 h-3.5 text-[#0066cc]" />
            <span>ResNet-18 + FAISS</span>
          </div>
        </div>
      </div>
    </header>
  );
}
