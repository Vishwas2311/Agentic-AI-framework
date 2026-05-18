"use client";

import Link from "next/link";

interface ActionCardProps {
  title: string;
  description: string;
  href: string;
}

export function ActionCard({ title, description, href }: ActionCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 flex items-start justify-between gap-4">
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-navy text-base leading-snug">{title}</h3>
        <p className="text-gray-500 text-sm mt-1 leading-snug">{description}</p>
      </div>
      <Link
        href={href}
        className="flex-shrink-0 bg-teal-600 hover:bg-teal-700 text-white text-sm font-semibold px-5 py-2 rounded-lg transition-colors"
      >
        Open
      </Link>
    </div>
  );
}
