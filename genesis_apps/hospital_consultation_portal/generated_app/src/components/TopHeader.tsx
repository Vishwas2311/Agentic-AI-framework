"use client";

import { HospitalLogo } from "./HospitalLogo";

interface TopHeaderProps {
  title: string;
  subtitle?: string;
}

export function TopHeader({ title, subtitle }: TopHeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-teal-600 to-teal-700 rounded-xl mb-6 shadow-sm">
      <div className="flex items-center gap-3">
        <HospitalLogo size={44} />
        <div>
          <h1 className="text-white font-bold text-lg leading-tight">{title}</h1>
          {subtitle && (
            <p className="text-teal-100 text-sm font-normal leading-tight">{subtitle}</p>
          )}
        </div>
      </div>
      <span className="text-teal-700 bg-white text-xs font-semibold px-4 py-2 rounded-full border border-teal-200 shadow-sm">
        Demo Patient Portal
      </span>
    </header>
  );
}
