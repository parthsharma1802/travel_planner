import React, { useState } from "react";
import { Sparkles, Send, Image as ImageIcon, MapPin, Calendar, Star, Compass, Bot, User, ArrowRight, ShieldCheck } from "lucide-react";
import { AI_SUGGESTION_PROMPTS, FEATURED_DESTINATIONS, LUXURY_HOTELS } from "../data/travelProductData";

export default function AiAssistant({ onSelectDestination }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "ai",
      text: "Namaste! I am your AI Travel Concierge. I can help you design custom itineraries, discover heritage landmarks from your photos, and recommend handpicked luxury stays across India. Where would you like to explore today?",
      suggestions: AI_SUGGESTION_PROMPTS
    }
  ]);

  const [inputQuery, setInputQuery] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [attachedImage, setAttachedImage] = useState(null);

  const handleSend = (textToSend = inputQuery) => {
    if (!textToSend.trim() && !attachedImage) return;

    const userMsg = {
      id: Date.now(),
      sender: "user",
      text: textToSend,
      image: attachedImage
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setAttachedImage(null);
    setIsTyping(true);

    // Simulate Grok API response logic
    setTimeout(() => {
      let aiResponseText = "";
      let recommendations = [];
      let hotels = [];

      const queryLower = textToSend.toLowerCase();

      if (queryLower.includes("qutub") || queryLower.includes("delhi")) {
        aiResponseText = "Delhi offers an extraordinary blend of medieval history and modern culture. Here is a curated highlight for Qutub Minar and surrounding heritage experiences:";
        recommendations = [FEATURED_DESTINATIONS[0], FEATURED_DESTINATIONS[3]];
      } else if (queryLower.includes("taj") || queryLower.includes("agra")) {
        aiResponseText = "Agra is home to the world's most romantic marble masterpiece. Here are the top landmark recommendations and 5-star view hotels:";
        recommendations = [FEATURED_DESTINATIONS[1]];
        hotels = [LUXURY_HOTELS[1]];
      } else if (queryLower.includes("jaipur") || queryLower.includes("hawa")) {
        aiResponseText = "Jaipur's royal architecture is unforgettable. Here is a luxury heritage recommendation:";
        recommendations = [FEATURED_DESTINATIONS[2]];
        hotels = [LUXURY_HOTELS[0]];
      } else {
        aiResponseText = "Here are premier heritage destinations and luxury hotels curated for your journey:";
        recommendations = FEATURED_DESTINATIONS.slice(0, 3);
        hotels = LUXURY_HOTELS.slice(0, 2);
      }

      const aiMsg = {
        id: Date.now() + 1,
        sender: "ai",
        text: aiResponseText,
        recommendations,
        hotels
      };

      setMessages((prev) => [...prev, aiMsg]);
      setIsTyping(false);
    }, 1200);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setAttachedImage(url);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      {/* Header Badge */}
      <div className="text-center mb-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-950 border border-blue-100 dark:border-blue-900/40 text-[#0066cc] dark:text-[#2997ff] text-xs font-semibold mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Grok-Powered AI Travel Concierge</span>
        </div>
        <h1 className="text-3xl font-semibold text-[#1d1d1f] dark:text-white tracking-tight">
          Your Personal AI Travel Assistant
        </h1>
        <p className="text-xs text-[#7a7a7a] dark:text-zinc-400 mt-1">
          Instant itinerary planning, visual landmark recognition & luxury stay recommendations
        </p>
      </div>

      {/* Chat Container Box */}
      <div className="bg-white dark:bg-zinc-900 rounded-3xl border border-gray-200 dark:border-zinc-800 shadow-xl flex flex-col h-[640px] overflow-hidden">
        {/* Messages Scroll Area */}
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${msg.sender === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
            >
              {/* Avatar */}
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-white shrink-0 ${
                  msg.sender === "ai"
                    ? "bg-[#0066cc] dark:bg-[#2997ff]"
                    : "bg-[#1d1d1f] dark:bg-zinc-700"
                }`}
              >
                {msg.sender === "ai" ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
              </div>

              {/* Message Bubble */}
              <div className={`max-w-2xl ${msg.sender === "user" ? "text-right" : ""}`}>
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-[#0066cc] dark:bg-[#2997ff] text-white rounded-tr-none"
                      : "bg-[#f5f5f7] dark:bg-zinc-800 text-[#1d1d1f] dark:text-white rounded-tl-none border border-gray-100 dark:border-zinc-700"
                  }`}
                >
                  {msg.image && (
                    <img src={msg.image} alt="User attachment" className="w-48 h-32 object-cover rounded-xl mb-3 border border-white/20" />
                  )}
                  <p>{msg.text}</p>
                </div>

                {/* Prompt Suggestion Chips */}
                {msg.suggestions && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {msg.suggestions.map((prompt) => (
                      <button
                        key={prompt}
                        onClick={() => handleSend(prompt)}
                        className="px-3 py-1.5 rounded-full text-xs font-medium bg-[#f5f5f7] dark:bg-zinc-800 hover:bg-blue-50 dark:hover:bg-blue-950 text-[#0066cc] dark:text-[#2997ff] border border-blue-100 dark:border-blue-900/30 transition-colors"
                      >
                        ⚡ {prompt}
                      </button>
                    ))}
                  </div>
                )}

                {/* AI Interactive Recommendation Cards */}
                {msg.recommendations && msg.recommendations.length > 0 && (
                  <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
                    {msg.recommendations.map((dest) => (
                      <div
                        key={dest.id}
                        onClick={() => onSelectDestination(dest)}
                        className="bg-white dark:bg-zinc-800 p-3 rounded-2xl border border-gray-200 dark:border-zinc-700 hover:border-[#0066cc] dark:hover:border-[#2997ff] cursor-pointer transition-all flex space-x-3 items-center"
                      >
                        <img src={dest.image_url} alt={dest.name} className="w-16 h-16 rounded-xl object-cover shrink-0" />
                        <div className="min-w-0 flex-1">
                          <h4 className="font-semibold text-xs text-[#1d1d1f] dark:text-white truncate">{dest.name}</h4>
                          <p className="text-[11px] text-[#7a7a7a] dark:text-zinc-400">{dest.city}, {dest.state}</p>
                          <div className="flex items-center space-x-2 mt-1 text-[11px]">
                            <span className="text-[#0066cc] dark:text-[#2997ff] font-semibold">⭐ {dest.rating}</span>
                            <span className="text-gray-300">•</span>
                            <span className="text-gray-500">{dest.price_per_person}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* AI Hotel Cards */}
                {msg.hotels && msg.hotels.length > 0 && (
                  <div className="mt-3 text-left">
                    <p className="text-xs font-semibold text-[#7a7a7a] dark:text-zinc-400 uppercase tracking-wider mb-2">Recommended Luxury Stay:</p>
                    {msg.hotels.map((hotel) => (
                      <div key={hotel.id} className="bg-amber-50/50 dark:bg-amber-950/30 p-3 rounded-2xl border border-amber-200 dark:border-amber-900/40 flex space-x-3 items-center">
                        <img src={hotel.image_url} alt={hotel.name} className="w-16 h-16 rounded-xl object-cover shrink-0" />
                        <div>
                          <h4 className="font-semibold text-xs text-[#1d1d1f] dark:text-white">{hotel.name}</h4>
                          <p className="text-[11px] text-[#7a7a7a] dark:text-zinc-400">{hotel.tagline}</p>
                          <p className="text-xs font-bold text-amber-700 dark:text-amber-400 mt-1">{hotel.price_per_night} / night</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-full bg-[#0066cc] dark:bg-[#2997ff] flex items-center justify-center text-white">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-[#f5f5f7] dark:bg-zinc-800 p-4 rounded-2xl text-xs text-[#7a7a7a] flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-[#0066cc] animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-[#0066cc] animate-bounce delay-100"></div>
                <div className="w-2 h-2 rounded-full bg-[#0066cc] animate-bounce delay-200"></div>
                <span>Curating itinerary & stay options...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-[#f5f5f7] dark:bg-zinc-800/80 border-t border-gray-200 dark:border-zinc-700">
          {attachedImage && (
            <div className="mb-3 flex items-center space-x-2 bg-white dark:bg-zinc-900 p-2 rounded-xl border border-gray-200 w-fit">
              <img src={attachedImage} alt="Attachment" className="w-10 h-10 rounded-lg object-cover" />
              <span className="text-xs text-[#7a7a7a]">Image attached for landmark recognition</span>
              <button onClick={() => setAttachedImage(null)} className="text-xs text-red-500 font-bold ml-2">✕</button>
            </div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center space-x-2"
          >
            <label className="p-2.5 rounded-full bg-white dark:bg-zinc-900 hover:bg-gray-100 dark:hover:bg-zinc-700 text-[#7a7a7a] cursor-pointer transition-colors border border-gray-200 dark:border-zinc-700">
              <ImageIcon className="w-4 h-4 text-[#0066cc] dark:text-[#2997ff]" />
              <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
            </label>

            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask AI Concierge: 'Plan 4-day Agra & Delhi luxury tour'..."
              className="flex-1 bg-white dark:bg-zinc-900 text-sm px-4 py-2.5 rounded-full border border-gray-200 dark:border-zinc-700 text-[#1d1d1f] dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0066cc]"
            />

            <button
              type="submit"
              disabled={!inputQuery.trim() && !attachedImage}
              className="apple-btn-primary p-2.5 !rounded-full disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
