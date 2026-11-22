import React from "react";
import { ChevronRight } from "lucide-react";

export default function PageHeader({ title, subtitle, badge, breadcrumbs = [], actions }) {
  return (
    <div className="py-8 border-b border-gray-200/60 dark:border-zinc-800/80 mb-8">
      {/* Breadcrumbs */}
      {breadcrumbs.length > 0 && (
        <nav className="flex items-center space-x-1.5 text-xs text-[#7a7a7a] dark:text-zinc-400 mb-3">
          {breadcrumbs.map((crumb, idx) => (
            <React.Fragment key={crumb}>
              {idx > 0 && <ChevronRight className="w-3 h-3 text-gray-400" />}
              <span className={idx === breadcrumbs.length - 1 ? "font-semibold text-[#1d1d1f] dark:text-white" : ""}>
                {crumb}
              </span>
            </React.Fragment>
          ))}
        </nav>
      )}

      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          {badge && (
            <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-blue-50 dark:bg-blue-950 text-[#0066cc] dark:text-[#2997ff] border border-blue-100 dark:border-blue-900/40 mb-2">
              {badge}
            </span>
          )}
          <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-[#1d1d1f] dark:text-white">
            {title}
          </h1>
          {subtitle && (
            <p className="text-sm text-[#7a7a7a] dark:text-zinc-400 mt-1 max-w-2xl leading-relaxed">
              {subtitle}
            </p>
          )}
        </div>

        {actions && <div className="flex items-center space-x-3">{actions}</div>}
      </div>
    </div>
  );
}
