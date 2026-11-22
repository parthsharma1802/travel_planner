import React from "react";
import Header from "./Header";
import Footer from "./Footer";

export default function AppLayout({ children, activeTab, setActiveTab, onOpenSearch }) {
  return (
    <div className="min-h-screen bg-white dark:bg-black text-[#1d1d1f] dark:text-white flex flex-col font-sans transition-colors duration-300">
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSearch={onOpenSearch}
      />

      {/* Main Content Slot */}
      <main className="flex-1">
        {children}
      </main>

      {/* Apple Footer */}
      <Footer />
    </div>
  );
}
