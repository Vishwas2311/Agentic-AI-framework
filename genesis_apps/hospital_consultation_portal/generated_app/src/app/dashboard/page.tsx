"use client";

import { AppShell } from "@/components/AppShell";
import { MetricCard } from "@/components/MetricCard";
import { ActionCard } from "@/components/ActionCard";
import { useApp } from "@/context/AppContext";

export default function DashboardPage() {
  const { state } = useApp();
  const { consultations } = state;

  const total      = consultations.length;
  const scheduled  = consultations.filter((c) => c.consultation_status === "Scheduled").length;
  const completed  = consultations.filter((c) => c.consultation_status === "Completed").length;
  const prescribed = consultations.filter((c) => c.prescription_status === "Available").length;

  const metrics = [
    { value: total,      label: "Total Consultations" },
    { value: scheduled,  label: "Scheduled" },
    { value: completed,  label: "Completed" },
    { value: prescribed, label: "Prescriptions Available" },
  ];

  const actions = [
    { title: "Book New Consultation", description: "Choose department, doctor, date and mode.", href: "/book" },
    { title: "My Consultations",      description: "Track status and update visit workflow.",  href: "/consultations" },
    { title: "View Prescriptions",    description: "See demo summaries for completed visits.",  href: "/prescriptions" },
    { title: "Contact Support",       description: "Get appointment help.",                     href: "#" },
  ];

  return (
    <AppShell
      title="Hospital Online Consultation Portal"
      subtitle="Patient dashboard for bookings, status, and prescriptions."
    >
      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {metrics.map((m) => (
          <MetricCard key={m.label} value={m.value} label={m.label} />
        ))}
      </div>

      {/* Action cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {actions.map((a) => (
          <ActionCard key={a.title} title={a.title} description={a.description} href={a.href} />
        ))}
      </div>
    </AppShell>
  );
}
