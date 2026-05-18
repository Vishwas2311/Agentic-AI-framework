"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import { useApp } from "@/context/AppContext";
import { HospitalLogo } from "@/components/HospitalLogo";
import { Eye, EyeOff, Lock, User } from "lucide-react";

const DEMO_EMAIL = "patient@example.com";
const DEMO_PASSWORD = "patient123";

export default function LoginPage() {
  const { dispatch } = useApp();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    setTimeout(() => {
      if (
        email.trim().toLowerCase() === DEMO_EMAIL &&
        password === DEMO_PASSWORD
      ) {
        dispatch({ type: "LOGIN", email: email.trim().toLowerCase() });
        router.push("/welcome");
      } else {
        setError("Invalid credentials. Use patient@example.com / patient123");
      }
      setLoading(false);
    }, 400);
  }

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center p-4">
      <div className="w-full max-w-5xl flex rounded-2xl overflow-hidden shadow-lg bg-white min-h-[520px]">
        {/* Left — Login card */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          className="flex-1 flex flex-col justify-center px-10 py-12"
        >
          <div className="flex justify-center mb-6">
            <HospitalLogo size={56} />
          </div>
          <h1 className="text-2xl font-bold text-navy text-center leading-tight">
            Hospital Online Consultation Portal
          </h1>
          <p className="text-gray-500 text-sm text-center mt-2 mb-8">
            Secure patient access for virtual consultations, prescriptions, and follow-ups.
          </p>

          <form onSubmit={handleLogin} className="flex flex-col gap-4" noValidate>
            <div className="flex flex-col gap-1">
              <label htmlFor="email" className="text-sm font-medium text-navy">
                Patient ID or Email
              </label>
              <div className="relative">
                <User
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                  aria-hidden="true"
                />
                <input
                  id="email"
                  type="email"
                  autoComplete="username"
                  placeholder="patient@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-9 pr-4 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  aria-required="true"
                />
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <label htmlFor="password" className="text-sm font-medium text-navy">
                Password
              </label>
              <div className="relative">
                <Lock
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                  aria-hidden="true"
                />
                <input
                  id="password"
                  type={showPwd ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-9 pr-10 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  aria-required="true"
                />
                <button
                  type="button"
                  onClick={() => setShowPwd((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label={showPwd ? "Hide password" : "Show password"}
                >
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <p role="alert" className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-teal-600 hover:bg-teal-700 disabled:opacity-60 text-white font-semibold py-3 rounded-lg transition-colors text-sm mt-1"
            >
              {loading ? "Signing in…" : "Login Securely"}
            </button>
          </form>

          <p className="text-center text-xs text-gray-400 mt-6">
            Demo system. Do not enter real patient data.
          </p>
        </motion.div>

        {/* Right — Illustration panel */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="hidden md:flex flex-1 bg-teal-50 items-center justify-center flex-col gap-4 p-10"
        >
          <div className="w-48 h-48 relative flex items-center justify-center">
            {/* Abstract doctor consultation illustration */}
            <div className="absolute w-32 h-32 rounded-full bg-teal-100 opacity-60" />
            <div className="relative flex gap-4 items-end">
              <div className="flex flex-col items-center gap-1">
                <div className="w-10 h-10 rounded-full bg-[#F4C99A]" />
                <div className="w-10 h-16 rounded-t-lg bg-teal-600" />
              </div>
              <div className="flex flex-col items-center gap-1">
                <div className="w-10 h-10 rounded-full bg-[#F4C99A]" />
                <div className="w-10 h-20 rounded-t-lg bg-teal-400" />
              </div>
            </div>
          </div>
          <p className="text-teal-700 font-semibold text-base text-center">
            Online Doctor Consultation
          </p>
          <p className="text-teal-500 text-sm text-center max-w-[220px]">
            Book virtual consultations from the comfort of your home.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
