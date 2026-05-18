"use client";

import { motion } from "motion/react";

interface MetricCardProps {
  value: number;
  label: string;
}

export function MetricCard({ value, label }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 flex flex-col gap-1"
    >
      <span className="text-3xl font-bold text-teal-600">{value}</span>
      <span className="text-sm text-gray-500 font-medium">{label}</span>
    </motion.div>
  );
}
