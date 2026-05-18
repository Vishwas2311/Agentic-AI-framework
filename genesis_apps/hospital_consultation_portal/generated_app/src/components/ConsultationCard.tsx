"use client";

import { motion } from "motion/react";
import { Consultation, ConsultationStatus, STATUS_TRANSITIONS } from "@/types";
import { useApp } from "@/context/AppContext";
import { StatusBadge } from "./StatusBadge";

export function ConsultationCard({
  consultation,
  index,
}: {
  consultation: Consultation;
  index: number;
}) {
  const { dispatch } = useApp();
  const transitions = STATUS_TRANSITIONS[consultation.consultation_status];

  function updateStatus(newStatus: ConsultationStatus) {
    dispatch({ type: "UPDATE_STATUS", id: consultation.id, status: newStatus });
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.04, ease: "easeOut" }}
      className="bg-white rounded-xl border border-gray-100 shadow-sm p-5"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-navy text-base">{consultation.patient_name}</h3>
          <p className="text-gray-500 text-sm mt-0.5">
            {consultation.department} &bull; {consultation.doctor} &bull;{" "}
            {consultation.consultation_mode}
          </p>
          <p className="text-gray-400 text-xs mt-1">
            {consultation.consultation_date} {consultation.consultation_time}
          </p>
          {consultation.symptoms && (
            <p className="text-gray-500 text-xs mt-1 italic truncate max-w-sm">
              Symptoms: {consultation.symptoms}
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <StatusBadge status={consultation.consultation_status} />
          {transitions.length > 0 && (
            <div className="flex gap-1 flex-wrap justify-end">
              {transitions.map((s) => (
                <button
                  key={s}
                  onClick={() => updateStatus(s)}
                  className="bg-navy hover:bg-navy-light text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors"
                  aria-label={`Update status to ${s}`}
                >
                  → {s}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
