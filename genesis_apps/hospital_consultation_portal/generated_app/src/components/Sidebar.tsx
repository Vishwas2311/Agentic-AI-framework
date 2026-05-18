"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Home,
  LayoutDashboard,
  CalendarPlus,
  ClipboardList,
  FileText,
  LogOut,
} from "lucide-react";

const navItems = [
  { label: "Welcome",           href: "/welcome",       icon: Home },
  { label: "Dashboard",         href: "/dashboard",     icon: LayoutDashboard },
  { label: "Book Consultation", href: "/book",          icon: CalendarPlus },
  { label: "My Consultations",  href: "/consultations", icon: ClipboardList },
  { label: "Prescriptions",     href: "/prescriptions", icon: FileText },
  { label: "Profile / Sign Out",href: "/signout",       icon: LogOut },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 flex-shrink-0 bg-white border-r border-gray-100 rounded-xl shadow-sm flex flex-col py-4 min-h-[600px]">
      <nav className="flex flex-col gap-1 px-3" aria-label="Main navigation">
        {navItems.map(({ label, href, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-teal-600 text-white"
                  : "text-navy hover:bg-teal-50 hover:text-teal-700"
              )}
              aria-current={active ? "page" : undefined}
            >
              <Icon size={16} aria-hidden="true" />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
