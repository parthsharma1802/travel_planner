import React, { useState } from "react";
import { Sparkles, Camera, Search, Compass, MapPin, Hotel, Calendar, BookOpen, Sun, Moon, Menu } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";
import MobileDrawer from "./MobileDrawer";

export default function Header({ activeTab, setActiveTab, onOpenSearch }) {
  const { theme, toggleTheme } = useTheme();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const navItems = [
    { id: "ai_assistant", label: "AI Concierge", icon: Sparkles },
    { id: "discover", label: "Explore", icon: Compass },
    { id: "destinations", label: "Destinations", icon: MapPin },
    { id: "hotels", label: "Stays & Hotels", icon: Hotel },
    { id: "trips", label: "My Trips", icon: Calendar },
    { id: "journal", label: "Travel Journal", icon: BookOpen },
    { id: "visual_search", label: "Photo Search", icon: Camera },
  ];

  return (
    <>
      <header className="sticky top-0 z-40 apple-glass-nav transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
          {/* Logo & Commercial Brand Name */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab("ai_assistant")}>
            <img
              src="/dora-avatar.png"
              alt="Dora AI"
              className="w-9 h-9 rounded-full object-cover shadow-sm border border-pink-300 dark:border-pink-700 ring-2 ring-pink-500/20"
            />
            <div className="flex items-center">
              <span className="font-bold text-lg tracking-tight text-[#1d1d1f] dark:text-white">
                Dora <span className="text-[#e91e63] dark:text-[#ff4081]">AI</span>
              </span>
              <span className="ml-2 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider bg-pink-50 dark:bg-pink-950/60 text-[#e91e63] dark:text-[#ff4081] rounded-full border border-pink-200 dark:border-pink-900/50">
                Explorer
              </span>
            </div>
          </div>

          {/* Commercial Navigation Items */}
          <nav className="hidden lg:flex items-center space-x-1 bg-[#f5f5f7] dark:bg-zinc-800/80 p-1 rounded-full border border-black/5 dark:border-white/10">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                    isActive
                      ? "bg-white dark:bg-zinc-900 text-[#1d1d1f] dark:text-white shadow-sm font-semibold"
                      : "text-[#7a7a7a] dark:text-zinc-400 hover:text-[#1d1d1f] dark:hover:text-white"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={onOpenSearch}
              className="flex items-center space-x-2 bg-[#f5f5f7] dark:bg-zinc-800 hover:bg-[#e8e8ed] dark:hover:bg-zinc-700 text-[#7a7a7a] dark:text-zinc-300 px-3 py-1.5 rounded-full text-xs transition-colors"
            >
              <Search className="w-3.5 h-3.5" />
              <span className="hidden xl:inline">Search destinations...</span>
              <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700 rounded text-gray-500 dark:text-zinc-400">
                ⌘K
              </kbd>
            </button>

            {/* Light / Dark Mode Toggle */}
            <button
              onClick={toggleTheme}
              title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
              className="w-8 h-8 rounded-full bg-[#f5f5f7] dark:bg-zinc-800 hover:bg-[#e8e8ed] dark:hover:bg-zinc-700 flex items-center justify-center text-[#1d1d1f] dark:text-white transition-colors"
            >
              {theme === "dark" ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-blue-600" />
              )}
            </button>

            {/* Mobile Drawer Button */}
            <button
              onClick={() => setIsMobileOpen(true)}
              className="lg:hidden w-8 h-8 rounded-full bg-[#f5f5f7] dark:bg-zinc-800 flex items-center justify-center text-gray-700 dark:text-gray-200"
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu Drawer */}
      <MobileDrawer
        isOpen={isMobileOpen}
        onClose={() => setIsMobileOpen(false)}
        navItems={navItems}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSearch={onOpenSearch}
      />
    </>
  );
}
