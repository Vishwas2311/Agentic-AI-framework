"use client";

import { useState, useMemo } from "react";
import { AppShell } from "@/components/AppShell";
import { ConsultationCard } from "@/components/ConsultationCard";
import { useApp } from "@/context/AppContext";
import { ConsultationStatus, DEPARTMENTS } from "@/types";
import { Search } from "lucide-react";

const STATUS_OPTIONS: (ConsultationStatus | "All")[] = [
  "All",
  "Requested",
  "Scheduled",
  "In Consultation",
  "Completed",
  "Cancelled",
];

export default function ConsultationsPage() {
  const { state } = useApp();
  const [search, setSearch]       = useState("");
  const [statusFilter, setStatus] = useState<ConsultationStatus | "All">("All");
  const [deptFilter, setDept]     = useState("All");

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return state.consultations.filter((c) => {
      const matchStatus = statusFilter === "All" || c.consultation_status === statusFilter;
      const matchDept   = deptFilter   === "All" || c.department === deptFilter;
      const matchSearch =
        !q ||
        c.patient_name.toLowerCase().includes(q) ||
        c.doctor.toLowerCase().includes(q) ||
        c.department.toLowerCase().includes(q);
      return matchStatus && matchDept && matchSearch;
    });
  }, [state.consultations, search, statusFilter, deptFilter]);

  return (
    <AppShell
      title="My Consultations"
      subtitle="Search, filter, and update consultation status."
    >
      {/* Filter row */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 mb-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="relative">
          <Search
            size={15}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
            aria-hidden="true"
          />
          <input
            type="search"
            placeholder="Search patient, doctor, department…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            aria-label="Search consultations"
          />
        </div>

        <div>
          <label htmlFor="status-filter" className="sr-only">Filter by status</label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatus(e.target.value as ConsultationStatus | "All")}
            className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 text-navy"
            aria-label="Filter by status"
          >
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="dept-filter" className="sr-only">Filter by department</label>
          <select
            id="dept-filter"
            value={deptFilter}
            onChange={(e) => setDept(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 text-navy"
            aria-label="Filter by department"
          >
            <option value="All">All Departments</option>
            {DEPARTMENTS.map((d) => <option key={d}>{d}</option>)}
          </select>
        </div>
      </div>

      {/* Consultation list */}
      <div className="flex flex-col gap-3">
        {filtered.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-10 text-center text-gray-400 text-sm">
            {state.consultations.length === 0
              ? "No consultations booked yet. Book your first consultation."
              : "No consultations match your search or filters."}
          </div>
        ) : (
          filtered.map((c, i) => (
            <ConsultationCard key={c.id} consultation={c} index={i} />
          ))
        )}
      </div>
    </AppShell>
  );
}
