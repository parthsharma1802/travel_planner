import React, { useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

export default function HorizontalCarouselSection({ title, subtitle, badge, children }) {
  const scrollRef = useRef(null);

  const scroll = (direction) => {
    if (scrollRef.current) {
      const { scrollLeft, clientWidth } = scrollRef.current;
      const scrollAmount = clientWidth * 0.75;
      scrollRef.current.scrollTo({
        left: direction === "left" ? scrollLeft - scrollAmount : scrollLeft + scrollAmount,
        behavior: "smooth"
      });
    }
  };

  return (
    <section className="py-10 bg-white dark:bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex items-end justify-between mb-6">
          <div>
            {badge && (
              <span className="text-xs font-semibold uppercase tracking-wider text-[#0066cc] dark:text-[#2997ff]">
                {badge}
              </span>
            )}
            <h2 className="text-2xl sm:text-3xl font-semibold text-[#1d1d1f] dark:text-white tracking-tight mt-0.5">
              {title}
            </h2>
            {subtitle && (
              <p className="text-xs text-[#7a7a7a] dark:text-zinc-400 mt-1">{subtitle}</p>
            )}
          </div>

          {/* Carousel Left / Right Scroll Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => scroll("left")}
              aria-label="Scroll Left"
              className="w-9 h-9 rounded-full bg-[#f5f5f7] dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700 flex items-center justify-center text-[#1d1d1f] dark:text-white transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={() => scroll("right")}
              aria-label="Scroll Right"
              className="w-9 h-9 rounded-full bg-[#f5f5f7] dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700 flex items-center justify-center text-[#1d1d1f] dark:text-white transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Side-Scrolling Horizontal Container */}
        <div
          ref={scrollRef}
          className="flex space-x-6 overflow-x-auto snap-x snap-mandatory scrollbar-none pb-4 pt-1"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          {children}
        </div>
      </div>
    </section>
  );
}
