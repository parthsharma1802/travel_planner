import React from "react";
import { Plus, MessageSquare, Compass, Hotel, BookOpen, Camera, Sun, Moon, Trash2, PanelLeftClose, Sparkles, Plane, Train, Ticket, Bookmark } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";

export default function GeminiSidebar({
  activeTab,
  setActiveTab,
  chatHistory,
  activeChatId,
  onSelectHistory,
  onNewChat,
  onDeleteHistory,
  onCloseSidebar,
  isOpen,
  onBookingPrompt
}) {
  const { theme, toggleTheme } = useTheme();

  return (
    <aside
      className={`bg-[#fafafa] dark:bg-[#0a0a0a] border-r border-[#ebebeb] dark:border-[#222222] flex flex-col justify-between h-screen sticky top-0 shrink-0 select-none transition-all duration-300 ease-in-out z-30 overflow-hidden ${
        isOpen ? "w-64 opacity-100" : "w-0 opacity-0 border-r-0"
      }`}
    >
      <div className="w-64 flex flex-col h-full justify-between">
        <div>
          {/* Brand Header */}
          <div className="p-4 border-b border-[#ebebeb] dark:border-[#222222] flex items-center justify-between">
            <div className="flex items-center space-x-2.5 cursor-pointer" onClick={onNewChat}>
              <img
                src="/dora-avatar.png"
                alt="Dora AI"
                className="w-8 h-8 rounded-full object-cover shadow-sm border border-pink-300 dark:border-pink-700"
              />
              <span className="font-bold text-sm tracking-tight text-[#171717] dark:text-white font-sans">
                Dora <span className="text-[#e91e63] dark:text-[#ff4081]">AI</span>
              </span>
            </div>

            {/* Sidebar Close Button */}
            <button
              onClick={onCloseSidebar}
              title="Close sidebar (⌘B)"
              className="p-1.5 rounded-[6px] hover:bg-[#ebebeb] dark:hover:bg-[#222222] text-[#8f8f8f] hover:text-[#171717] dark:hover:text-white transition-colors"
            >
              <PanelLeftClose className="w-4 h-4" />
            </button>
          </div>

          {/* New Chat Button */}
          <div className="p-3">
            <button
              onClick={onNewChat}
              className="w-full flex items-center justify-center space-x-2 px-3 py-2.5 rounded-[6px] bg-[#171717] dark:bg-white hover:bg-black dark:hover:bg-gray-100 text-white dark:text-black text-xs font-medium transition-all shadow-xs"
            >
              <Plus className="w-4 h-4 text-[#0066cc] dark:text-[#2997ff]" />
              <span>New Trip Session</span>
            </button>
          </div>

          {/* Recent Sessions (Dynamically shows real user sessions) */}
          {chatHistory && chatHistory.length > 0 && (
            <div className="px-3 pt-3">
              <p className="px-2 font-mono-eyebrow text-[#8f8f8f] dark:text-[#666666] mb-2">
                Recent Sessions
              </p>
              <div className="space-y-0.5 max-h-56 overflow-y-auto">
                {chatHistory.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => onSelectHistory(item)}
                    className={`group flex items-center justify-between px-2.5 py-1.5 rounded-[6px] text-xs cursor-pointer transition-all ${
                      activeChatId === item.id
                        ? "bg-[#ebebeb] dark:bg-[#222222] text-[#0066cc] dark:text-[#2997ff] font-medium"
                        : "text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-[#f2f2f2] dark:hover:bg-[#18181b]"
                    }`}
                  >
                    <div className="flex items-center space-x-2 truncate">
                      <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-60" />
                      <span className="truncate">{item.title}</span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteHistory(item.id);
                      }}
                      title="Delete session"
                      className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity p-0.5"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
          {/* Booking & Transit Services */}
          <div className="px-3 pt-3">
            <p className="px-2 font-mono-eyebrow text-[#8f8f8f] dark:text-[#666666] mb-1.5 flex items-center justify-between">
              <span>Booking & Transit</span>
              <span className="text-[9px] text-emerald-600 dark:text-emerald-400 font-semibold uppercase">Live Providers</span>
            </p>
            <div className="space-y-0.5">
              <button
                onClick={() => {
                  setActiveTab("chatbot");
                  if (typeof onBookingPrompt === "function") {
                    onBookingPrompt("Search flights for my trip");
                  }
                }}
                className="w-full flex items-center space-x-2.5 px-2.5 py-1.5 rounded-[6px] text-xs text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-sky-50 dark:hover:bg-sky-950/30 hover:text-sky-600 dark:hover:text-sky-400 transition-all cursor-pointer group"
              >
                <Plane className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400 group-hover:scale-110 transition-transform" />
                <span>Flight Booking (Google)</span>
              </button>

              <button
                onClick={() => {
                  setActiveTab("chatbot");
                  if (typeof onBookingPrompt === "function") {
                    onBookingPrompt("Search trains for my trip");
                  }
                }}
                className="w-full flex items-center space-x-2.5 px-2.5 py-1.5 rounded-[6px] text-xs text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-amber-50 dark:hover:bg-amber-950/30 hover:text-amber-600 dark:hover:text-amber-400 transition-all cursor-pointer group"
              >
                <Train className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform" />
                <span>Train Booking (IRCTC)</span>
              </button>

              <button
                onClick={() => {
                  setActiveTab("chatbot");
                  if (typeof onBookingPrompt === "function") {
                    onBookingPrompt("Find hotels for my destination");
                  }
                }}
                className="w-full flex items-center space-x-2.5 px-2.5 py-1.5 rounded-[6px] text-xs text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-emerald-50 dark:hover:bg-emerald-950/30 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all cursor-pointer group"
              >
                <Hotel className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform" />
                <span>Hotel Stays (Makcorps)</span>
              </button>
            </div>
          </div>

          <div className="px-3 pt-4">
            <p className="px-2 font-mono-eyebrow text-[#8f8f8f] dark:text-[#666666] mb-1.5">
              Travel Extensions
            </p>
            <div className="space-y-0.5">
              <button
                onClick={() => setActiveTab("trips")}
                className={`w-full flex items-center space-x-2.5 px-2.5 py-1.5 rounded-[6px] text-xs transition-all ${
                  activeTab === "trips"
                    ? "bg-[#ebebeb] dark:bg-[#222222] text-[#0066cc] dark:text-[#2997ff] font-medium"
                    : "text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-[#f2f2f2] dark:hover:bg-[#18181b]"
                }`}
              >
                <Bookmark className="w-3.5 h-3.5 opacity-70" />
                <span>Saved Trips & Itineraries</span>
              </button>

              <button
                onClick={() => setActiveTab("discover")}
                className={`w-full flex items-center space-x-2.5 px-2.5 py-1.5 rounded-[6px] text-xs transition-all ${
                  activeTab === "discover"
                    ? "bg-[#ebebeb] dark:bg-[#222222] text-[#0066cc] dark:text-[#2997ff] font-medium"
                    : "text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-[#f2f2f2] dark:hover:bg-[#18181b]"
                }`}
              >
                <Compass className="w-3.5 h-3.5 opacity-70" />
                <span>Destinations Catalogue</span>
              </button>

              <button
                onClick={() => setActiveTab("hotels")}
                className={`w-full flex items-center space-x-2.5 px-2.5 py-1.5 rounded-[6px] text-xs transition-all ${
                  activeTab === "hotels"
                    ? "bg-[#ebebeb] dark:bg-[#222222] text-[#0066cc] dark:text-[#2997ff] font-medium"
                    : "text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-[#f2f2f2] dark:hover:bg-[#18181b]"
                }`}
              >
                <Hotel className="w-3.5 h-3.5 opacity-70" />
                <span>Stays & Accommodations</span>
              </button>

              <button
                onClick={() => setActiveTab("journal")}
                className={`w-full flex items-center space-x-2.5 px-2.5 py-1.5 rounded-[6px] text-xs transition-all ${
                  activeTab === "journal"
                    ? "bg-[#ebebeb] dark:bg-[#222222] text-[#0066cc] dark:text-[#2997ff] font-medium"
                    : "text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-[#f2f2f2] dark:hover:bg-[#18181b]"
                }`}
              >
                <BookOpen className="w-3.5 h-3.5 opacity-70" />
                <span>Travel Journal</span>
              </button>

              <button
                onClick={() => setActiveTab("visual_search")}
                className={`w-full flex items-center space-x-2.5 px-2.5 py-1.5 rounded-[6px] text-xs transition-all ${
                  activeTab === "visual_search"
                    ? "bg-[#ebebeb] dark:bg-[#222222] text-[#0066cc] dark:text-[#2997ff] font-medium"
                    : "text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-[#f2f2f2] dark:hover:bg-[#18181b]"
                }`}
              >
                <Camera className="w-3.5 h-3.5 opacity-70" />
                <span>Visual AI Search</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer Controls */}
        <div className="p-3 border-t border-[#ebebeb] dark:border-[#222222] space-y-2">
          <button
            onClick={toggleTheme}
            className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-[6px] text-xs text-[#4d4d4d] dark:text-[#a1a1a1] hover:bg-[#f2f2f2] dark:hover:bg-[#18181b] transition-colors"
          >
            <span className="flex items-center space-x-2">
              {theme === "dark" ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-blue-600" />}
              <span>{theme === "dark" ? "Light Mode" : "Dark Mode"}</span>
            </span>
            <span className="font-mono text-[10px] uppercase text-[#8f8f8f]">{theme}</span>
          </button>

          <div className="flex items-center space-x-2 px-2.5 py-1.5 rounded-[6px] bg-white dark:bg-[#111111] border border-[#ebebeb] dark:border-[#222222]">
            <img src="/dora-avatar.png" alt="Dora AI" className="w-5 h-5 rounded-full object-cover" />
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-[#171717] dark:text-white truncate">Dora AI Explorer</p>
              <p className="text-[10px] font-mono text-pink-600 dark:text-pink-400">Smart Travel Suite</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
