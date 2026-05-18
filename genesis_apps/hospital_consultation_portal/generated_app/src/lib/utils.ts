import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { ConsultationStatus } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function statusColor(status: ConsultationStatus): string {
  switch (status) {
    case "Requested":
      return "bg-amber-100 text-amber-800 border-amber-300";
    case "Scheduled":
      return "bg-teal-100 text-teal-700 border-teal-300";
    case "In Consultation":
      return "bg-blue-100 text-blue-700 border-blue-300";
    case "Completed":
      return "bg-green-100 text-green-700 border-green-300";
    case "Cancelled":
      return "bg-red-100 text-red-700 border-red-300";
    default:
      return "bg-gray-100 text-gray-700 border-gray-300";
  }
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  try {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}
