import React from "react";
import { Sparkles, Globe, Shield, Apple, Smartphone } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-[#f5f5f7] dark:bg-[#1c1c1e] border-t border-[#e0e0e0] dark:border-zinc-800 py-12 mt-20 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-10 border-b border-gray-200 dark:border-zinc-800 text-xs">
          {/* Brand Info */}
          <div className="space-y-3 md:col-span-2">
            <div className="flex items-center space-x-2.5">
              <img
                src="/dora-avatar.png"
                alt="Dora AI"
                className="w-7 h-7 rounded-full object-cover shadow-sm border border-pink-300 dark:border-pink-700"
              />
              <span className="font-bold text-sm text-[#1d1d1f] dark:text-white">Dora AI Travel Platform</span>
            </div>
            <p className="text-[#7a7a7a] dark:text-zinc-400 max-w-sm leading-relaxed">
              Your intelligent AI-powered travel concierge. Seamlessly discover heritage landmarks, plan custom itineraries with Dora AI, and explore stays & transport across India.
            </p>
          </div>

          {/* Platform Directory */}
          <div className="space-y-2">
            <p className="font-semibold text-[#1d1d1f] dark:text-white uppercase tracking-wider text-[11px]">Explore Platform</p>
            <ul className="space-y-1.5 text-[#7a7a7a] dark:text-zinc-400">
              <li><a href="#ai" className="hover:text-[#e91e63] dark:hover:text-[#ff4081] transition-colors">Dora AI Concierge</a></li>
              <li><a href="#destinations" className="hover:text-[#e91e63] dark:hover:text-[#ff4081] transition-colors">Heritage Destinations</a></li>
              <li><a href="#hotels" className="hover:text-[#e91e63] dark:hover:text-[#ff4081] transition-colors">Stays & Hotels</a></li>
              <li><a href="#trips" className="hover:text-[#e91e63] dark:hover:text-[#ff4081] transition-colors">Curated Itineraries</a></li>
              <li><a href="#journal" className="hover:text-[#e91e63] dark:hover:text-[#ff4081] transition-colors">Travel Journal Stories</a></li>
            </ul>
          </div>

          {/* Mobile App Downloads */}
          <div className="space-y-2">
            <p className="font-semibold text-[#1d1d1f] dark:text-white uppercase tracking-wider text-[11px]">Get Dora AI App</p>
            <p className="text-[#7a7a7a] dark:text-zinc-400 text-xs">Experience visual photo search & AI concierge on mobile</p>
            <div className="pt-2 space-y-2">
              <div className="flex items-center space-x-2 bg-white dark:bg-zinc-800 p-2 rounded-xl border border-gray-200 dark:border-zinc-700 cursor-pointer">
                <Apple className="w-5 h-5 text-[#1d1d1f] dark:text-white" />
                <div>
                  <p className="text-[9px] uppercase text-gray-400">Download on the</p>
                  <p className="text-xs font-semibold text-[#1d1d1f] dark:text-white">App Store</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Micro Legal & Copyright */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-[#7a7a7a] dark:text-zinc-500 space-y-2 sm:space-y-0">
          <div>
            © 2026 Dora AI Inc. All rights reserved. Built with modern design.
          </div>
          <div className="flex items-center space-x-4">
            <span className="hover:underline cursor-pointer">Privacy Policy</span>
            <span>•</span>
            <span className="hover:underline cursor-pointer">Terms of Service</span>
            <span>•</span>
            <span className="hover:underline cursor-pointer">Cookie Preferences</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
