import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Clean and sanitize markdown content before rendering:
 * - Extracts conversational message if raw JSON payload leaked into text
 * - Unescapes literal \\n and \\" characters
 * - Cleans stray braces or python dict syntax
 */
function sanitizeMarkdown(raw) {
  if (!raw || typeof raw !== "string") return "";
  let s = raw.trim();

  // If raw content starts with code block json or naked json
  if (s.startsWith("```json")) {
    s = s.slice(7);
    if (s.endsWith("```")) s = s.slice(0, -3);
    s = s.trim();
  } else if (s.startsWith("```") && s.endsWith("```")) {
    const inner = s.slice(3, -3).trim();
    if (inner.startsWith("{") && inner.endsWith("}")) {
      s = inner;
    }
  }

  // Check if string is a JSON object dump
  if ((s.startsWith("{") && s.endsWith("}")) || (s.startsWith("[") && s.endsWith("]"))) {
    try {
      const parsed = JSON.parse(s);
      if (typeof parsed === "object" && parsed !== null) {
        if (parsed.message && typeof parsed.message === "string") {
          s = parsed.message;
        } else if (parsed.summary && typeof parsed.summary === "string") {
          s = parsed.summary;
        } else if (parsed.itinerary && Array.isArray(parsed.itinerary.days)) {
          // Construct markdown summary if only raw itinerary JSON was returned
          const daysMd = parsed.itinerary.days
            .map(
              (d) =>
                `### Day ${d.day || ""}: ${d.title || ""}\n• **Morning**: ${d.morning || "—"}\n• **Afternoon**: ${d.afternoon || "—"}\n• **Evening**: ${d.evening || "—"}\n• **Stay**: ${d.stay || "—"}`
            )
            .join("\n\n");
          s = `## Travel Itinerary\n\n${daysMd}`;
        }
      }
    } catch {
      // Regex extraction fallback for "message": "..."
      const msgMatch = s.match(/"message"\s*:\s*"((?:\\.|[^"\\])*)"/);
      if (msgMatch && msgMatch[1]) {
        try {
          s = JSON.parse(`"${msgMatch[1]}"`);
        } catch {
          s = msgMatch[1].replace(/\\n/g, "\n").replace(/\\"/g, '"');
        }
      }
    }
  }

  // Unescape literal backslash-n if present
  if (s.includes("\\n")) {
    s = s.replace(/\\n/g, "\n");
  }
  if (s.includes('\\"')) {
    s = s.replace(/\\"/g, '"');
  }

  return s.trim();
}

