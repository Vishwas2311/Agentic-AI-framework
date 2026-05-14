import { PROVIDERS } from "./mock-data";

export function recommendProviders(specialty: string, urgencyLevel: string) {
  const normalized = specialty.toLowerCase();
  const urgent = urgencyLevel.toLowerCase().includes("urgent") || urgencyLevel.toLowerCase().includes("emergency");
  const preferred = PROVIDERS.filter((provider) => provider.specialty.toLowerCase().includes(normalized) && provider.acceptingPatients);
  const fallback = urgent
    ? PROVIDERS.filter((provider) => provider.specialty === "Urgent Care")
    : PROVIDERS.filter((provider) => provider.acceptingPatients);
  return (preferred.length ? preferred : fallback).slice(0, 3);
}
