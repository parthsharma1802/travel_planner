import React, { useState } from "react";
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, X, Check, Clock, Sparkles } from "lucide-react";

export default function TravelCalendarModal({ isOpen, onClose, onSelectDateRange }) {
  const [currentDate, setCurrentDate] = useState(new Date(2026, 9, 1)); // Default Oct 2026
  const [startDate, setStartDate] = useState(15);
  const [endDate, setEndDate] = useState(20);

  if (!isOpen) return null;

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth(); // 0-indexed

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayOfWeek = new Date(year, month, 1).getDay(); // 0 = Sun

  const handlePrevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const handleDateClick = (day) => {
    if (!startDate || (startDate && endDate)) {
      setStartDate(day);
      setEndDate(null);
    } else if (startDate && !endDate) {
      if (day < startDate) {
        setStartDate(day);
        setEndDate(null);
      } else {
        setEndDate(day);
      }
    }
  };

  const applyPreset = (numDays) => {
    setStartDate(10);
    setEndDate(10 + numDays - 1);
  };

  const daysCount = startDate && endDate ? endDate - startDate + 1 : startDate ? 1 : 0;
  const nightsCount = daysCount > 1 ? daysCount - 1 : 0;

  const formatMonthName = monthNames[month];

  const formattedStartStr = startDate ? `${startDate} ${formatMonthName.slice(0, 3)} ${year}` : "";
  const formattedEndStr = endDate ? `${endDate} ${formatMonthName.slice(0, 3)} ${year}` : "";
  const rangeDisplay = endDate ? `${formattedStartStr} - ${formattedEndStr}` : formattedStartStr;

  const handleApply = () => {
    if (!startDate) return;
    onSelectDateRange({
      startDate: formattedStartStr,
      endDate: formattedEndStr,
      rangeDisplay,
      daysCount,
      nightsCount,
      fullText: `${rangeDisplay} (${daysCount} Days / ${nightsCount} Nights)`
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-[#111111] border border-[#ebebeb] dark:border-[#222222] rounded-[16px] shadow-2xl w-full max-w-lg overflow-hidden font-sans text-left">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-4 px-5 border-b border-[#ebebeb] dark:border-[#222222]">
          <div className="flex items-center space-x-2">
            <CalendarIcon className="w-5 h-5 text-[#0070f3]" />
            <h3 className="font-semibold text-base text-[#171717] dark:text-white">
              Select Travel Date Range
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-[6px] text-[#8f8f8f] hover:text-[#171717] dark:hover:text-white hover:bg-gray-100 dark:hover:bg-zinc-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Calendar Body */}
        <div className="p-5 space-y-4">
          {/* Quick Presets */}
          <div>
            <p className="text-[11px] font-mono font-medium text-[#8f8f8f] uppercase tracking-wider mb-2">
              Quick Indian Trip Presets
            </p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => applyPreset(2)}
                className="px-3 py-1.5 rounded-[6px] text-xs font-medium bg-[#fafafa] dark:bg-[#1c1c1c] border border-[#ebebeb] dark:border-[#333333] hover:border-[#0070f3] text-[#171717] dark:text-white transition-colors"
              >
                Weekend (2 Days)
              </button>
              <button
                onClick={() => applyPreset(4)}
                className="px-3 py-1.5 rounded-[6px] text-xs font-medium bg-[#fafafa] dark:bg-[#1c1c1c] border border-[#ebebeb] dark:border-[#333333] hover:border-[#0070f3] text-[#171717] dark:text-white transition-colors"
              >
                Long Weekend (4 Days)
              </button>
              <button
                onClick={() => applyPreset(7)}
                className="px-3 py-1.5 rounded-[6px] text-xs font-medium bg-[#fafafa] dark:bg-[#1c1c1c] border border-[#ebebeb] dark:border-[#333333] hover:border-[#0070f3] text-[#171717] dark:text-white transition-colors"
              >
                1 Week (7 Days)
              </button>
              <button
                onClick={() => applyPreset(14)}
                className="px-3 py-1.5 rounded-[6px] text-xs font-medium bg-[#fafafa] dark:bg-[#1c1c1c] border border-[#ebebeb] dark:border-[#333333] hover:border-[#0070f3] text-[#171717] dark:text-white transition-colors"
              >
                2 Weeks (14 Days)
              </button>
            </div>
          </div>

          {/* Month Header Navigation */}
          <div className="flex items-center justify-between pt-2">
            <h4 className="font-semibold text-sm text-[#171717] dark:text-white">
              {formatMonthName} {year}
            </h4>
            <div className="flex items-center space-x-1">
              <button
                onClick={handlePrevMonth}
                className="p-1.5 rounded-[6px] hover:bg-gray-100 dark:hover:bg-zinc-800 text-[#171717] dark:text-white transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={handleNextMonth}
                className="p-1.5 rounded-[6px] hover:bg-gray-100 dark:hover:bg-zinc-800 text-[#171717] dark:text-white transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Days Grid */}
          <div>
            {/* Weekday Labels */}
            <div className="grid grid-cols-7 gap-1 text-center font-mono text-[11px] text-[#8f8f8f] mb-1 font-semibold">
              <span>Su</span>
              <span>Mo</span>
              <span>Tu</span>
              <span>We</span>
              <span>Th</span>
              <span>Fr</span>
              <span>Sa</span>
            </div>

            {/* Day Numbers */}
            <div className="grid grid-cols-7 gap-1 text-center text-xs">
              {/* Empty leading padding days */}
              {Array.from({ length: firstDayOfWeek }).map((_, idx) => (
                <div key={`empty-${idx}`} className="h-9" />
              ))}

              {/* Month Days */}
              {Array.from({ length: daysInMonth }).map((_, idx) => {
                const day = idx + 1;
                const isStart = startDate === day;
                const isEnd = endDate === day;
                const isInRange = startDate && endDate && day > startDate && day < endDate;

                let btnStyle = "bg-transparent text-[#171717] dark:text-white hover:bg-gray-100 dark:hover:bg-zinc-800";
                if (isStart || isEnd) {
                  btnStyle = "bg-[#0070f3] text-white font-bold shadow-sm";
                } else if (isInRange) {
                  btnStyle = "bg-blue-100 dark:bg-blue-900/50 text-[#0070f3] dark:text-blue-200 font-medium";
                }

                return (
                  <button
                    key={day}
                    onClick={() => handleDateClick(day)}
                    className={`h-9 rounded-[8px] flex items-center justify-center transition-all ${btnStyle}`}
                  >
                    {day}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Selected Summary Bar */}
          {startDate && (
            <div className="p-3 bg-[#fafafa] dark:bg-[#171717] rounded-[10px] border border-[#ebebeb] dark:border-[#222222] flex items-center justify-between text-xs">
              <div>
                <p className="text-[#8f8f8f] text-[10px] font-mono">SELECTED TRIP RANGE</p>
                <p className="font-semibold text-[#171717] dark:text-white mt-0.5">{rangeDisplay}</p>
              </div>
              <div className="text-right">
                <span className="font-bold text-sm text-[#0070f3]">
                  {daysCount} Days {nightsCount > 0 ? `/ ${nightsCount} Nights` : ""}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer Actions */}
        <div className="p-4 px-5 border-t border-[#ebebeb] dark:border-[#222222] flex items-center justify-end space-x-3 bg-gray-50/50 dark:bg-[#171717]/50">
          <button
            onClick={onClose}
            className="vercel-btn-control !py-2 !px-4 text-xs font-medium"
          >
            Cancel
          </button>
          <button
            onClick={handleApply}
            disabled={!startDate}
            className="vercel-btn-pill !py-2 !px-5 text-xs font-medium flex items-center space-x-1.5 disabled:opacity-40"
          >
            <Check className="w-3.5 h-3.5" />
            <span>Apply Travel Dates</span>
          </button>
        </div>
      </div>
    </div>
  );
}
