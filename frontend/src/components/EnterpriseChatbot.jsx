import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles, Send, Image as ImageIcon, FileText, Mic, Copy, Download, Trash2,
  Bot, User, ChevronDown, Check, Star, MapPin, Calendar as CalendarIcon, Layers, ExternalLink,
  ShieldCheck, DollarSign, Compass, ArrowRight, X, ChevronRight, CornerDownLeft, Terminal, PanelLeftOpen, Sun, Moon, CloudSun, Wind, Droplets, HelpCircle, CheckCircle2, Edit3, Plane, Train, Hotel, ShoppingBag, Bookmark
} from "lucide-react";
import { FEATURED_DESTINATIONS, LUXURY_HOTELS } from "../data/travelProductData";
import { useTheme } from "../context/ThemeContext";
import RouteMapWidget from "./RouteMapWidget";
import FlightBookingWidget from "./FlightBookingWidget";
import TrainBookingWidget from "./TrainBookingWidget";
import HotelBookingWidget from "./HotelBookingWidget";
import BookingReviewModal from "./BookingReviewModal";
import TravelCalendarModal from "./TravelCalendarModal";
import ItineraryCard from "./ItineraryCard";
import MarkdownRenderer from "./MarkdownRenderer";

export default function EnterpriseChatbot({ onSelectDestination, isSidebarOpen, onOpenSidebar, messages, setMessages }) {
  const { theme, toggleTheme } = useTheme();
  const [inputQuery, setInputQuery] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isRecognizingLandmark, setIsRecognizingLandmark] = useState(false);
  const [attachedImage, setAttachedImage] = useState(null);
  const [attachedPdf, setAttachedPdf] = useState(null);
  const [copiedId, setCopiedId] = useState(null);
  
  // Booking Selection & Review State
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [selectedTrain, setSelectedTrain] = useState(null);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [activeTripContext, setActiveTripContext] = useState({});

  // Saved trip state: { [msgId]: boolean }
  const [savingTrip, setSavingTrip] = useState({});
  const [savedTripSuccess, setSavedTripSuccess] = useState({});

  // Multi-select quiz options state: { [qId]: ["Option A", "Option B"] }
  const [quizSelections, setQuizSelections] = useState({});
  // Free-text quiz answers: { [qId]: "text" } — for starting_point, budget, something-else
  const [quizFreeTexts, setQuizFreeTexts] = useState({});
  
  // Interactive Travel Calendar State
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [selectedTravelDates, setSelectedTravelDates] = useState(null);

  // PDF download state: { [msgId]: boolean }
  const [pdfDownloading, setPdfDownloading] = useState({});

  const messagesEndRef = useRef(null);
  const aiMsgRefs = useRef({});

  // ── Helper to guarantee valid itineraryData structure ───────────────────
  const ensureItineraryData = (msg, activeContext = {}) => {
    if (msg.itineraryData && typeof msg.itineraryData === "object" && Array.isArray(msg.itineraryData.days) && msg.itineraryData.days.length > 0) {
      return msg.itineraryData;
    }

    const dest = msg.preferences?.destination || activeContext.destination || "India";
    const orig = msg.preferences?.starting_point || activeContext.origin || "Delhi";
    const budget = msg.preferences?.budget || activeContext.budget || "Standard";

    let days = [];
    if (Array.isArray(msg.itineraryDays) && msg.itineraryDays.length > 0) {
      days = msg.itineraryDays.map((d, idx) => ({
        day: idx + 1,
        title: d.title || `Day ${idx + 1} - ${dest} Highlights`,
        morning: d.details ? d.details.slice(0, 140) : "Morning sightseeing and landmark visits",
        afternoon: "Afternoon cultural exploration and dining",
        evening: "Evening local market stroll and dinner",
        stay: "Verified Accommodations",
        estimated_cost: "Included in budget"
      }));
    } else if (msg.text) {
      const dayRegex = /\*?\*?(Day\s+\d+)\*?\*?[:\s–—-]+([^\n]+)([\s\S]*?)(?=(?:\*?\*?Day\s+\d+\*?\*?|$))/gi;
      let match;
      let idx = 1;
      while ((match = dayRegex.exec(msg.text)) !== null) {
        days.push({
          day: idx++,
          title: match[2].trim().replace(/\*\*/g, ""),
          morning: match[3].trim().replace(/\*\*/g, "").slice(0, 140) || "Morning sightseeing",
          afternoon: "Afternoon exploration and dining",
          evening: "Evening relaxation and local markets",
          stay: "Verified Stays",
          estimated_cost: "Included in budget"
        });
      }
    }

    if (days.length === 0) {
      days = [
        { day: 1, title: `Arrival & Highlights in ${dest}`, morning: "Morning iconic landmark exploration", afternoon: "Cultural sights & regional cuisine", evening: "Sunset point & local bazaar", stay: "Verified Stays", estimated_cost: "₹3,500" },
        { day: 2, title: `Heritage & Culture in ${dest}`, morning: "Historic forts & museum tours", afternoon: "Artisan crafts & scenic views", evening: "Traditional dining & music", stay: "Verified Stays", estimated_cost: "₹3,500" },
        { day: 3, title: `Local Flavor & Departure`, morning: "Local breakfast & souvenir shopping", afternoon: "Scenic walking tour", evening: "Return transit", stay: "Departure", estimated_cost: "₹3,000" }
      ];
    }

    return {
      overview: {
        title: `${days.length}-Day Itinerary for ${dest}`,
        destination: dest,
        origin: orig,
        dates: msg.preferences?.dates || activeContext.dates || "",
        duration: `${days.length} Days`,
        transport: msg.preferences?.transport || activeContext.transport || "Car",
        budget: budget,
        total_estimated_cost: `₹${days.length * 4000}`
      },
      days: days,
      budget_breakdown: {
        transport: "Transit / Fuel",
        accommodation: "Verified Stays",
        food: "Dining & Delicacies",
        activities: "Sightseeing & Passes",
        total: `₹${days.length * 4000}`
      }
    };
  };

  // ── PDF download handler ────────────────────────────────────────────────
  const downloadItineraryPDF = async (msg) => {
    const msgId = msg.id || Date.now();
    setPdfDownloading(prev => ({ ...prev, [msgId]: true }));
    try {
      const itinData = ensureItineraryData(msg, activeTripContext);
      const payload = {
        itinerary: itinData,
        preferences: {
          ...activeTripContext,
          ...(msg.preferences || {}),
        },
        route_data: msg.routeData || null,
        hotel: selectedHotel || msg.hotel || null,
        flight: selectedFlight || msg.flight || null,
        train: selectedTrain || msg.train || null,
        weather: msg.weatherData || activeTripContext?.weather || null,
      };
      const resp = await fetch("/api/itinerary/pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) throw new Error(`Server error ${resp.status}`);
      const blob = await resp.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      const dest = (itinData?.overview?.destination || itinData?.title || "Dora_AI").replace(/[^a-zA-Z0-9]/g, "_");
      a.href     = url;
      a.download = `Dora_AI_${dest}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF download failed:", err);
      alert("PDF generation encountered an issue. Please try again.");
    } finally {
      setPdfDownloading(prev => ({ ...prev, [msgId]: false }));
    }
  };

  // ── Save Trip to Backend Handler ──────────────────────────────────────────
  const saveTripToBackend = async (msg) => {
    if (!msg.itineraryData) return;
    const msgId = msg.id;
    setSavingTrip(prev => ({ ...prev, [msgId]: true }));
    try {
      const payload = {
        title: msg.itineraryData?.overview?.title || `Trip to ${msg.itineraryData?.overview?.destination || activeTripContext.destination || 'India'}`,
        destination: msg.itineraryData?.overview?.destination || activeTripContext.destination || '',
        origin: msg.itineraryData?.overview?.origin || activeTripContext.origin || '',
        dates: msg.itineraryData?.overview?.dates || activeTripContext.dates || '',
        duration: msg.itineraryData?.overview?.duration || '3 Days',
        travelers: msg.itineraryData?.overview?.travelers || activeTripContext.travelers || '2 Travelers',
        budget: msg.itineraryData?.overview?.budget || activeTripContext.budget || '',
        hotel: selectedHotel,
        transport: selectedFlight || selectedTrain,
        itinerary: msg.itineraryData,
        route_data: msg.routeData,
        estimated_total: (selectedHotel?.price_inr || 0) * 3 + (selectedFlight?.price || selectedTrain?.fare_inr || 0)
      };
      const resp = await fetch("/api/trips", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (resp.ok) {
        setSavedTripSuccess(prev => ({ ...prev, [msgId]: true }));
        setTimeout(() => setSavedTripSuccess(prev => ({ ...prev, [msgId]: false })), 3500);
      }
    } catch (err) {
      console.error("Failed to save trip:", err);
      alert("Failed to save trip. Please try again.");
    } finally {
      setSavingTrip(prev => ({ ...prev, [msgId]: false }));
    }
  };

  // Smart Scroll Behavior: Scroll smoothly to the START/TOP of the new AI message answer
  useEffect(() => {
    if (messages.length > 0) {
      const lastMsg = messages[messages.length - 1];
      if (lastMsg.sender === "ai" && aiMsgRefs.current[lastMsg.id]) {
        aiMsgRefs.current[lastMsg.id].scrollIntoView({ behavior: "smooth", block: "start" });
      } else if (lastMsg.sender === "user") {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [messages, isTyping]);

  const handleSend = async (textToSend = inputQuery) => {
    if (!textToSend.trim() && !attachedImage && !attachedPdf && !selectedTravelDates) return;

    let queryText = textToSend;

    // Default friendly prompt when image is uploaded without text
    if (!queryText.trim() && attachedImage) {
      queryText = "What landmark is this? Can you tell me more about it?";
    }

    // Detect explicit calendar/date intent
    const lowerInput = (textToSend || "").toLowerCase().trim();
    if (
      lowerInput.includes("choose my travel dates") ||
      lowerInput.includes("set my trip dates") ||
      lowerInput.includes("i want to select dates") ||
      lowerInput.includes("select dates on calendar") ||
      lowerInput.includes("open calendar")
    ) {
      setIsCalendarOpen(true);
    }

    // Detect PDF download or export intent
    const isPdfExplicitRequest = /\bpdf\b/i.test(lowerInput) && (
      lowerInput.includes("download") ||
      lowerInput.includes("generate") ||
      lowerInput.includes("get") ||
      lowerInput.includes("export") ||
      lowerInput.includes("option") ||
      lowerInput.includes("give") ||
      lowerInput.includes("banao") ||
      lowerInput.includes("chahiye") ||
      lowerInput.includes("de do") ||
      lowerInput.includes("karo") ||
      lowerInput.trim() === "pdf"
    );
    if (isPdfExplicitRequest && !attachedImage) {
      const lastItineraryMsg = [...messages].reverse().find(m => 
        m.sender === "ai" && (
          m.itineraryData || 
          (m.itineraryDays && m.itineraryDays.length > 0) || 
          (m.text && /day\s*1\b/i.test(m.text)) ||
          (m.text && /itinerary/i.test(m.text))
        )
      );
      if (lastItineraryMsg) {
        setInputQuery("");
        const userMsg = { id: Date.now(), sender: "user", text: textToSend };
        const itinData = ensureItineraryData(lastItineraryMsg, activeTripContext);
        const dest = itinData?.overview?.destination || activeTripContext.destination || "Trip";
        const aiConfirmMsg = {
          id: Date.now() + 1,
          sender: "ai",
          text: `📄 **Generating your verified PDF Itinerary for ${dest}...**\n\nYour print-ready A4 document has been prepared and your download has started. You can also re-download it below anytime.`,
          itineraryData: itinData,
          routeData: lastItineraryMsg.routeData,
          preferences: lastItineraryMsg.preferences
        };
        setMessages([...messages, userMsg, aiConfirmMsg]);
        downloadItineraryPDF({ ...lastItineraryMsg, itineraryData: itinData });
        return;
      } else {
        setInputQuery("");
        const userMsg = { id: Date.now(), sender: "user", text: textToSend };
        const aiGuideMsg = {
          id: Date.now() + 1,
          sender: "ai",
          text: "I would be happy to generate your official PDF Itinerary! Please ask me to plan a trip first (for example: *'Plan a 3-day trip to Jaipur'*) and I will generate the complete day-by-day plan with an instant PDF download option."
        };
        setMessages([...messages, userMsg, aiGuideMsg]);
        return;
      }
    }

    // Append travel dates if selected via Calendar Range Picker
    if (selectedTravelDates && !queryText.includes(selectedTravelDates.rangeDisplay)) {
      queryText = queryText.trim() 
        ? `${queryText} (Travel Dates: ${selectedTravelDates.fullText})`
        : `I want to travel during ${selectedTravelDates.fullText}`;
    }

    const currentImageAttachment = attachedImage;
    const currentPdfAttachment = attachedPdf;

    setInputQuery("");
    setAttachedImage(null);
    setAttachedPdf(null);
    setIsTyping(true);

    try {
      // 1. Run Computer Vision Landmark Recognition & FAISS Visual Similarity if image is attached
      let landmarkContext = null;
      if (currentImageAttachment) {
        setIsRecognizingLandmark(true);
        try {
          let fileToSend = currentImageAttachment.file;
          if (!fileToSend && currentImageAttachment.url) {
            const blob = await fetch(currentImageAttachment.url).then((r) => r.blob());
            fileToSend = new File([blob], currentImageAttachment.name || "upload.jpg", {
              type: blob.type || "image/jpeg"
            });
          }

          if (fileToSend) {
            const formData = new FormData();
            formData.append("file", fileToSend);
            const recRes = await fetch("/api/landmark/recognize", {
              method: "POST",
              body: formData
            });
            if (recRes.ok) {
              landmarkContext = await recRes.json();
            }
          }
        } catch (recErr) {
          console.warn("Landmark recognition skipped:", recErr);
        } finally {
          setIsRecognizingLandmark(false);
        }
      }

      const userMsg = {
        id: Date.now(),
        sender: "user",
        text: queryText,
        image: currentImageAttachment,
        pdf: currentPdfAttachment,
        travelDates: selectedTravelDates,
        landmarkContext: landmarkContext
      };

      const newMessages = [...messages, userMsg];
      setMessages(newMessages);

      // 2. Build conversation payload for backend API
      const apiMessages = newMessages.map((m, idx) => {
        let content = m.text;
        if (idx === newMessages.length - 1 && landmarkContext) {
          if (landmarkContext.landmark_name) {
            content = `${m.text} [User attached a photo: The trained CV landmark model identified it as ${landmarkContext.landmark_name}, ${landmarkContext.location || ''}]`;
          } else if (landmarkContext.scene_context?.display_name) {
            content = `${m.text} [User attached a photo: Places365 scene recognition identified this as a ${landmarkContext.scene_context.display_name} (${landmarkContext.scene_context.travel_category}) scene. The user wants to know about this location / similar scenic destinations.]`;
          }
        }
        return {
          role: m.sender === "ai" ? "assistant" : "user",
          content: content
        };
      });

      // 3. Call backend FastAPI endpoint connected to Groq
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: apiMessages,
          landmark_context: landmarkContext
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      let aiResponseText = data.message || "Hello! I am Dora AI Assistant. How can I help plan your trip?";
      let itineraryDays = [];
      let weatherCard = null;
      let routeData = data.route_data || null;
      let quizData = (data.quiz && data.quiz.active && Array.isArray(data.quiz.questions) && data.quiz.questions.length > 0) ? data.quiz : null;
      let itineraryData = data.itinerary || null;

      const intent = data.intent || "general_question";
      const prefDest = data.preferences?.destination || "";

      // INTENT-DRIVEN tool usage -- only fetch/show tools when AI signals it
      // Route: only for explicit route_planning intent OR final road-trip itinerary with itineraryData
      if (
        !routeData &&
        (intent === "route_planning" || (intent === "plan_itinerary" && itineraryData && data.preferences?.transport?.toLowerCase().includes("car")))
      ) {
        const origin = data.preferences?.starting_point || data.preferences?.destination || "";
        const dest = data.preferences?.destination || "";
        if (origin && dest && origin !== dest) {
          try {
            const mRes = await fetch("/api/maps/route", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ origin, stops: [dest] })
            });
            if (mRes.ok) routeData = await mRes.json();
          } catch (mErr) {
            console.warn("Route fetch skipped:", mErr);
          }
        }
      }

      // Weather: only for weather_inquiry intent
      if (intent === "weather_inquiry" && prefDest) {
        try {
          const wRes = await fetch(`/api/weather?city=${encodeURIComponent(prefDest)}`);
          if (wRes.ok) weatherCard = await wRes.json();
        } catch (wErr) {
          console.warn("Weather fetch skipped:", wErr);
        }
      }

      // Extract day-by-day itinerary specs
      if (itineraryData && Array.isArray(itineraryData.days) && itineraryData.days.length > 0) {
        itineraryDays = itineraryData.days.map((d) => ({
          day: typeof d.day === "number" ? `Day ${d.day}` : (d.day || d.label || "Day"),
          title: d.title || d.destination || "Exploration",
          details: [d.morning, d.afternoon, d.evening].filter(Boolean).join(" • ") || d.summary || d.description || ""
        }));
      } else if (aiResponseText.includes("Day 1") || aiResponseText.includes("Day 1:")) {
        const dayRegex = /\*?\*?(Day\s+\d+)\*?\*?[:\s–—-]+([^\n]+)([\s\S]*?)(?=(?:\*?\*?Day\s+\d+\*?\*?|$))/gi;
        let match;
        while ((match = dayRegex.exec(aiResponseText)) !== null) {
          const dayLabel = match[1].trim();
          const dayTitle = match[2].trim().replace(/\*\*/g, "");
          const dayDetails = match[3].trim().replace(/\*\*/g, "").replace(/\n+/g, " ");
          if (dayTitle && !dayTitle.toLowerCase().includes("plan")) {
            itineraryDays.push({
              day: dayLabel,
              title: dayTitle,
              details: dayDetails.slice(0, 260)
            });
          }
        }
      }

      if (!itineraryData && (itineraryDays.length > 0 || /day\s*1\b/i.test(aiResponseText))) {
        itineraryData = ensureItineraryData({
          itineraryDays,
          text: aiResponseText,
          preferences: data.preferences
        }, activeTripContext);
      }

      const flightData = data.flight_data || null;
      const trainData = data.train_data || null;
      const hotelData = data.hotel_data || null;

      if (data.preferences) {
        setActiveTripContext((prev) => ({
          ...prev,
          destination: data.preferences.destination || prev.destination,
          origin: data.preferences.starting_point || prev.origin,
          budget: data.preferences.budget || prev.budget,
          dates: data.preferences.dates || prev.dates,
          duration_days: parseInt((data.preferences.duration || "").replace(/[^0-9]/g, "") || "3", 10)
        }));
      }

      const aiMsg = {
        id: Date.now() + 1,
        sender: "ai",
        text: aiResponseText,
        itineraryDays,
        weatherCard,
        routeData,
        quizData,
        itineraryData,
        flightData,
        trainData,
        hotelData,
        preferences: data.preferences || null
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.warn("Backend API offline or unreachable, using dynamic fallback response:", err);
      
      let fallbackText = `Hello! I am Dora AI Assistant. How can I help you plan your journey today?`;
      if (textToSend.toLowerCase().includes("hi") || textToSend.toLowerCase().includes("hello")) {
        fallbackText = "Greetings! I'm Dora AI Travel Assistant. What destination or heritage trip are you planning today?";
      }

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "ai",
          text: fallbackText,
          actionChips: [
            { label: "Plan 3-Day Trip", action: "plan_trip" },
            { label: "Find Nearby Stays", action: "find_hotels" }
          ]
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  // Multi-Select Option Toggle Handler
  const handleQuizOptionClick = (qId, optionText) => {
    setQuizSelections((prev) => {
      const currentList = prev[qId] || [];
      if (currentList.includes(optionText)) {
        return { ...prev, [qId]: currentList.filter((item) => item !== optionText) };
      } else {
        return { ...prev, [qId]: [...currentList, optionText] };
      }
    });
  };

  const submitQuizAnswers = () => {
    // Merge multi-select + free-text answers
    const allAnswers = {};
    Object.entries(quizSelections).forEach(([k, v]) => { allAnswers[k] = Array.isArray(v) ? v.join(" + ") : v; });
    Object.entries(quizFreeTexts).forEach(([k, v]) => {
      if (v && v.trim()) {
        if (allAnswers[k]) {
          allAnswers[k] = allAnswers[k].replace("Something else", `Something else (${v.trim()})`);
        } else {
          allAnswers[k] = v.trim();
        }
      }
    });

    const formattedAnswers = Object.entries(allAnswers)
      .map(([k, v]) => `${k}: ${v}`)
      .filter(str => !str.endsWith(": "))
      .join(", ");

    let fullSubmissionStr = formattedAnswers;

    if (selectedTravelDates) {
      fullSubmissionStr = fullSubmissionStr
        ? `${fullSubmissionStr}, Travel Dates: ${selectedTravelDates.fullText}`
        : `Travel Dates: ${selectedTravelDates.fullText}`;
    }

    handleSend(`My trip choices: ${fullSubmissionStr}`);
  };

  const handleFileUpload = (e, type) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (type === "image") {
      setAttachedImage({
        url: URL.createObjectURL(file),
        name: file.name,
        size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
        file: file
      });
    } else if (type === "pdf") {
      setAttachedPdf({
        name: file.name,
        size: `${(file.size / 1024).toFixed(1)} KB`,
        file: file
      });
    }
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const hasMessages = messages.length > 0;
  const hasAnyQuizSelection =
    Object.values(quizSelections).some((arr) => Array.isArray(arr) && arr.length > 0) ||
    Object.values(quizFreeTexts).some((v) => v && v.trim().length > 0) ||
    Boolean(selectedTravelDates);

  return (
    <div className="flex-1 flex flex-col h-screen w-full relative font-sans overflow-hidden transition-all duration-300">
      {/* Interactive Travel Date Range Calendar Modal */}
      <TravelCalendarModal
        isOpen={isCalendarOpen}
        onClose={() => setIsCalendarOpen(false)}
        onSelectDateRange={(dates) => setSelectedTravelDates(dates)}
      />

      {/* Booking Review & Budget Modal */}
      <BookingReviewModal
        isOpen={isReviewModalOpen}
        onClose={() => setIsReviewModalOpen(false)}
        selectedHotel={selectedHotel}
        selectedFlight={selectedFlight}
        selectedTrain={selectedTrain}
        tripContext={activeTripContext}
        onConfirmSelection={() => {
          let summaryDetails = [];
          if (selectedHotel) summaryDetails.push(`Stay: ${selectedHotel.hotel_name} (₹${selectedHotel.price_inr}/night on ${selectedHotel.best_vendor})`);
          if (selectedFlight) summaryDetails.push(`Flight: ${selectedFlight.airline} ${selectedFlight.flight_number} (₹${selectedFlight.price})`);
          if (selectedTrain) summaryDetails.push(`Train: ${selectedTrain.train_name} #${selectedTrain.train_number} (₹${selectedTrain.fare_inr})`);
          handleSend(`Please update my trip itinerary with my selected bookings: ${summaryDetails.join(", ")}`);
        }}
      />

      {/* Top Header Overlay Controls */}
      <div className="absolute top-4 left-4 right-4 z-40 flex items-center justify-between pointer-events-none px-2 sm:px-6">
        {!isSidebarOpen ? (
          <button
            onClick={onOpenSidebar}
            title="Open sidebar"
            className="pointer-events-auto p-2 rounded-[6px] bg-white dark:bg-[#111111] border border-[#ebebeb] dark:border-[#222222] shadow-md text-[#171717] dark:text-white hover:bg-gray-100 dark:hover:bg-zinc-800 transition-all flex items-center justify-center"
          >
            <PanelLeftOpen className="w-4.5 h-4.5 text-[#0066cc] dark:text-[#2997ff]" />
          </button>
        ) : (
          <div></div>
        )}

        {/* Center: Trip Review & Cart Quick Access Badge */}
        <button
          onClick={() => setIsReviewModalOpen(true)}
          className="pointer-events-auto px-3.5 py-1.5 rounded-full bg-white dark:bg-[#111111] border border-[#ebebeb] dark:border-[#222222] shadow-md hover:border-emerald-500/50 transition-all flex items-center space-x-2 text-xs font-semibold cursor-pointer group"
          title="Review Trip Selection, Budget & Bookings"
        >
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <ShoppingBag className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform" />
          <span className="text-[#171717] dark:text-white">Trip Review</span>
          {(selectedHotel || selectedFlight || selectedTrain) && (
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-600 text-white font-mono font-bold">
              {[selectedHotel ? 1 : 0, selectedFlight ? 1 : 0, selectedTrain ? 1 : 0].reduce((a, b) => a + b, 0)}
            </span>
          )}
        </button>

        <button
          onClick={toggleTheme}
          title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
          className="pointer-events-auto p-2 rounded-[6px] bg-white dark:bg-[#111111] border border-[#ebebeb] dark:border-[#222222] shadow-md text-[#171717] dark:text-white hover:bg-gray-100 dark:hover:bg-zinc-800 transition-all flex items-center space-x-2 text-xs font-medium"
        >
          {theme === "dark" ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-blue-600" />
          )}
          <span className="hidden sm:inline">{theme === "dark" ? "Light" : "Dark"}</span>
        </button>
      </div>

      {/* Unified Chat Workspace: Scrollable Content Stream + Persistent Bottom Input Dock */}
      <div className="flex-1 flex flex-col items-center w-full h-full overflow-hidden">
        {/* Scrollable Stream Container */}
        <div className="flex-1 overflow-y-auto pt-16 pb-6 space-y-6 w-full px-4 sm:px-8 lg:px-16 xl:px-24 flex flex-col">
          {!hasMessages ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center px-4 max-w-2xl mx-auto my-auto py-12">
              <div className="w-16 h-16 rounded-2xl p-1 bg-white dark:bg-[#1f1f23] shadow-lg border border-pink-200 dark:border-pink-900/40 mb-4 flex items-center justify-center overflow-hidden">
                <img src="/dora-ai-logo.png" alt="Dora AI" className="w-full h-full object-contain rounded-xl" />
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#171717] dark:text-white">
                Where would you like to travel?
              </h2>
              <p className="text-sm text-[#8f8f8f] mt-2 max-w-md">
                Plan road trips, explore cultural landmarks, or craft custom itineraries across India with Dora AI.
              </p>

              {/* Quick Starter Suggestions */}
              <div className="flex flex-wrap items-center justify-center gap-2 mt-6">
                {[
                  "Road trip from Delhi to Goa for 7 days",
                  "4-day Golden Triangle heritage itinerary",
                  "Spiritual trip to Uttarakhand with parents",
                  "Best places to visit in Jaipur"
                ].map((promptText) => (
                  <button
                    key={promptText}
                    type="button"
                    onClick={() => handleSend(promptText)}
                    className="px-3.5 py-1.5 rounded-full text-xs bg-[#f4f4f5] dark:bg-[#1f1f23] hover:bg-[#e4e4e7] dark:hover:bg-[#27272a] text-[#4d4d4d] dark:text-[#d4d4d8] border border-[#e4e4e7] dark:border-[#27272a] transition-all cursor-pointer"
                  >
                    {promptText}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  ref={msg.sender === "ai" ? (el) => (aiMsgRefs.current[msg.id] = el) : null}
                  className={`flex items-start space-x-4 w-full scroll-mt-20 ${msg.sender === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
                >
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 overflow-hidden ${
                    msg.sender === "ai"
                      ? "bg-white p-0.5 border border-pink-300 dark:border-pink-800 shadow-sm"
                      : "bg-gradient-to-tr from-[#18181b] to-[#3f3f46] dark:from-zinc-200 dark:to-white text-white dark:text-zinc-900 shadow-sm border border-black/10 dark:border-white/20"
                  }`}
                >
                  {msg.sender === "ai" ? (
                    <img src="/dora-avatar.png" alt="Dora AI" className="w-full h-full object-contain rounded-full" />
                  ) : (
                    <User className="w-4.5 h-4.5" />
                  )}
                </div>

                {/* Bubble */}
                <div className={`w-full max-w-full ${msg.sender === "user" ? "flex justify-end" : "sm:max-w-[88%] lg:max-w-[82%] xl:max-w-[78%]"}`}>
                  <div
                    className={`${
                      msg.sender === "user"
                        ? "max-w-full sm:max-w-[82%] md:max-w-[75%] px-5 py-3.5 rounded-[18px] rounded-tr-[4px] bg-[#18181b] dark:bg-white text-white dark:text-[#09090b] shadow-md border border-black/10 dark:border-zinc-200 text-left font-normal sm:font-medium tracking-normal"
                        : "w-full p-4 sm:p-5 vercel-card text-[#171717] dark:text-[#ffffff] rounded-[14px] rounded-tl-none"
                    }`}
                  >
                    {msg.landmarkContext?.landmark_name ? (
                      <div className="flex items-center space-x-2 text-[11px] font-mono opacity-90 mb-2.5">
                        <span className="px-2.5 py-0.5 rounded-full bg-white/20 dark:bg-black/20 font-semibold">
                          📍 {msg.landmarkContext.landmark_name}
                          {msg.landmarkContext.location ? ` • ${msg.landmarkContext.location}` : ""}
                        </span>
                      </div>
                    ) : msg.landmarkContext?.scene_context?.display_name ? (
                      <div className="flex items-center space-x-2 text-[11px] font-mono opacity-90 mb-2.5">
                        <span className="px-2.5 py-0.5 rounded-full bg-white/20 dark:bg-black/20 font-semibold">
                          🌄 {msg.landmarkContext.scene_context.display_name} • {msg.landmarkContext.scene_context.travel_category}
                        </span>
                      </div>
                    ) : null}

                    {msg.image && (
                      <img src={msg.image.url} alt="Attachment" className="w-72 h-44 object-cover rounded-[10px] mb-3 border border-black/10 dark:border-white/10" />
                    )}

                    {msg.pdf && (
                      <div className="flex items-center space-x-3 bg-white/10 dark:bg-black/10 p-3 rounded-[8px] mb-3 text-xs font-mono">
                        <FileText className="w-4 h-4 text-red-400" />
                        <div className="text-left">
                          <p className="font-medium">{msg.pdf.name}</p>
                          <p className="text-[10px] opacity-70">{msg.pdf.size}</p>
                        </div>
                      </div>
                    )}

                    <MarkdownRenderer content={msg.text} isUser={msg.sender === "user"} />
                  </div>

                  {/* Premium Structured Itinerary Card */}
                  {(msg.itineraryData || (msg.itineraryDays && msg.itineraryDays.length > 0)) && (
                    <div>
                      {msg.itineraryData && (
                        <ItineraryCard
                          itinerary={msg.itineraryData}
                          routeData={msg.routeData}
                          selectedHotel={selectedHotel}
                          selectedFlight={selectedFlight}
                          selectedTrain={selectedTrain}
                        />
                      )}
                      {/* Action buttons — placed right below the itinerary card */}
                      <div className="mt-3 flex items-center justify-end space-x-2">
                        <button
                          id={`save-trip-${msg.id}`}
                          onClick={() => saveTripToBackend(msg)}
                          disabled={savingTrip[msg.id]}
                          className={`flex items-center space-x-2 px-4 py-2.5 rounded-[10px] text-sm font-semibold transition-all duration-200 active:scale-95 shadow-sm ${
                            savedTripSuccess[msg.id]
                              ? "bg-emerald-600 text-white"
                              : "bg-white dark:bg-[#18181b] border border-[#ebebeb] dark:border-[#27272a] hover:border-emerald-500 text-[#171717] dark:text-white"
                          }`}
                        >
                          {savedTripSuccess[msg.id] ? (
                            <>
                              <CheckCircle2 className="w-4 h-4 text-white" />
                              <span>Trip Saved!</span>
                            </>
                          ) : (
                            <>
                              <Bookmark className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                              <span>{savingTrip[msg.id] ? "Saving…" : "Save Trip"}</span>
                            </>
                          )}
                        </button>

                        <button
                          id={`download-pdf-${msg.id}`}
                          onClick={() => downloadItineraryPDF(msg)}
                          disabled={pdfDownloading[msg.id]}
                          className="flex items-center space-x-2 px-4 py-2.5 rounded-[10px] bg-[#0070f3] hover:bg-[#0051b3] disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold shadow-md shadow-[#0070f3]/20 transition-all duration-200 active:scale-95"
                        >
                          <Download className="w-4 h-4" />
                          <span>{pdfDownloading[msg.id] ? "Generating PDF…" : "Download PDF"}</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Interactive Dora AI Customization Quiz Widget -- only shown when explicitly active */}
                  {msg.quizData && msg.quizData.active && Array.isArray(msg.quizData.questions) && msg.quizData.questions.length > 0 && (
                    <div className="mt-4 vercel-card p-5 text-left w-full bg-gradient-to-r from-pink-50/70 to-purple-50/50 dark:from-[#0f172a] dark:to-[#1e1b4b] border-pink-200 dark:border-pink-900/40 rounded-[14px]">
                      <div className="flex items-center justify-between pb-3 border-b border-pink-200/50 dark:border-pink-900/40 mb-4">
                        <div className="flex items-center space-x-2">
                          <HelpCircle className="w-5 h-5 text-[#e91e63]" />
                          <h4 className="font-semibold text-base text-[#171717] dark:text-white">
                            Dora AI Personalization Quiz — Select Preferences
                          </h4>
                        </div>
                        <span className="text-[11px] font-mono font-medium px-2.5 py-0.5 rounded-[4px] bg-pink-100 dark:bg-pink-900/60 text-[#e91e63] dark:text-pink-200">
                          Multi-Select Enabled
                        </span>
                      </div>

                      <div className="space-y-4">

                        {/* Quiz Questions List — supports free_text, multi-select, and Something else */}
                        {msg.quizData.questions.map((q) => {
                          const isFreeText = q.free_text === true || (q.options && q.options.length === 0);
                          const hasSomethingElse = !isFreeText && q.options && q.options.includes("Something else");
                          const somethingElseSelected = Array.isArray(quizSelections[q.id]) && quizSelections[q.id].includes("Something else");
                          return (
                            <div key={q.id} className="p-3.5 bg-white/90 dark:bg-[#111111]/90 rounded-[10px] border border-blue-100 dark:border-indigo-900/30">
                              <div className="flex items-center justify-between mb-2.5">
                                <p className="font-semibold text-sm text-[#171717] dark:text-white">{q.question}</p>
                                {!isFreeText && <span className="text-[10px] text-[#8f8f8f] font-mono">Select one or more</span>}
                              </div>

                              {/* FREE TEXT QUESTION (starting_point, budget, etc.) */}
                              {isFreeText ? (
                                <div className="flex items-center space-x-2">
                                  <Edit3 className="w-4 h-4 text-[#0070f3] shrink-0" />
                                  <input
                                    type="text"
                                    value={quizFreeTexts[q.id] || ""}
                                    onChange={(e) => setQuizFreeTexts(prev => ({ ...prev, [q.id]: e.target.value }))}
                                    placeholder={q.placeholder || (q.id === "starting_point" ? "e.g. Delhi, Mumbai, Bengaluru..." : "Type your answer...")}
                                    className="flex-1 bg-[#fafafa] dark:bg-[#1c1c1c] border border-[#ebebeb] dark:border-[#333333] rounded-[8px] px-3 py-2 text-sm text-[#171717] dark:text-white placeholder:text-[#8f8f8f] focus:outline-none focus:border-[#0070f3] transition-colors"
                                  />
                                </div>
                              ) : (
                                /* MULTI-SELECT OPTIONS */
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                                  {q.options.map((opt, oIdx) => {
                                    const isSelected = Array.isArray(quizSelections[q.id]) && quizSelections[q.id].includes(opt);
                                    return (
                                      <button
                                        key={opt}
                                        onClick={() => handleQuizOptionClick(q.id, opt)}
                                        className={`p-2.5 rounded-[8px] text-xs font-medium border text-left flex items-center justify-between transition-all ${
                                          isSelected
                                            ? "bg-[#0070f3] text-white border-[#0070f3] shadow-sm font-semibold"
                                            : "bg-[#fafafa] dark:bg-[#1c1c1c] text-[#171717] dark:text-white border-[#ebebeb] dark:border-[#333333] hover:border-[#0070f3]"
                                        }`}
                                      >
                                        <span className="truncate">{oIdx + 1}. {opt}</span>
                                        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 shrink-0 ml-1" />}
                                      </button>
                                    );
                                  })}
                                </div>
                              )}

                              {/* "Something else" triggers a free-text box */}
                              {hasSomethingElse && somethingElseSelected && (
                                <div className="mt-2 flex items-center space-x-2">
                                  <Edit3 className="w-4 h-4 text-[#0070f3] shrink-0" />
                                  <input
                                    type="text"
                                    value={quizFreeTexts[`${q.id}_else`] || ""}
                                    onChange={(e) => setQuizFreeTexts(prev => ({ ...prev, [`${q.id}_else`]: e.target.value }))}
                                    placeholder="Tell us more..."
                                    className="flex-1 bg-[#fafafa] dark:bg-[#1c1c1c] border border-[#0070f3]/60 rounded-[8px] px-3 py-2 text-sm text-[#171717] dark:text-white placeholder:text-[#8f8f8f] focus:outline-none focus:border-[#0070f3] transition-colors"
                                  />
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>

                      <button
                        onClick={submitQuizAnswers}
                        disabled={!hasAnyQuizSelection}
                        className="mt-4 w-full sm:w-auto vercel-btn-pill !py-2.5 !px-6 text-sm flex items-center justify-center space-x-2 disabled:opacity-40"
                      >
                        <Sparkles className="w-4 h-4 text-amber-300" />
                        <span>Generate My Custom Itinerary</span>
                      </button>
                    </div>
                  )}

                  {/* Leaflet & OSRM Interactive Route Map Widget */}
                  {msg.routeData && (
                    <RouteMapWidget routeData={msg.routeData} />
                  )}

                  {/* Interactive Flight Booking & Price Comparison Widget */}
                  {msg.flightData && (
                    <FlightBookingWidget
                      flightData={msg.flightData}
                      onSelectFlight={(fl) => setSelectedFlight(fl)}
                      selectedFlight={selectedFlight}
                    />
                  )}

                  {/* Interactive Train Booking & Schedules Widget */}
                  {msg.trainData && (
                    <TrainBookingWidget
                      trainData={msg.trainData}
                      onSelectTrain={(tr) => setSelectedTrain(tr)}
                      selectedTrain={selectedTrain}
                    />
                  )}

                  {/* Interactive Hotel Booking & Multi-Vendor Comparison Widget */}
                  {msg.hotelData && (
                    <HotelBookingWidget
                      hotelData={msg.hotelData}
                      onSelectHotel={(ht) => setSelectedHotel(ht)}
                      selectedHotel={selectedHotel}
                    />
                  )}

                  {/* Live Open-Meteo Weather Card Widget */}
                  {msg.weatherCard && (
                    <div className="mt-3.5 vercel-card p-4 text-left w-full bg-gradient-to-r from-blue-50/80 to-indigo-50/50 dark:from-[#0d1b2a]/80 dark:to-[#1b263b]/50 border-blue-200 dark:border-blue-900/40">
                      <div className="flex items-center justify-between pb-2 border-b border-blue-200/60 dark:border-blue-900/40 mb-3">
                        <div className="flex items-center space-x-2">
                          <CloudSun className="w-5 h-5 text-amber-500" />
                          <span className="font-semibold text-sm text-[#171717] dark:text-white">
                            Live Weather Report — {msg.weatherCard.city}, {msg.weatherCard.country}
                          </span>
                        </div>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-[4px] bg-blue-100 dark:bg-blue-900/60 text-blue-800 dark:text-blue-200">
                          {msg.weatherCard.cached ? "Cached" : "Live API"}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                        <div className="p-2.5 rounded-[8px] bg-white/80 dark:bg-[#111111]/80 border border-blue-100 dark:border-blue-900/30">
                          <p className="text-[#8f8f8f] font-mono text-[10px]">Temperature</p>
                          <p className="font-bold text-base text-[#171717] dark:text-white mt-0.5">
                            {msg.weatherCard.current_temperature_c}°C
                          </p>
                          <p className="text-[10px] text-[#8f8f8f] mt-0.5">
                            H: {msg.weatherCard.today_max_temp_c}°C | L: {msg.weatherCard.today_min_temp_c}°C
                          </p>
                        </div>

                        <div className="p-2.5 rounded-[8px] bg-white/80 dark:bg-[#111111]/80 border border-blue-100 dark:border-blue-900/30">
                          <p className="text-[#8f8f8f] font-mono text-[10px]">Condition</p>
                          <p className="font-medium text-sm text-[#171717] dark:text-white mt-1 truncate">
                            {msg.weatherCard.weather_condition}
                          </p>
                        </div>

                        <div className="p-2.5 rounded-[8px] bg-white/80 dark:bg-[#111111]/80 border border-blue-100 dark:border-blue-900/30">
                          <p className="text-[#8f8f8f] font-mono text-[10px]">Wind Speed</p>
                          <div className="flex items-center space-x-1 mt-1">
                            <Wind className="w-3.5 h-3.5 text-blue-500" />
                            <span className="font-medium text-sm text-[#171717] dark:text-white">
                              {msg.weatherCard.windspeed_kmh} km/h
                            </span>
                          </div>
                        </div>

                        <div className="p-2.5 rounded-[8px] bg-white/80 dark:bg-[#111111]/80 border border-blue-100 dark:border-blue-900/30">
                          <p className="text-[#8f8f8f] font-mono text-[10px]">Precipitation</p>
                          <div className="flex items-center space-x-1 mt-1">
                            <Droplets className="w-3.5 h-3.5 text-blue-500" />
                            <span className="font-medium text-sm text-[#171717] dark:text-white">
                              {msg.weatherCard.precipitation_sum_mm} mm
                            </span>
                          </div>
                        </div>
                      </div>

                      <p className="text-[10px] font-mono text-[#8f8f8f] mt-2.5 pt-2 border-t border-blue-200/40 dark:border-blue-900/30">
                        {msg.weatherCard.attribution}
                      </p>
                    </div>
                  )}

                  {/* Day-by-Day Timeline Itinerary */}
                  {msg.itineraryDays && msg.itineraryDays.length > 0 && (
                    <div className="mt-3.5 vercel-card p-5 text-left w-full">
                      <div className="flex items-center justify-between pb-3 border-b border-[#ebebeb] dark:border-[#222222] mb-3">
                        <span className="font-mono-eyebrow text-[#171717] dark:text-white">
                          Extracted Itinerary Specs
                        </span>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => copyToClipboard(msg.itineraryDays.map(d => `${d.day}: ${d.title}`).join("\n"), msg.id)}
                            className="vercel-btn-control flex items-center space-x-1 !py-1 !px-2.5 text-xs"
                          >
                            {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-[#8f8f8f]" />}
                            <span>{copiedId === msg.id ? "Copied" : "Copy"}</span>
                          </button>
                          <button
                            id={`download-pdf-inline-${msg.id}`}
                            onClick={() => downloadItineraryPDF(msg)}
                            disabled={pdfDownloading[msg.id]}
                            className="vercel-btn-pill flex items-center space-x-1 !py-1 !px-3 text-xs disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Download className="w-3.5 h-3.5" />
                            <span>{pdfDownloading[msg.id] ? "…" : "PDF"}</span>
                          </button>
                        </div>
                      </div>

                      <div className="space-y-3">
                        {msg.itineraryDays.map((item) => (
                          <div key={item.day} className="p-4 bg-[#fafafa] dark:bg-[#171717] rounded-[10px] border border-[#ebebeb] dark:border-[#222222]">
                            <span className="font-mono text-xs font-medium px-2.5 py-0.5 rounded-[4px] bg-[#ebebeb] dark:bg-[#222222] text-[#171717] dark:text-white">
                              {item.day}
                            </span>
                            <h5 className="font-semibold text-sm text-[#171717] dark:text-white mt-1.5">{item.title}</h5>
                            <p className="text-xs sm:text-sm text-[#4d4d4d] dark:text-[#a1a1a1] mt-1 leading-relaxed">{item.details}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}


                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-white p-0.5 border border-pink-300 dark:border-pink-800 shadow-sm flex items-center justify-center shrink-0 overflow-hidden">
                  <img src="/dora-avatar.png" alt="Dora AI" className="w-full h-full object-contain rounded-full animate-pulse" />
                </div>
                <div className="vercel-card p-3.5 text-xs text-[#8f8f8f] font-mono flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#e91e63] animate-ping"></div>
                  <span>
                    {isRecognizingLandmark
                      ? "Identifying landmark with Dora Vision..."
                      : "Dora AI is generating your response..."}
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

          {/* Widescreen Bottom Input Dock Bar */}
          <div className="w-full max-w-5xl lg:max-w-6xl xl:max-w-7xl px-4 sm:px-8 pb-4 sm:pb-6 mx-auto shrink-0 z-30">
            <div className="bg-white/95 dark:bg-[#111111]/95 backdrop-blur-md rounded-[14px] p-3 sm:p-3.5 border border-[#ebebeb] dark:border-[#222222] shadow-2xl">
              {(attachedImage || attachedPdf || selectedTravelDates) && (
                <div className="mb-2 px-2 flex flex-wrap items-center gap-2">
                  {selectedTravelDates && (
                    <div className="flex items-center space-x-2 bg-amber-50 dark:bg-amber-950/40 p-1.5 px-3 rounded-[6px] border border-amber-200 dark:border-amber-900/50 text-xs font-mono text-amber-800 dark:text-amber-200">
                      <CalendarIcon className="w-3.5 h-3.5 text-amber-500" />
                      <span>📅 {selectedTravelDates.fullText}</span>
                      <button onClick={() => setSelectedTravelDates(null)} className="text-red-500 font-bold ml-1">✕</button>
                    </div>
                  )}
                  {attachedImage && (
                    <div className="flex items-center space-x-2 bg-[#fafafa] dark:bg-[#1c1c1c] p-1.5 px-3 rounded-[6px] border border-[#ebebeb] dark:border-[#333333] text-xs font-mono">
                      <ImageIcon className="w-3.5 h-3.5 text-[#0070f3]" />
                      <span className="truncate max-w-xs">{attachedImage.name}</span>
                      <button onClick={() => setAttachedImage(null)} className="text-red-500 font-bold ml-1">✕</button>
                    </div>
                  )}
                  {attachedPdf && (
                    <div className="flex items-center space-x-2 bg-[#fafafa] dark:bg-[#1c1c1c] p-1.5 px-3 rounded-[6px] border border-[#ebebeb] dark:border-[#333333] text-xs font-mono">
                      <FileText className="w-4 h-4 text-red-500" />
                      <span className="truncate max-w-xs">{attachedPdf.name}</span>
                      <button onClick={() => setAttachedPdf(null)} className="text-red-500 font-bold ml-1">✕</button>
                    </div>
                  )}
                </div>
              )}

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex items-center space-x-3"
              >
                {/* Calendar Range Picker Trigger */}
                <button
                  type="button"
                  onClick={() => setIsCalendarOpen(true)}
                  title="Select Travel Dates Calendar"
                  className="p-2 rounded-[6px] hover:bg-[#f2f2f2] dark:hover:bg-[#1c1c1c] text-amber-500 hover:text-amber-600 transition-colors"
                >
                  <CalendarIcon className="w-5 h-5" />
                </button>

                <label title="Attach Photo" className="p-2 rounded-[6px] hover:bg-[#f2f2f2] dark:hover:bg-[#1c1c1c] text-[#8f8f8f] hover:text-[#171717] dark:hover:text-white cursor-pointer transition-colors">
                  <ImageIcon className="w-5 h-5 text-[#0070f3]" />
                  <input type="file" accept="image/*" onChange={(e) => handleFileUpload(e, "image")} className="hidden" />
                </label>

                <label title="Attach PDF Document" className="p-2 rounded-[6px] hover:bg-[#f2f2f2] dark:hover:bg-[#1c1c1c] text-[#8f8f8f] hover:text-[#171717] dark:hover:text-white cursor-pointer transition-colors">
                  <FileText className="w-5 h-5 text-red-500" />
                  <input type="file" accept=".pdf,.doc,.docx" onChange={(e) => handleFileUpload(e, "pdf")} className="hidden" />
                </label>

                <input
                  type="text"
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  placeholder="Ask anything or plan a trip..."
                  className="flex-1 bg-transparent text-base px-2 py-1.5 text-[#171717] dark:text-white placeholder-[#8f8f8f] focus:outline-none"
                />

                <button
                  type="submit"
                  disabled={!inputQuery.trim() && !attachedImage && !attachedPdf && !selectedTravelDates}
                  className="vercel-btn-pill !p-2.5 !rounded-[6px] disabled:opacity-30 flex items-center justify-center shrink-0"
                >
                  <CornerDownLeft className="w-4.5 h-4.5" />
                </button>
              </form>
            </div>
          </div>
        </div>
    </div>
  );
}
