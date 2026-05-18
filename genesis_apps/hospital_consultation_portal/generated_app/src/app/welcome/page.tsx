"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { AppShell } from "@/components/AppShell";
import { useApp } from "@/context/AppContext";
import { CalendarPlus, ClipboardList, FileText, HeadphonesIcon } from "lucide-react";

export default function WelcomePage() {
  const { state } = useApp();

  const infoCards = [
    { label: "Upcoming Consultations", desc: "Track scheduled appointments", icon: ClipboardList },
    { label: "Prescriptions",          desc: "Check availability after visits",  icon: FileText },
    { label: "Support",                desc: "Contact hospital desk",             icon: HeadphonesIcon },
  ];

  return (
    <AppShell
      title="Welcome to Online Consultation"
      subtitle="Book, track, and manage your hospital consultations from home."
    >
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8">
        {/* Hero row */}
        <div className="flex flex-col md:flex-row md:items-start gap-8">
          <div className="flex-1">
            <motion.h2
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35 }}
              className="text-3xl font-bold text-navy"
            >
              Welcome, Patient
            </motion.h2>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.35, delay: 0.1 }}
              className="text-gray-500 mt-2 mb-8 text-sm"
            >
              Your healthcare journey is now simpler. Choose a quick action below to get started.
            </motion.p>

            <div className="flex flex-wrap gap-3">
              <Link
                href="/book"
                className="bg-teal-600 hover:bg-teal-700 text-white font-semibold px-6 py-3 rounded-lg text-sm transition-colors"
              >
                <CalendarPlus size={15} className="inline mr-2 -mt-0.5" aria-hidden="true" />
                Book Consultation
              </Link>
              <Link
                href="/consultations"
                className="bg-navy hover:bg-navy-light text-white font-semibold px-6 py-3 rounded-lg text-sm transition-colors"
              >
                <ClipboardList size={15} className="inline mr-2 -mt-0.5" aria-hidden="true" />
                View Consultations
              </Link>
            </div>
          </div>

          {/* Illustration */}
          <div className="hidden md:flex flex-col items-center justify-center bg-teal-50 rounded-xl p-6 gap-3 min-w-[200px]">
            <div className="flex gap-4 items-end">
              <div className="flex flex-col items-center gap-1">
                <div className="w-8 h-8 rounded-full bg-[#F4C99A]" />
                <div className="w-10 h-14 rounded-t-lg bg-teal-600" />
              </div>
              <div className="flex flex-col items-center gap-1">
                <div className="w-8 h-8 rounded-full bg-[#F4C99A]" />
                <div className="w-10 h-16 rounded-t-lg bg-teal-400" />
              </div>
            </div>
            <p className="text-teal-700 font-semibold text-sm text-center">Video Consultation Ready</p>
          </div>
        </div>

        {/* Info cards row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8 pt-6 border-t border-gray-100">
          {infoCards.map(({ label, desc, icon: Icon }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: 0.15 + i * 0.06 }}
              className="bg-surface rounded-xl border border-gray-100 p-4"
            >
              <Icon size={18} className="text-teal-600 mb-2" aria-hidden="true" />
              <h3 className="font-semibold text-navy text-sm">{label}</h3>
              <p className="text-gray-400 text-xs mt-0.5">{desc}</p>
            </motion.div>
          ))}
        </div>
      </div>

      <p className="text-xs text-gray-400 text-center mt-4">
        Logged in as: {state.session.patientEmail}
      </p>
    </AppShell>
  );
}
