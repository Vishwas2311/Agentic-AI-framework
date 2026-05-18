"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import { AppShell } from "@/components/AppShell";
import { useApp } from "@/context/AppContext";
import { CheckCircle } from "lucide-react";

export default function SignOutPage() {
  const { dispatch } = useApp();
  const router = useRouter();
  const [done, setDone] = useState(false);

  function handleSignOut() {
    setDone(true);
    setTimeout(() => {
      dispatch({ type: "LOGOUT" });
      router.replace("/");
    }, 1200);
  }

  return (
    <AppShell title="Profile / Sign Out" subtitle="Safely end your hospital portal session.">
      <div className="flex items-start justify-center pt-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="bg-white rounded-2xl border border-gray-100 shadow-sm p-12 flex flex-col items-center gap-5 max-w-lg w-full text-center"
        >
          {done ? (
            <>
              <CheckCircle size={56} className="text-teal-500" aria-hidden="true" />
              <h2 className="text-xl font-bold text-navy">Signed out successfully</h2>
              <p className="text-gray-500 text-sm">
                Your session has been cleared. Returning to login…
              </p>
            </>
          ) : (
            <>
              <div className="w-16 h-16 rounded-full bg-teal-50 flex items-center justify-center">
                <CheckCircle size={36} className="text-teal-500" aria-hidden="true" />
              </div>
              <h2 className="text-2xl font-bold text-navy">You are about to sign out</h2>
              <p className="text-gray-500 text-sm">
                After signing out, your session will be cleared and the login page will be shown again.
              </p>
              <button
                onClick={handleSignOut}
                className="bg-red-500 hover:bg-red-600 text-white font-semibold px-10 py-3 rounded-xl text-sm transition-colors"
              >
                Sign Out Securely
              </button>
              <p className="text-xs text-gray-400">
                Demo system. Do not enter real patient data.
              </p>
            </>
          )}
        </motion.div>
      </div>
    </AppShell>
  );
}
