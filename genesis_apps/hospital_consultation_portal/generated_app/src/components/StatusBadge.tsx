"use client";

import { cn, statusColor } from "@/lib/utils";
import { ConsultationStatus } from "@/types";

export function StatusBadge({ status }: { status: ConsultationStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border",
        statusColor(status)
      )}
      aria-label={`Status: ${status}`}
    >
      {status}
    </span>
  );
}