export default function MarkdownRenderer({ content, className = "", isUser = false }) {
  const sanitized = useMemo(() => sanitizeMarkdown(content), [content]);

  return (
    <div
      className={`markdown-content text-sm leading-relaxed space-y-2.5 ${
        isUser
          ? "text-white dark:text-zinc-900 font-medium"
          : "text-[#171717] dark:text-[#ededed]"
      } ${className}`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headers
          h1: ({ node, ...props }) => (
            <h1
              className={`text-xl sm:text-2xl font-bold mt-4 mb-2 pb-1 border-b ${
                isUser
                  ? "text-white dark:text-zinc-950 border-white/20 dark:border-black/10"
                  : "text-[#171717] dark:text-white border-black/5 dark:border-white/10"
              }`}
              {...props}
            />
          ),
          h2: ({ node, ...props }) => (
            <h2
              className={`text-lg sm:text-xl font-bold mt-3.5 mb-2 flex items-center space-x-2 ${
                isUser ? "text-white dark:text-zinc-950" : "text-[#171717] dark:text-white"
              }`}
              {...props}
            />
          ),
          h3: ({ node, ...props }) => (
            <h3
              className={`text-base sm:text-lg font-semibold mt-3 mb-1.5 ${
                isUser ? "text-white dark:text-zinc-950" : "text-[#171717] dark:text-white"
              }`}
              {...props}
            />
          ),
          h4: ({ node, ...props }) => (
            <h4
              className={`text-sm sm:text-base font-semibold mt-2 mb-1 ${
                isUser ? "text-white dark:text-zinc-950" : "text-[#171717] dark:text-white"
              }`}
              {...props}
            />
          ),

          // Paragraphs & Lists
          p: ({ node, ...props }) => (
            <p
              className={`leading-relaxed mb-2.5 last:mb-0 ${
                isUser ? "text-white dark:text-zinc-900 font-normal sm:font-medium text-sm sm:text-[15px]" : "text-[#333333] dark:text-[#e4e4e7]"
              }`}
              {...props}
            />
          ),
          ul: ({ node, ...props }) => (
            <ul
              className={`list-disc pl-5 space-y-1 mb-2.5 ${
                isUser ? "text-white dark:text-zinc-900" : "text-[#333333] dark:text-[#e4e4e7]"
              }`}
              {...props}
            />
          ),
          ol: ({ node, ...props }) => (
            <ol
              className={`list-decimal pl-5 space-y-1 mb-2.5 ${
                isUser ? "text-white dark:text-zinc-900" : "text-[#333333] dark:text-[#e4e4e7]"
              }`}
              {...props}
            />
          ),
          li: ({ node, ...props }) => (
            <li className="leading-relaxed pl-1" {...props} />
          ),

          // Bold & Emphasis
          strong: ({ node, ...props }) => (
            <strong
              className={`font-semibold ${
                isUser ? "text-white dark:text-black" : "text-[#171717] dark:text-white"
              }`}
              {...props}
            />
          ),
          em: ({ node, ...props }) => (
            <em
              className={`italic ${
                isUser ? "text-white/90 dark:text-zinc-800" : "text-[#4a4a4a] dark:text-[#d1d1d6]"
              }`}
              {...props}
            />
          ),

          // Blockquotes
          blockquote: ({ node, ...props }) => (
            <blockquote
              className={`border-l-4 pl-3.5 py-1 my-2.5 rounded-r-[6px] italic ${
                isUser
                  ? "border-white/60 dark:border-black/60 bg-white/10 dark:bg-black/5 text-white dark:text-zinc-900"
                  : "border-[#e91e63] dark:border-[#ff4081] bg-pink-50/50 dark:bg-pink-950/20 text-[#4a4a4a] dark:text-[#d4d4d8]"
              }`}
              {...props}
            />
          ),

          // Tables
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-3 rounded-[10px] border border-[#ebebeb] dark:border-[#27272a] shadow-xs">
              <table className="w-full text-left text-xs border-collapse divide-y divide-[#ebebeb] dark:divide-[#27272a]" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-[#f9fafb] dark:bg-[#18181b] text-[#171717] dark:text-white font-semibold" {...props} />
          ),
          tbody: ({ node, ...props }) => (
            <tbody className="divide-y divide-[#ebebeb] dark:divide-[#27272a] bg-white dark:bg-[#111111]" {...props} />
          ),
          tr: ({ node, ...props }) => (
            <tr className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="px-3.5 py-2.5 font-semibold text-[11px] uppercase tracking-wider text-[#71717a] dark:text-[#a1a1aa] whitespace-nowrap" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td
              className={`px-3.5 py-2.5 whitespace-normal leading-normal ${
                isUser ? "text-white dark:text-zinc-900" : "text-[#333333] dark:text-[#e4e4e7]"
              }`}
              {...props}
            />
          ),

          // Code
          code: ({ node, inline, ...props }) =>
            inline ? (
              <code
                className={`px-1.5 py-0.5 rounded-[4px] font-mono text-[11px] ${
                  isUser
                    ? "bg-white/20 dark:bg-black/10 text-white dark:text-zinc-950 font-semibold"
                    : "bg-black/5 dark:bg-white/10 text-[#e91e63] dark:text-[#ff4081]"
                }`}
                {...props}
              />
            ) : (
              <pre className="p-3 rounded-[8px] bg-[#18181b] text-gray-100 font-mono text-xs overflow-x-auto my-2 border border-zinc-800">
                <code {...props} />
              </pre>
            ),

          // Links
          a: ({ node, ...props }) => (
            <a
              className={`${
                isUser
                  ? "text-cyan-200 dark:text-blue-600 underline font-semibold"
                  : "text-[#0070f3] dark:text-[#38bdf8] hover:underline font-medium"
              }`}
              target="_blank"
              rel="noopener noreferrer"
              {...props}
            />
          ),

          // Horizontal rule
          hr: ({ node, ...props }) => (
            <hr
              className={`my-4 border-t ${
                isUser ? "border-white/20 dark:border-black/20" : "border-[#ebebeb] dark:border-[#27272a]"
              }`}
              {...props}
            />
          )
        }}
      >
        {sanitized}
      </ReactMarkdown>
    </div>
  );
}
