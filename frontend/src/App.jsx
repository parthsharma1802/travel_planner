import React, { useState, useEffect } from "react";
import { ThemeProvider } from "./context/ThemeContext";
import GeminiSidebar from "./components/shell/GeminiSidebar";
import EnterpriseChatbot from "./components/EnterpriseChatbot";
import VisualDiscovery from "./components/VisualDiscovery";
import DestinationsCatalogue from "./components/DestinationsCatalogue";
import HotelsSection from "./components/HotelsSection";
import TripsSection from "./components/TripsSection";
import TravelJournal from "./components/TravelJournal";
import LandmarkDetailModal from "./components/LandmarkDetailModal";
import PageContainer from "./components/shell/PageContainer";
import PageHeader from "./components/shell/PageHeader";
import { FEATURED_DESTINATIONS } from "./data/travelProductData";

function GeminiAppWorkspace() {
  const [activeTab, setActiveTab] = useState("chatbot");
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [tripToConvert, setTripToConvert] = useState(null);
  const STORAGE_KEY_CHATS = "smarttrip_chats_store";
  const STORAGE_KEY_HISTORY = "smarttrip_chat_history";

  // Load from localStorage if available, otherwise start with a clean initial session
  const [chatHistory, setChatHistory] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_HISTORY);
      const parsed = saved ? JSON.parse(saved) : [];
      if (parsed.length > 0) return parsed;
      return [{ id: "chat_init", title: "New Trip Session" }];
    } catch {
      return [{ id: "chat_init", title: "New Trip Session" }];
    }
  });

  // Store messages for each chat session ID
  const [chatsStore, setChatsStore] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_CHATS);
      const parsed = saved ? JSON.parse(saved) : null;
      if (parsed && Object.keys(parsed).length > 0) return parsed;
      return { chat_init: [] };
    } catch {
      return { chat_init: [] };
    }
  });

  const [activeChatId, setActiveChatId] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_HISTORY);
      const parsed = saved ? JSON.parse(saved) : [];
      return parsed.length > 0 ? parsed[0].id : "chat_init";
    } catch {
      return "chat_init";
    }
  });
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Persist to localStorage whenever chatHistory or chatsStore updates
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(chatHistory));
    } catch (e) {
      console.warn("Failed to persist chatHistory:", e);
    }
  }, [chatHistory]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_CHATS, JSON.stringify(chatsStore));
    } catch (e) {
      console.warn("Failed to persist chatsStore:", e);
    }
  }, [chatsStore]);

  // Current active chat messages
  const currentMessages = chatsStore[activeChatId] || [];

  // Update messages for current active chat and automatically update title in history
  const setMessagesForActiveChat = (updater) => {
    setChatsStore((prevStore) => {
      const prevMsgs = prevStore[activeChatId] || [];
      const newMsgs = typeof updater === "function" ? updater(prevMsgs) : updater;

      // Auto-update title in chat history on first message
      if (newMsgs.length > 0) {
        const firstUserMsg = newMsgs.find((m) => m.sender === "user");
        if (firstUserMsg) {
          const autoTitle = firstUserMsg.text.slice(0, 26) + (firstUserMsg.text.length > 26 ? "..." : "");
          setChatHistory((prevHist) => {
            const exists = prevHist.some((item) => item.id === activeChatId);
            if (exists) {
              return prevHist.map((item) =>
                item.id === activeChatId ? { ...item, title: autoTitle } : item
              );
            } else {
              return [{ id: activeChatId, title: autoTitle }, ...prevHist];
            }
          });
        }
      }

      return {
        ...prevStore,
        [activeChatId]: newMsgs
      };
    });
  };

  const handleNewChat = () => {
    setActiveTab("chatbot");
    const newId = `chat_${Date.now()}`;
    const newChat = { id: newId, title: "New Trip Session" };
    setChatHistory((prev) => [newChat, ...prev]);
    setChatsStore((prev) => ({ ...prev, [newId]: [] }));
    setActiveChatId(newId);
  };

  const handleSelectHistory = (item) => {
    setActiveTab("chatbot");
    setActiveChatId(item.id);
  };

  const handleDeleteHistory = (id) => {
    setChatHistory((prev) => prev.filter((item) => item.id !== id));
    setChatsStore((prev) => {
      const copy = { ...prev };
      delete copy[id];
      return copy;
    });
    if (activeChatId === id) {
      const remaining = chatHistory.filter((item) => item.id !== id);
      if (remaining.length > 0) {
        setActiveChatId(remaining[0].id);
      } else {
        handleNewChat();
      }
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#ffffff] dark:bg-[#131314] text-[#171717] dark:text-[#f4f4f5] overflow-hidden font-sans">
      {/* Left Gemini Sidebar (Smooth Collapsible Drawer) */}
      <GeminiSidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        chatHistory={chatHistory}
        activeChatId={activeChatId}
        onSelectHistory={handleSelectHistory}
        onNewChat={handleNewChat}
        onDeleteHistory={handleDeleteHistory}
        onCloseSidebar={() => setIsSidebarOpen(false)}
        isOpen={isSidebarOpen}
        onBookingPrompt={(prompt) => {
          setActiveTab("chatbot");
          setMessagesForActiveChat((prev) => [
            ...prev,
            {
              id: Date.now(),
              sender: "user",
              text: prompt
            }
          ]);
        }}
      />

      {/* Main Workspace Area (Smoothly stretches to 100% full width when sidebar is closed) */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative w-full transition-all duration-300 ease-in-out">
        {/* Tab 1: AI Chatbot Workspace (Primary Core) */}
        {activeTab === "chatbot" && (
          <EnterpriseChatbot
            key={activeChatId}
            onSelectDestination={setSelectedDestination}
            isSidebarOpen={isSidebarOpen}
            onOpenSidebar={() => setIsSidebarOpen(true)}
            messages={currentMessages}
            setMessages={setMessagesForActiveChat}
          />
        )}

        {/* Tab: Saved Trips & Portfolio */}
        {activeTab === "trips" && (
          <div className="flex-1 overflow-y-auto">
            <PageContainer className="py-6">
              <PageHeader
                title="Saved Itineraries & Trips"
                subtitle="Manage your custom travel plans, restore itineraries into the AI planner, or explore curated tours."
                badge="Personal Portfolio"
                breadcrumbs={["Home", "Saved Trips"]}
              />
              <TripsSection
                onOpenTrip={(trip) => {
                  setActiveTab("chatbot");
                  const restoredMsg = {
                    id: Date.now(),
                    sender: "ai",
                    text: `Here is your restored trip plan for **${trip.title}** (${trip.destination || 'Custom Trip'}). All itinerary days, stay, and transport selections have been loaded!`,
                    itineraryData: trip.itinerary,
                    routeData: trip.route_data,
                    preferences: {
                      destination: trip.destination,
                      origin: trip.origin,
                      dates: trip.dates,
                      budget: trip.budget,
                      travelers: trip.travelers,
                      duration: trip.duration
                    }
                  };
                  setMessagesForActiveChat((prev) => [...prev, restoredMsg]);
                }}
                onNewTrip={handleNewChat}
                onConvertToJournal={(trip) => {
                  setTripToConvert(trip);
                  setActiveTab("journal");
                }}
              />
            </PageContainer>
          </div>
        )}

        {/* Tab 2: Explore Destinations */}
        {activeTab === "discover" && (
          <div className="flex-1 overflow-y-auto">
            <PageContainer className="py-6">
              <PageHeader
                title="Heritage Destinations"
                subtitle="Browse 24 canonical physical landmark classes from our audited tourism database."
                badge="Destinations"
                breadcrumbs={["Home", "Destinations"]}
              />
              <DestinationsCatalogue
                destinations={FEATURED_DESTINATIONS}
                onSelectDestination={setSelectedDestination}
              />
            </PageContainer>
          </div>
        )}

        {/* Tab 3: Stays & Hotels */}
        {activeTab === "hotels" && (
          <div className="flex-1 overflow-y-auto">
            <PageContainer className="py-6">
              <PageHeader
                title="Luxury Stays & Heritage Hotels"
                subtitle="Handpicked royal palaces, boutique resorts, and 5-star properties offering views of landmark monuments."
                badge="Hotels & Stays"
                breadcrumbs={["Home", "Hotels"]}
              />
              <HotelsSection />
            </PageContainer>
          </div>
        )}

        {/* Tab 4: Travel Journal */}
        {activeTab === "journal" && (
          <div className="flex-1 overflow-y-auto">
            <PageContainer className="py-6">
              <PageHeader
                title="Travel Journal & Photography Guides"
                subtitle="Document your travels, convert saved trips into stories, or read curated guides written by travel editors."
                badge="Journal & Blog"
                breadcrumbs={["Home", "Journal"]}
              />
              <TravelJournal
                initialTripToConvert={tripToConvert}
                onClearInitialTrip={() => setTripToConvert(null)}
              />
            </PageContainer>
          </div>
        )}

        {/* Tab 5: Visual Photo Search */}
        {activeTab === "visual_search" && (
          <div className="flex-1 overflow-y-auto">
            <PageContainer className="py-6">
              <PageHeader
                title="Visual Photo Discovery"
                subtitle="Upload any photo to identify landmarks and discover nearby experiences."
                badge="Photo AI Search"
                breadcrumbs={["Home", "Visual Search"]}
              />
              <VisualDiscovery onSelectDestination={setSelectedDestination} />
            </PageContainer>
          </div>
        )}

        {/* Destination Modal Inspector */}
        {selectedDestination && (
          <LandmarkDetailModal
            landmark={selectedDestination}
            onClose={() => setSelectedDestination(null)}
          />
        )}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <GeminiAppWorkspace />
    </ThemeProvider>
  );
}
