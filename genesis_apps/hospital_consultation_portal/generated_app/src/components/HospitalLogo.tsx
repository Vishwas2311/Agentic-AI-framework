"use client";

export function HospitalLogo({ size = 40 }: { size?: number }) {
  return (
    <div
      className="flex items-center justify-center rounded-full bg-teal-600 text-white font-bold flex-shrink-0"
      style={{ width: size, height: size, fontSize: size * 0.5 }}
      aria-label="Hospital logo"
    >
      +
    </div>
  );
}
