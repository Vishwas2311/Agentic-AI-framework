"use client";

import { AppShell } from "@/components/AppShell";
import { useApp } from "@/context/AppContext";
import { CheckCircle, Clock, FileText } from "lucide-react";

export default function PrescriptionsPage() {
  const { state } = useApp();

  const completedConsultations = state.consultations.filter(
    (c) => c.consultation_status === "Completed"
  );

  const hasAvailable = completedConsultations.length > 0;

  return (
    <AppShell
      title="Prescriptions & Medical Summary"
      subtitle="Demo prescription summaries for completed consultations."
    >
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 max-w-3xl">
        <h2 className="text-xl font-bold text-navy mb-6">Prescription Status</h2>

        {/* Status badge */}
        <div className="mb-6">
          {hasAvailable ? (
            <span className="inline-flex items-center gap-2 bg-teal-50 border border-teal-200 text-teal-700 px-4 py-2.5 rounded-xl font-semibold text-sm">
              <CheckCircle size={16} aria-hidden="true" />
              Available for Completed Visit
            </span>
          ) : (
            <span className="inline-flex items-center gap-2 bg-amber-50 border border-amber-200 text-amber-700 px-4 py-2.5 rounded-xl font-semibold text-sm">
              <Clock size={16} aria-hidden="true" />
              Pending — Complete a consultation to view prescription
            </span>
          )}
        </div>

        {hasAvailable ? (
          <>
            {/* Summary cards */}
            {[
              {
                title: "Doctor Advice",
                body: "This is a demo prescription summary. Follow-up with hospital desk for real medical advice.",
              },
              {
                title: "Medication Notes",
                body: "Placeholder medication notes shown only for app demonstration.",
              },
              {
                title: "Follow-up Recommendation",
                body: "Schedule a follow-up consultation if symptoms continue.",
              },
            ].map(({ title, body }) => (
              <div
                key={title}
                className="flex items-start gap-4 bg-surface rounded-xl border border-gray-100 px-5 py-4 mb-3"
              >
                <FileText size={18} className="text-teal-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
                <div>
                  <h3 className="font-semibold text-navy text-sm">{title}</h3>
                  <p className="text-gray-500 text-sm mt-0.5">{body}</p>
                </div>
              </div>
            ))}

            <button
              disabled
              className="mt-4 bg-teal-600 opacity-70 cursor-not-allowed text-white font-semibold px-6 py-2.5 rounded-lg text-sm"
              aria-label="Download placeholder prescription (demo only)"
            >
              Download Placeholder
            </button>

            <p className="text-xs text-gray-400 mt-3">
              This is a demo prescription summary. Do not use as real medical advice.
            </p>
          </>
        ) : (
          <div className="text-gray-400 text-sm bg-surface rounded-xl p-6 text-center">
            No prescriptions available yet. Complete a consultation to view the demo summary.
          </div>
        )}
      </div>
    </AppShell>
  );
}
