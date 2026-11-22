import React, { useState, useEffect } from "react";
import {
  BookOpen, Clock, User, ArrowUpRight, Plus, Edit3, Trash2,
  Calendar, MapPin, Sparkles, Image as ImageIcon, Check, X, Bookmark,
  ChevronRight, ArrowLeft, Tag, FileText, Share2, Compass
} from "lucide-react";
import { TRAVEL_ARTICLES } from "../data/travelProductData";

export default function TravelJournal({ initialTripToConvert, onClearInitialTrip }) {
  const [personalPosts, setPersonalPosts] = useState([]);
  const [savedTrips, setSavedTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSubTab, setActiveSubTab] = useState("my_journal"); // my_journal, editorial
  
  // Modal / Form states
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingPostId, setEditingPostId] = useState(null);
  const [viewingPost, setViewingPost] = useState(null);

  // Form Fields
  const [title, setTitle] = useState("");
  const [destination, setDestination] = useState("");
  const [date, setDate] = useState("");
  const [content, setContent] = useState("");
  const [photoUrl, setPhotoUrl] = useState("");
  const [selectedTripId, setSelectedTripId] = useState("");
  const [author, setAuthor] = useState("Me");
  const [tags, setTags] = useState("");

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/journal/posts");
      if (res.ok) {
        const data = await res.json();
        setPersonalPosts(data.posts || []);
      }
    } catch (err) {
      console.warn("Could not fetch journal posts:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSavedTrips = async () => {
    try {
      const res = await fetch("/api/trips");
      if (res.ok) {
        const data = await res.json();
        setSavedTrips(data.trips || []);
      }
    } catch (err) {
      console.warn("Could not fetch saved trips:", err);
    }
  };

  useEffect(() => {
    fetchPosts();
    fetchSavedTrips();
  }, []);

  // Handle initial trip conversion if triggered from Saved Trips
  useEffect(() => {
    if (initialTripToConvert) {
      handleConvertTrip(initialTripToConvert.id);
      if (typeof onClearInitialTrip === "function") {
        onClearInitialTrip();
      }
    }
  }, [initialTripToConvert]);

  const openCreateModal = () => {
    setEditingPostId(null);
    setTitle("");
    setDestination("");
    setDate(new Date().toLocaleDateString("en-IN", { month: "long", day: "numeric", year: "numeric" }));
    setContent("");
    setPhotoUrl("");
    setSelectedTripId("");
    setTags("");
    setAuthor("Me");
    setIsEditorOpen(true);
  };

  const openEditModal = (post, e) => {
    if (e) e.stopPropagation();
    setEditingPostId(post.id);
    setTitle(post.title || "");
    setDestination(post.destination || "");
    setDate(post.date || "");
    setContent(post.content || "");
    setPhotoUrl(post.cover_image || (post.photos && post.photos[0]) || "");
    setSelectedTripId(post.trip_id || "");
    setTags(Array.isArray(post.tags) ? post.tags.join(", ") : "");
    setAuthor(post.author || "Me");
    setIsEditorOpen(true);
  };

  const handleSavePost = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const payload = {
      title: title.trim(),
      destination: destination.trim(),
      trip_id: selectedTripId || null,
      trip_title: savedTrips.find(t => t.id === selectedTripId)?.title || null,
      date: date.trim() || new Date().toLocaleDateString("en-IN"),
      content: content.trim(),
      cover_image: photoUrl.trim() || null,
      photos: photoUrl.trim() ? [photoUrl.trim()] : [],
      tags: tags ? tags.split(",").map(t => t.trim()).filter(Boolean) : [],
      author: author.trim() || "Me",
      read_time: `${Math.max(1, Math.ceil((content.split(" ").length || 100) / 180))} min read`
    };

    try {
      if (editingPostId) {
        const res = await fetch(`/api/journal/posts/${editingPostId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const data = await res.json();
          setPersonalPosts(prev => prev.map(p => p.id === editingPostId ? data.post : p));
        }
      } else {
        const res = await fetch("/api/journal/posts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const data = await res.json();
          setPersonalPosts(prev => [data.post, ...prev]);
        }
      }
      setIsEditorOpen(false);
    } catch (err) {
      console.error("Failed to save journal post:", err);
      alert("Failed to save journal story. Please try again.");
    }
  };

  const handleDeletePost = async (postId, e) => {
    if (e) e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this journal post?")) return;

    try {
      const res = await fetch(`/api/journal/posts/${postId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        setPersonalPosts(prev => prev.filter(p => p.id !== postId));
        if (viewingPost && viewingPost.id === postId) {
          setViewingPost(null);
        }
      }
    } catch (err) {
      console.error("Failed to delete journal post:", err);
    }
  };

  const handleConvertTrip = async (tripId) => {
    try {
      const res = await fetch(`/api/journal/from-trip/${tripId}`, {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        setPersonalPosts(prev => [data.post, ...prev]);
        setActiveSubTab("my_journal");
        openEditModal(data.post);
      }
    } catch (err) {
      console.error("Failed to convert trip to journal:", err);
    }
  };

  return (
    <div className="w-full space-y-6 text-left">
      {/* Header & Sub-tab controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#ebebeb] dark:border-[#222222]">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#0066cc] dark:text-[#2997ff] flex items-center">
              <BookOpen className="w-3.5 h-3.5 mr-1" />
              Travel Journal & Blog
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 font-bold">
              {personalPosts.length} Stories
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#171717] dark:text-white tracking-tight mt-1">
            Personal Memories & Heritage Guides
          </h2>
          <p className="text-xs text-[#71717a] dark:text-[#a1a1aa] mt-1">
            Document your journeys, convert saved trips into stories, or read curated destination guides.
          </p>
        </div>

        <div className="flex items-center space-x-2 self-start sm:self-auto">
          {/* Subtabs */}
          <div className="flex items-center p-0.5 rounded-[8px] bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/10 text-xs">
            <button
              onClick={() => setActiveSubTab("my_journal")}
              className={`px-3 py-1.5 rounded-[6px] font-medium transition-all ${
                activeSubTab === "my_journal"
                  ? "bg-white dark:bg-[#1f1f23] text-[#171717] dark:text-white shadow-xs font-semibold"
                  : "text-[#71717a] dark:text-[#a1a1aa] hover:text-[#171717]"
              }`}
            >
              My Journal ({personalPosts.length})
            </button>
            <button
              onClick={() => setActiveSubTab("editorial")}
              className={`px-3 py-1.5 rounded-[6px] font-medium transition-all ${
                activeSubTab === "editorial"
                  ? "bg-white dark:bg-[#1f1f23] text-[#171717] dark:text-white shadow-xs font-semibold"
                  : "text-[#71717a] dark:text-[#a1a1aa] hover:text-[#171717]"
              }`}
            >
              Editorial Guides ({TRAVEL_ARTICLES.length})
            </button>
          </div>

          <button
            onClick={openCreateModal}
            className="px-3.5 py-1.5 rounded-[8px] bg-[#0066cc] hover:bg-[#0055b3] text-white text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Write Story</span>
          </button>
        </div>
      </div>

      {/* SUBTAB 1: PERSONAL TRAVEL JOURNAL */}
      {activeSubTab === "my_journal" && (
        <div>
          {/* Quick Convert from Saved Trips bar if user has saved trips */}
          {savedTrips.length > 0 && (
            <div className="p-3.5 mb-6 rounded-[12px] bg-gradient-to-r from-blue-50/70 via-indigo-50/40 to-purple-50/50 dark:from-[#0f172a] dark:via-[#1e1b4b]/40 dark:to-[#17171a] border border-blue-200/60 dark:border-blue-900/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="flex items-center space-x-2.5">
                <div className="w-7 h-7 rounded-md bg-[#0066cc]/10 dark:bg-[#2997ff]/20 text-[#0066cc] dark:text-[#2997ff] flex items-center justify-center font-bold">
                  <Bookmark className="w-4 h-4" />
                </div>
                <div>
                  <span className="font-bold text-[#171717] dark:text-white">Convert a Saved Trip to Journal Story</span>
                  <p className="text-[11px] text-[#71717a] dark:text-[#a1a1aa]">Auto-generate a memory draft with full days and highlights.</p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <select
                  value=""
                  onChange={(e) => {
                    if (e.target.value) handleConvertTrip(e.target.value);
                  }}
                  className="bg-white dark:bg-[#18181b] border border-[#ebebeb] dark:border-[#27272a] rounded-[6px] px-2.5 py-1.5 text-xs text-[#171717] dark:text-white font-medium focus:outline-none"
                >
                  <option value="">Select a Saved Trip...</option>
                  {savedTrips.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.title} ({t.destination})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {loading ? (
            <div className="py-12 text-center text-xs text-[#8f8f8f]">
              <Sparkles className="w-6 h-6 mx-auto mb-2 text-[#0066cc] animate-spin" />
              Loading your journal stories...
            </div>
          ) : personalPosts.length === 0 ? (
            <div className="py-16 text-center max-w-md mx-auto p-6 rounded-[16px] border border-dashed border-[#ebebeb] dark:border-[#27272a] bg-black/2 dark:bg-white/2">
              <div className="w-12 h-12 rounded-full bg-[#0066cc]/10 dark:bg-[#2997ff]/20 text-[#0066cc] dark:text-[#2997ff] flex items-center justify-center mx-auto mb-3">
                <BookOpen className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-base text-[#171717] dark:text-white">
                Your travel journal is empty
              </h3>
              <p className="text-xs text-[#71717a] dark:text-[#a1a1aa] mt-1.5 leading-relaxed">
                Write personal memories, photo essays, and cultural notes from your trips across India.
              </p>
              <button
                onClick={openCreateModal}
                className="mt-4 px-4 py-2 rounded-[8px] bg-[#0066cc] text-white text-xs font-semibold hover:bg-[#0055b3] transition-all inline-flex items-center space-x-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Write Your First Story</span>
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {personalPosts.map((post) => (
                <div
                  key={post.id}
                  onClick={() => setViewingPost(post)}
                  className="apple-card cursor-pointer group overflow-hidden border border-[#ebebeb] dark:border-[#27272a] bg-white dark:bg-[#17171a] flex flex-col justify-between hover:shadow-md transition-all shadow-xs"
                >
                  <div>
                    {post.cover_image && (
                      <div className="relative h-48 w-full overflow-hidden bg-gray-100 dark:bg-zinc-800">
                        <img
                          src={post.cover_image}
                          alt={post.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                        {post.destination && (
                          <div className="absolute top-3 left-3 bg-black/70 backdrop-blur-md px-3 py-1 rounded-full text-[11px] font-semibold text-white flex items-center space-x-1">
                            <MapPin className="w-3 h-3 text-sky-400" />
                            <span>{post.destination}</span>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="p-5">
                      <div className="flex items-center justify-between text-xs text-[#71717a] dark:text-[#a1a1aa] mb-2">
                        <div className="flex items-center space-x-2">
                          <User className="w-3.5 h-3.5" />
                          <span>{post.author || "Me"}</span>
                          <span>•</span>
                          <Calendar className="w-3.5 h-3.5" />
                          <span>{post.date}</span>
                        </div>

                        {/* Edit & Delete Action Buttons */}
                        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={(e) => openEditModal(post, e)}
                            className="p-1 text-gray-400 hover:text-[#0066cc] dark:hover:text-[#2997ff] transition-colors"
                            title="Edit story"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={(e) => handleDeletePost(post.id, e)}
                            className="p-1 text-gray-400 hover:text-rose-600 transition-colors"
                            title="Delete story"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      <h3 className="text-base font-bold text-[#171717] dark:text-white mt-1 group-hover:text-[#0066cc] dark:group-hover:text-[#2997ff] transition-colors leading-snug">
                        {post.title}
                      </h3>

                      <p className="text-xs text-[#71717a] dark:text-[#a1a1aa] mt-2 line-clamp-3 leading-relaxed">
                        {post.content ? post.content.replace(/^[#\*\-]+\s*/gm, "") : "Click to read full journal entry..."}
                      </p>

                      {/* Tags & Trip Link */}
                      <div className="mt-3 flex flex-wrap items-center gap-1.5">
                        {post.trip_title && (
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 flex items-center">
                            <Bookmark className="w-2.5 h-2.5 mr-1" />
                            {post.trip_title}
                          </span>
                        )}
                        {post.tags && post.tags.slice(0, 3).map((t) => (
                          <span key={t} className="text-[10px] font-medium px-2 py-0.5 rounded bg-black/5 dark:bg-white/5 text-[#52525b] dark:text-[#d4d4d8]">
                            #{t}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="p-5 pt-0 flex items-center justify-between text-xs text-[#0066cc] dark:text-[#2997ff] font-medium border-t border-black/5 dark:border-white/5 pt-3">
                    <span className="text-[#8f8f8f] font-mono text-[11px]">{post.read_time || "3 min read"}</span>
                    <span className="flex items-center space-x-1">
                      <span>Read Story</span>
                      <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* SUBTAB 2: EDITORIAL CURATED GUIDES */}
      {activeSubTab === "editorial" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {TRAVEL_ARTICLES.map((article) => (
            <div
              key={article.id}
              className="apple-card cursor-pointer group overflow-hidden border border-[#ebebeb] dark:border-[#27272a] bg-white dark:bg-[#17171a] flex flex-col justify-between shadow-xs"
            >
              <div>
                <div className="relative h-52 w-full overflow-hidden">
                  <img src={article.image_url} alt={article.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  <div className="absolute top-3 left-3 bg-white/90 dark:bg-black/80 backdrop-blur-md px-3 py-1 rounded-full text-[11px] font-semibold text-[#171717] dark:text-white">
                    {article.category}
                  </div>
                </div>

                <div className="p-5">
                  <div className="flex items-center space-x-3 text-xs text-[#71717a] dark:text-[#a1a1aa]">
                    <span className="flex items-center space-x-1"><User className="w-3.5 h-3.5" /><span>{article.author}</span></span>
                    <span>•</span>
                    <span className="flex items-center space-x-1"><Clock className="w-3.5 h-3.5" /><span>{article.read_time}</span></span>
                    <span>•</span>
                    <span>{article.date}</span>
                  </div>

                  <h3 className="text-base font-bold text-[#171717] dark:text-white mt-2 group-hover:text-[#0066cc] dark:group-hover:text-[#2997ff] transition-colors leading-snug">
                    {article.title}
                  </h3>

                  <p className="text-xs text-[#71717a] dark:text-[#a1a1aa] mt-2 leading-relaxed line-clamp-3">
                    {article.snippet}
                  </p>
                </div>
              </div>

              <div className="p-5 pt-0 flex items-center justify-between text-xs text-[#0066cc] dark:text-[#2997ff] font-medium border-t border-[#ebebeb] dark:border-[#27272a] pt-3">
                <span className="text-[#8f8f8f]">Editorial Guide</span>
                <span className="flex items-center space-x-1">
                  <span>Read Guide</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* MODAL 1: WRITE / EDIT JOURNAL POST */}
      {isEditorOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white dark:bg-[#121214] border border-[#ebebeb] dark:border-[#27272a] rounded-[16px] max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col text-left">
            <div className="p-5 border-b border-[#ebebeb] dark:border-[#222222] flex items-center justify-between sticky top-0 bg-white/95 dark:bg-[#121214]/95 backdrop-blur-md z-10">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#0066cc]/10 dark:bg-[#2997ff]/20 text-[#0066cc] dark:text-[#2997ff] flex items-center justify-center font-bold">
                  <Edit3 className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-base text-[#171717] dark:text-white">
                  {editingPostId ? "Edit Journal Story" : "Write New Travel Story"}
                </h3>
              </div>
              <button
                onClick={() => setIsEditorOpen(false)}
                className="p-1.5 rounded-[6px] hover:bg-black/5 dark:hover:bg-white/10 text-[#8f8f8f] hover:text-[#171717] dark:hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSavePost} className="p-5 space-y-4 flex-1">
              <div>
                <label className="block text-xs font-semibold text-[#171717] dark:text-white mb-1">
                  Story Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Sunset over Nahargarh Fort & Jaigarh Hills"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-[#fafafa] dark:bg-[#1c1c1e] border border-[#ebebeb] dark:border-[#27272a] rounded-[8px] px-3 py-2 text-sm text-[#171717] dark:text-white placeholder:text-[#8f8f8f] focus:outline-none focus:border-[#0066cc]"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-[#171717] dark:text-white mb-1">
                    Destination
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Jaipur, Rajasthan"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    className="w-full bg-[#fafafa] dark:bg-[#1c1c1e] border border-[#ebebeb] dark:border-[#27272a] rounded-[8px] px-3 py-2 text-xs text-[#171717] dark:text-white placeholder:text-[#8f8f8f] focus:outline-none focus:border-[#0066cc]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#171717] dark:text-white mb-1">
                    Travel Date
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. October 15, 2026"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full bg-[#fafafa] dark:bg-[#1c1c1e] border border-[#ebebeb] dark:border-[#27272a] rounded-[8px] px-3 py-2 text-xs text-[#171717] dark:text-white placeholder:text-[#8f8f8f] focus:outline-none focus:border-[#0066cc]"
                  />
                </div>
              </div>

              {savedTrips.length > 0 && (
                <div>
                  <label className="block text-xs font-semibold text-[#171717] dark:text-white mb-1">
                    Link to Saved Trip (Optional)
                  </label>
                  <select
                    value={selectedTripId}
                    onChange={(e) => setSelectedTripId(e.target.value)}
                    className="w-full bg-[#fafafa] dark:bg-[#1c1c1e] border border-[#ebebeb] dark:border-[#27272a] rounded-[8px] px-3 py-2 text-xs text-[#171717] dark:text-white focus:outline-none focus:border-[#0066cc]"
                  >
                    <option value="">No linked trip</option>
                    {savedTrips.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.title} ({t.destination})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-[#171717] dark:text-white mb-1">
                  Cover Photo URL
                </label>
                <input
                  type="url"
                  placeholder="https://images.unsplash.com/photo-..."
                  value={photoUrl}
                  onChange={(e) => setPhotoUrl(e.target.value)}
                  className="w-full bg-[#fafafa] dark:bg-[#1c1c1e] border border-[#ebebeb] dark:border-[#27272a] rounded-[8px] px-3 py-2 text-xs text-[#171717] dark:text-white placeholder:text-[#8f8f8f] focus:outline-none focus:border-[#0066cc]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#171717] dark:text-white mb-1">
                  Story Content (Markdown supported)
                </label>
                <textarea
                  rows={8}
                  required
                  placeholder="Write about the hidden cafes you visited, the architecture, driving notes, cultural moments..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full bg-[#fafafa] dark:bg-[#1c1c1e] border border-[#ebebeb] dark:border-[#27272a] rounded-[8px] p-3 text-xs leading-relaxed text-[#171717] dark:text-white placeholder:text-[#8f8f8f] focus:outline-none focus:border-[#0066cc]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#171717] dark:text-white mb-1">
                  Tags (comma separated)
                </label>
                <input
                  type="text"
                  placeholder="Heritage, Sunset, Photography, RoadTrip"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  className="w-full bg-[#fafafa] dark:bg-[#1c1c1e] border border-[#ebebeb] dark:border-[#27272a] rounded-[8px] px-3 py-2 text-xs text-[#171717] dark:text-white placeholder:text-[#8f8f8f] focus:outline-none focus:border-[#0066cc]"
                />
              </div>

              <div className="pt-3 border-t border-[#ebebeb] dark:border-[#222222] flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsEditorOpen(false)}
                  className="px-4 py-2 rounded-[6px] text-xs font-medium bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-[#171717] dark:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-[6px] text-xs font-semibold bg-[#0066cc] hover:bg-[#0055b3] text-white shadow-sm"
                >
                  {editingPostId ? "Save Changes" : "Publish Story"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: FULL STORY VIEWER */}
      {viewingPost && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white dark:bg-[#121214] border border-[#ebebeb] dark:border-[#27272a] rounded-[16px] max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col text-left">
            {viewingPost.cover_image && (
              <div className="relative h-64 w-full overflow-hidden rounded-t-[16px]">
                <img src={viewingPost.cover_image} alt={viewingPost.title} className="w-full h-full object-cover" />
                <button
                  onClick={() => setViewingPost(null)}
                  className="absolute top-4 right-4 p-2 rounded-full bg-black/60 backdrop-blur-md text-white hover:bg-black/80 transition-all"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            <div className="p-6 space-y-4">
              {!viewingPost.cover_image && (
                <div className="flex justify-end">
                  <button
                    onClick={() => setViewingPost(null)}
                    className="p-1.5 rounded-[6px] hover:bg-black/5 dark:hover:bg-white/10 text-[#8f8f8f]"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              )}

              <div className="flex items-center space-x-2 text-xs text-[#71717a] dark:text-[#a1a1aa]">
                {viewingPost.destination && (
                  <span className="font-semibold text-[#0066cc] dark:text-[#2997ff] flex items-center">
                    <MapPin className="w-3.5 h-3.5 mr-1" />
                    {viewingPost.destination}
                  </span>
                )}
                <span>•</span>
                <span>{viewingPost.date}</span>
                <span>•</span>
                <span>{viewingPost.read_time || "3 min read"}</span>
              </div>

              <h2 className="text-2xl font-bold text-[#171717] dark:text-white leading-tight">
                {viewingPost.title}
              </h2>

              <div className="text-sm leading-relaxed text-[#3f3f46] dark:text-[#d4d4d8] whitespace-pre-line border-t border-[#ebebeb] dark:border-[#222222] pt-4">
                {viewingPost.content}
              </div>

              {viewingPost.tags && viewingPost.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-3 border-t border-[#ebebeb] dark:border-[#222222]">
                  {viewingPost.tags.map((t) => (
                    <span key={t} className="text-xs px-2.5 py-1 rounded-full bg-black/5 dark:bg-white/5 text-[#52525b] dark:text-[#d4d4d8]">
                      #{t}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="p-4 border-t border-[#ebebeb] dark:border-[#222222] bg-[#fafafa] dark:bg-[#0c0c0e] flex items-center justify-between">
              <button
                onClick={(e) => {
                  openEditModal(viewingPost, e);
                  setViewingPost(null);
                }}
                className="px-3.5 py-1.5 rounded-[6px] text-xs font-semibold bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-[#171717] dark:text-white flex items-center space-x-1.5"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Edit Story</span>
              </button>
              <button
                onClick={() => setViewingPost(null)}
                className="px-4 py-1.5 rounded-[6px] text-xs font-semibold bg-[#0066cc] text-white hover:bg-[#0055b3]"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
