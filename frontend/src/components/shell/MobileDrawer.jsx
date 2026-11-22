import React from "react";
import { X, Sun, Moon, Search } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";

export default function MobileDrawer({ isOpen, onClose, navItems, activeTab, setActiveTab, onOpenSearch }) {
  const { theme, toggleTheme } = useTheme();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 md:hidden flex flex-col bg-white/95 dark:bg-black/95 backdrop-blur-xl animate-fadeIn">
      {/* Drawer Header */}
      <div className="h-14 px-6 flex items-center justify-between border-b border-black/5 dark:border-white/10">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-full bg-white p-0.5 border border-pink-300 shadow-sm overflow-hidden flex items-center justify-center">
            <img src="/dora-ai-logo.png" alt="Dora AI" className="w-full h-full object-contain rounded-full" />
          </div>
          <span className="font-bold text-lg text-[#1d1d1f] dark:text-white">Dora AI</span>
        </div>
        <button
          onClick={onClose}
          className="w-8 h-8 rounded-full bg-gray-100 dark:bg-zinc-800 flex items-center justify-center text-gray-700 dark:text-gray-200"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Nav Links */}
      <div className="flex-1 px-6 py-8 space-y-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => {
                setActiveTab(item.id);
                onClose();
              }}
              className={`w-full flex items-center space-x-3 p-3.5 rounded-2xl text-base font-medium transition-all ${
                isActive
                  ? "bg-[#0066cc] dark:bg-[#2997ff] text-white font-semibold shadow-sm"
                  : "text-[#1d1d1f] dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-zinc-800"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          );
        })}

        <div className="pt-6 border-t border-gray-100 dark:border-zinc-800 space-y-3">
          <button
            onClick={() => {
              onOpenSearch();
              onClose();
            }}
            className="w-full flex items-center space-x-3 p-3.5 rounded-2xl bg-gray-100 dark:bg-zinc-800 text-gray-700 dark:text-gray-200 text-sm font-medium"
          >
            <Search className="w-4 h-4 text-gray-500" />
            <span>Search Landmarks (⌘K)</span>
          </button>

          <button
            onClick={toggleTheme}
            className="w-full flex items-center justify-between p-3.5 rounded-2xl bg-gray-100 dark:bg-zinc-800 text-gray-700 dark:text-gray-200 text-sm font-medium"
          >
            <span className="flex items-center space-x-3">
              {theme === "dark" ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-blue-500" />}
              <span>{theme === "dark" ? "Light Mode" : "Dark Mode"}</span>
            </span>
            <span className="text-xs text-gray-400 font-mono uppercase">{theme}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
