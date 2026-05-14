"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import type { CSSProperties, ChangeEvent, FormEvent, ReactNode } from "react";
import { MotionConfig } from "motion/react";
import {
  AlertTriangle,
  ArrowRight,
  Check,
  ChevronDown,
  FileText,
  HeartPulse,
  Home,
  Lock,
  LogOut,
  MapPin,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Upload,
  UserRoundCheck,
} from "lucide-react";
import { PROVIDERS as DEMO_PROVIDERS } from "@/lib/mock-data";
import type { AiResponseSource, DocumentSummaryResponse, Provider, TriageRequest, TriageResponse, User } from "@/lib/types";

type View = "home" | "login" | "dashboard" | "triage" | "navigator" | "documents" | "emergency" | "safety";

const APP_NAME = "CLAIR";
const APP_FRAME = "w-full";
const protectedViewPaths: Partial<Record<View, string>> = {
  dashboard: "/dashboard",
  triage: "/triage",
  navigator: "/navigator",
  documents: "/documents",
  emergency: "/emergency",
  safety: "/safety",
};

const navItems: Array<{ href: string; label: string; icon: ReactNode; view: View }> = [
  { href: "/dashboard", label: "Dashboard", icon: <Home size={15} />, view: "dashboard" },
  { href: "/triage", label: "Symptom Triage", icon: <HeartPulse size={15} />, view: "triage" },
  { href: "/navigator", label: "Care Navigator", icon: <MapPin size={15} />, view: "navigator" },
  { href: "/documents", label: "Documents", icon: <FileText size={15} />, view: "documents" },
  { href: "/emergency", label: "Emergency", icon: <ShieldAlert size={15} />, view: "emergency" },
  { href: "/safety", label: "Safety & Trust", icon: <ShieldCheck size={15} />, view: "safety" },
];

function getPostLoginPath() {
  if (typeof window === "undefined") return "/dashboard";
  const requestedPath = new URLSearchParams(window.location.search).get("next");
  if (requestedPath?.startsWith("/") && !requestedPath.startsWith("//")) {
    return requestedPath;
  }
  return "/dashboard";
}

function goAfterAuth() {
  window.location.assign(getPostLoginPath());
}

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "U";
}

function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  disabled = false,
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  variant?: "primary" | "secondary" | "danger" | "yellow";
  disabled?: boolean;
  className?: string;
}) {
  const styles = {
    primary: "bg-[var(--clair-ink)] text-white hover:bg-black",
    secondary: "border border-black/10 bg-white/70 text-[var(--clair-ink)] hover:bg-white",
    danger: "bg-red-600 text-white hover:bg-red-700",
    yellow: "bg-[var(--clair-yellow)] text-[var(--clair-ink)] hover:bg-[#ffd33d]",
  }[variant];

  return (
    <button
      type={type}
      disabled={disabled}
      className={`motion-hover-lift inline-flex min-h-10 items-center justify-center gap-2 rounded-full px-5 py-2 text-sm font-semibold transition ${styles} disabled:cursor-not-allowed disabled:opacity-55 disabled:hover:translate-y-0 disabled:hover:shadow-none ${className}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`clair-card motion-card motion-hover-lift ${className}`}>{children}</section>;
}

function DarkPanel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`clair-dark-card motion-card motion-hover-lift ${className}`}>{children}</section>;
}

function Field({
  label,
  value,
  onChange,
  placeholder = "",
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
      <span>{label}</span>
      <input
        aria-label={label}
        type={type}
        autoComplete={type === "password" ? "current-password" : label === "Email" ? "username" : undefined}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        className="h-11 rounded-2xl border border-black/10 bg-white/70 px-4 text-slate-950 outline-none transition focus:border-[var(--clair-ink)] focus:ring-2 focus:ring-[var(--clair-yellow)]/40"
      />
    </label>
  );
}

function BrandMark() {
  return (
    <Link href="/" className="motion-hover-lift inline-flex min-h-12 items-center rounded-full border border-black/20 bg-white/55 px-6 text-2xl font-semibold tracking-normal text-[var(--clair-ink)]" aria-label="CLAIR home">
      {APP_NAME}
    </Link>
  );
}

function UserPill({ user }: { user: User }) {
  return (
    <div
      role="group"
      aria-label={`Signed in as ${user.name}`}
      className="motion-hover-lift inline-flex h-12 items-center gap-3 rounded-full border border-black/10 bg-white/75 px-3 pr-4 shadow-sm"
    >
      <img src="/images/patient-portrait.jpg" alt="" className="h-8 w-8 rounded-full object-cover" />
      <span className="hidden leading-tight sm:block">
        <span className="block text-xs font-bold text-[var(--clair-ink)]">{user.name}</span>
        <span className="block text-[11px] font-semibold capitalize text-slate-500">{user.role.replace("_", " ")}</span>
      </span>
      <ChevronDown size={14} className="text-slate-500" />
    </div>
  );
}

function SessionSkeleton() {
  return <div className="h-11 w-32 animate-pulse rounded-full border border-black/10 bg-white/50" aria-label="Checking session" />;
}

function TopNavigation({
  view,
  currentUser,
  sessionChecked,
  onLogout,
  marketing = false,
}: {
  view: View;
  currentUser: User | null;
  sessionChecked: boolean;
  onLogout?: () => void;
  marketing?: boolean;
}) {
  return (
    <header className={`${APP_FRAME} motion-navbar relative z-10 flex flex-wrap items-center justify-between gap-4 rounded-full border border-black/15 bg-white/70 px-5 py-3 shadow-sm backdrop-blur md:flex-nowrap`}>
      <BrandMark />
      <nav className="order-3 flex w-full items-center justify-center gap-2 overflow-x-auto md:order-none md:w-auto" aria-label="Primary">
        {navItems.filter((item) => !marketing || item.view !== "emergency").map((item) => (
          <Link
            key={item.href}
            href={item.href}
            prefetch={false}
            className={`motion-hover-lift inline-flex h-10 shrink-0 items-center gap-2 rounded-full px-5 text-sm font-semibold transition ${
              item.view === view ? "bg-[var(--clair-ink)] text-white" : "text-slate-700 hover:bg-white/80 hover:text-[var(--clair-ink)]"
            }`}
          >
            {item.icon}
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="flex items-center gap-2">
        {!sessionChecked ? <SessionSkeleton /> : null}
        {sessionChecked && currentUser ? (
          <>
            <UserPill user={currentUser} />
            {onLogout ? (
              <Button variant="secondary" onClick={onLogout} className="px-4">
                <LogOut size={15} /> Logout
              </Button>
            ) : null}
          </>
        ) : null}
        {sessionChecked && !currentUser ? (
          <Link className="motion-hover-lift inline-flex min-h-10 items-center justify-center rounded-full bg-white px-5 py-2 text-sm font-semibold text-[var(--clair-ink)] shadow-sm transition hover:bg-[var(--clair-yellow)]" href="/login">
            Login
          </Link>
        ) : null}
      </div>
    </header>
  );
}

function Shell({
  view,
  children,
  currentUser,
  sessionChecked,
  onLogout,
}: {
  view: View;
  children: ReactNode;
  currentUser: User | null;
  sessionChecked: boolean;
  onLogout: () => void;
}) {
  return (
    <div className="min-h-dvh w-full p-2 text-[var(--clair-ink)]">
      <div className="clair-board min-h-[calc(100dvh-1rem)] w-full">
        <TopNavigation view={view} currentUser={currentUser} sessionChecked={sessionChecked} onLogout={onLogout} />
        <main
          key={view}
          className={`${APP_FRAME} motion-page mt-4 min-w-0`}
        >
          {children}
        </main>
      </div>
    </div>
  );
}

function Metric({ label, value, icon, tone = "white" }: { label: string; value: string; icon: ReactNode; tone?: "white" | "yellow" | "dark" }) {
  return (
    <Panel className={`${tone === "yellow" ? "!bg-[var(--clair-yellow)]" : tone === "dark" ? "!bg-[var(--clair-ink)] !text-white" : ""} min-h-28`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className={`text-sm font-semibold ${tone === "dark" ? "text-white/70" : "text-slate-500"}`}>{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-normal">{value}</p>
        </div>
        <span className={`grid h-11 w-11 place-items-center rounded-2xl ${tone === "dark" ? "bg-white/10 text-white" : "bg-white/65 text-[var(--clair-ink)]"}`}>{icon}</span>
      </div>
    </Panel>
  );
}

export default function ClairAppShell({ view }: { view: View }) {
  const router = useRouter();
  const [email, setEmail] = useState("patient@example.com");
  const [accessCode, setAccessCode] = useState("patient123");
  const [loginMessage, setLoginMessage] = useState("");
  const [triage, setTriage] = useState<TriageRequest>({ symptoms: "", duration: "", ageRange: "", riskFlags: [] });
  const [triageResult, setTriageResult] = useState<TriageResponse | null>(null);
  const [providers, setProviders] = useState<Provider[]>(DEMO_PROVIDERS);
  const [documentSummary, setDocumentSummary] = useState<DocumentSummaryResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("Secure demo session ready.");
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [sessionChecked, setSessionChecked] = useState(view === "home");

  const topProviders = useMemo(() => providers.slice(0, 3), [providers]);
  const protectedPath = protectedViewPaths[view];

  async function readSessionUser(): Promise<User | null> {
    try {
      const response = await fetch("/api/session");
      if (!response.ok) return null;
      const data = await response.json();
      return data?.user ?? null;
    } catch {
      return null;
    }
  }

  useEffect(() => {
    let active = true;
    setSessionChecked(false);
    readSessionUser().then((user) => {
      if (!active) return;
      setCurrentUser(user);
      setSessionChecked(true);
      if (!user && protectedPath) {
        router.replace(`/login?next=${encodeURIComponent(protectedPath)}`);
      }
    });

    return () => {
      active = false;
    };
  }, [protectedPath, router, view]);

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password: accessCode }),
    });
    setBusy(false);
    if (!response.ok) {
      setLoginMessage("The demo credentials did not match.");
      return;
    }
    const data = await response.json().catch(() => null);
    setCurrentUser(data?.user ?? null);
    setSessionChecked(true);
    setLoginMessage("");
    goAfterAuth();
  }

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" });
    setCurrentUser(null);
    setSessionChecked(true);
    setDocumentSummary(null);
    setSelectedFile(null);
    setTriageResult(null);
    setNotice("Signed out.");
    router.push("/login");
  }

  async function runTriage() {
    setBusy(true);
    const response = await fetch("/api/triage/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(triage),
    });
    const data = await response.json();
    setBusy(false);
    if (!response.ok) {
      setNotice(data.message || "Triage could not be completed.");
      return;
    }
    setTriageResult(data);
    const recommended = await fetch("/api/providers/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then((res) => res.json()).catch(() => ({ providers: [] }));
    if (Array.isArray(recommended.providers)) setProviders(recommended.providers);
  }

  async function uploadDocument() {
    if (!selectedFile) return;
    setBusy(true);
    setNotice("Summarizing document...");
    const form = new FormData();
    form.append("file", selectedFile);

    async function submitDocument() {
      return fetch("/api/documents/analyze", { method: "POST", body: form });
    }

    const response = await submitDocument();

    const data = await response.json().catch(() => ({ message: "Document analysis could not be completed." }));
    setBusy(false);
    if (!response.ok) {
      setDocumentSummary(null);
      if (response.status === 401) {
        setCurrentUser(null);
        setSessionChecked(true);
        setNotice("Please log in before summarizing documents.");
        router.push("/login?next=%2Fdocuments");
        return;
      }
      setNotice(data.message || "Document analysis could not be completed.");
      return;
    }
    setDocumentSummary(data as DocumentSummaryResponse);
    setNotice("Document summary generated.");
  }

  function onFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setDocumentSummary(null);
    setNotice(file ? `${file.name} is ready to summarize.` : "Choose a text-based PDF to summarize.");
  }

  if (view === "home" || view === "login") {
    return (
      <MotionConfig reducedMotion="user">
        <main className="min-h-dvh w-full p-2 text-[var(--clair-ink)] sm:p-3">
          <div className="clair-board min-h-[calc(100dvh-1.5rem)] w-full">
            <TopNavigation view="dashboard" currentUser={currentUser} sessionChecked={sessionChecked} onLogout={logout} />
            <section className={`${APP_FRAME} motion-page grid gap-6 py-7 lg:grid-cols-[minmax(0,1fr)_560px] lg:items-center`}>
              <div className="motion-card motion-card-delay-1 space-y-7">
                <div className="inline-flex items-center gap-2 rounded-full bg-white/75 px-4 py-2 text-sm font-semibold shadow-sm">
                  <ShieldCheck size={16} /> Premium healthcare AI workspace
                </div>
                <div className="space-y-4">
                  <h1 className="max-w-4xl text-5xl font-semibold leading-[0.95] tracking-normal text-[var(--clair-ink)] lg:text-7xl">
                    Clinical AI Navigation Platform
                  </h1>
                  <p className="max-w-3xl text-xl leading-8 text-slate-600">
                    One secure page for login, symptom triage, provider routing, document intelligence, and session-first privacy.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <Link href="/triage" prefetch={false} className="motion-hover-lift inline-flex min-h-12 items-center justify-center gap-2 rounded-full bg-[var(--clair-yellow)] px-7 py-3 text-sm font-bold text-[var(--clair-ink)] transition hover:bg-[#ffd33d]">
                    Start Symptom Check <ArrowRight size={17} />
                  </Link>
                  <Link href="/documents" prefetch={false} className="motion-hover-lift inline-flex min-h-12 items-center justify-center gap-2 rounded-full bg-white px-7 py-3 text-sm font-bold text-[var(--clair-ink)] shadow-sm transition hover:bg-slate-50">
                    Upload Document
                  </Link>
                </div>
                <div className="grid max-w-4xl gap-4 sm:grid-cols-3">
                  <WorkflowChip tone="mint" number="1" title="Patient Input" />
                  <WorkflowChip tone="yellow" number="2" title="AI Triage" />
                  <WorkflowChip tone="dark" number="3" title="Provider Match" />
                </div>
              </div>
              <Panel className="motion-card-delay-2 min-h-[560px]">
                <div className="mb-6 flex items-center gap-3">
                  <span className="grid h-12 w-12 place-items-center rounded-2xl bg-[var(--clair-ink)] text-white"><Lock size={20} /></span>
                  <div>
                    <h2 className="text-3xl font-semibold">Login to CLAIR</h2>
                    <p className="text-sm text-slate-500">Use demo access to enter the healthcare AI web platform.</p>
                  </div>
                </div>
                <div className="grid gap-4">
                  {sessionChecked && currentUser ? (
                    <div className="rounded-3xl border border-emerald-200 bg-emerald-50/85 p-4">
                      <UserPill user={currentUser} />
                      <p className="mt-3 text-sm text-slate-700">You are already signed in. You can continue, log out, or sign in again below.</p>
                    </div>
                  ) : null}
                  <form className="grid gap-4" onSubmit={login}>
                    <Field label="Email" value={email} onChange={setEmail} />
                    <Field label="Access code" value={accessCode} onChange={setAccessCode} type="password" />
                    {loginMessage ? <p className="text-sm font-semibold text-red-700">{loginMessage}</p> : null}
                    <Button type="submit" disabled={busy} className="mt-2 w-full"><UserRoundCheck size={17} />Login</Button>
                  </form>
                  {sessionChecked && currentUser ? (
                    <div className="grid gap-3 sm:grid-cols-2">
                      <Button onClick={goAfterAuth} className="w-full"><UserRoundCheck size={17} />Continue</Button>
                      <Button variant="secondary" onClick={logout} className="w-full"><LogOut size={16} />Logout</Button>
                    </div>
                  ) : null}
                  <div className="rounded-3xl bg-[var(--clair-mint)]/70 p-4 text-sm">
                    <p className="font-bold">Demo Credentials</p>
                    <p className="text-slate-600">patient@example.com / patient123</p>
                  </div>
                  <p className="text-sm text-slate-500">No public signup in Release 1. Documents stay in memory only.</p>
                </div>
              </Panel>
            </section>
          </div>
        </main>
      </MotionConfig>
    );
  }

  if (protectedPath && (!sessionChecked || !currentUser)) {
    return (
      <MotionConfig reducedMotion="user">
        <Shell view={view} currentUser={currentUser} sessionChecked={sessionChecked} onLogout={logout}>
          <div className="grid min-h-[620px] place-items-center">
            <Panel className="motion-card-delay-1 max-w-xl text-center">
              <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-[var(--clair-yellow)]">
                <Lock size={24} />
              </div>
              <h1 className="mt-5 text-4xl font-semibold">Secure session required</h1>
              <p className="mt-3 text-slate-600">
                {sessionChecked ? "Redirecting to login..." : "Checking your CLAIR session..."}
              </p>
              <Link
                href={`/login?next=${encodeURIComponent(protectedPath)}`}
                prefetch={false}
                className="motion-hover-lift mt-6 inline-flex min-h-11 items-center justify-center rounded-full bg-[var(--clair-ink)] px-6 py-2 text-sm font-semibold text-white"
              >
                Go to login
              </Link>
            </Panel>
          </div>
        </Shell>
      </MotionConfig>
    );
  }

  return (
    <MotionConfig reducedMotion="user">
      <Shell view={view} currentUser={currentUser} sessionChecked={sessionChecked} onLogout={logout}>
        {view === "dashboard" ? (
          <DashboardScreen providers={topProviders} />
        ) : null}

        {view === "triage" ? (
          <TriageScreen triage={triage} setTriage={setTriage} busy={busy} runTriage={runTriage} triageResult={triageResult} />
        ) : null}

        {view === "navigator" ? <NavigatorScreen providers={providers} /> : null}

        {view === "documents" ? (
          <DocumentsScreen
            selectedFile={selectedFile}
            onFile={onFile}
            busy={busy}
            uploadDocument={uploadDocument}
            documentSummary={documentSummary}
            notice={notice}
          />
        ) : null}

        {view === "emergency" ? <EmergencyScreen /> : null}

        {view === "safety" ? <SafetyScreen currentUser={currentUser} onLogout={logout} /> : null}
      </Shell>
    </MotionConfig>
  );
}

function WorkflowChip({ number, title, tone }: { number: string; title: string; tone: "mint" | "yellow" | "dark" }) {
  const chipTone = {
    mint: "border-emerald-200 bg-emerald-50/90 text-[var(--clair-deep)] shadow-[0_16px_34px_rgba(6,59,54,0.10)]",
    yellow: "border-yellow-300 bg-yellow-100/90 text-[var(--clair-ink)] shadow-[0_16px_34px_rgba(120,92,0,0.10)]",
    dark: "border-black/20 bg-[#242424] text-white shadow-[0_16px_34px_rgba(20,20,20,0.18)]",
  }[tone];
  const numberTone = {
    mint: "bg-[var(--clair-mint)] text-[var(--clair-ink)]",
    yellow: "bg-[var(--clair-yellow)] text-[var(--clair-ink)]",
    dark: "bg-white/15 text-[var(--clair-mint)]",
  }[tone];
  const detailTone = tone === "dark" ? "text-white/70" : "text-slate-600";

  return (
    <div className={`motion-card motion-hover-lift flex items-center gap-3 rounded-3xl border p-4 ${chipTone}`}>
      <span className={`grid h-12 w-12 place-items-center rounded-full text-xl font-bold ${numberTone}`}>{number}</span>
      <div>
        <p className="font-semibold">{title}</p>
        <p className={`text-sm ${detailTone}`}>Realtime safe workflow</p>
      </div>
    </div>
  );
}

function TrustRow({ title, detail, tone }: { title: string; detail: string; tone: "mint" | "yellow" | "dark" }) {
  const rowTone = {
    mint: "border-emerald-200/80 bg-emerald-50/85 text-[var(--clair-deep)] shadow-[0_18px_36px_rgba(6,59,54,0.10)]",
    yellow: "border-yellow-300/70 bg-yellow-100/80 text-[var(--clair-ink)] shadow-[0_18px_36px_rgba(120,92,0,0.10)]",
    dark: "border-black/20 bg-[#242424] text-white shadow-[0_18px_36px_rgba(20,20,20,0.16)]",
  }[tone];
  const iconTone = {
    mint: "bg-[var(--clair-mint)] text-[var(--clair-ink)]",
    yellow: "bg-[var(--clair-yellow)] text-[var(--clair-ink)]",
    dark: "bg-white/15 text-[var(--clair-mint)]",
  }[tone];
  const detailTone = tone === "dark" ? "text-white/70" : "text-slate-600";

  return (
    <div className={`motion-card motion-hover-lift flex items-center gap-4 rounded-3xl border p-5 ${rowTone}`}>
      <span className={`grid h-12 w-12 place-items-center rounded-full ${iconTone}`}><Check size={18} /></span>
      <div>
        <p className="text-xl font-semibold">{title}</p>
        <p className={`text-sm ${detailTone}`}>{detail}</p>
      </div>
    </div>
  );
}

function DashboardScreen({ providers }: { providers: Provider[] }) {
  return (
    <div className="motion-page grid gap-4">
      <section className="grid gap-3">
        <div className="grid gap-2 xl:grid-cols-[1fr_auto] xl:items-end">
          <div>
            <h1 className="text-4xl font-normal leading-tight tracking-normal text-[var(--clair-ink)] 2xl:text-5xl">Welcome in, Maya</h1>
            <p className="mt-2 max-w-3xl text-base text-slate-600">
              CLAIR is ready to explain your blood report, highlight important markers, and prepare doctor questions.
            </p>
          </div>
          <div className="rounded-full bg-white/35 px-6 py-3 text-sm font-semibold text-slate-700 backdrop-blur">
            Blood Test PDF analysis ready
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <StatusStripItem label="Triage Status" value="Ready" tone="dark" icon={<HeartPulse size={17} />} delayClass="motion-card-delay-1" />
          <StatusStripItem label="Uploaded Reports" value="1 PDF" tone="yellow" icon={<FileText size={17} />} delayClass="motion-card-delay-1" />
          <StatusStripItem label="Provider Matches" value={`${providers.length}`} icon={<MapPin size={17} />} delayClass="motion-card-delay-2" />
          <StatusStripItem label="Safety Status" value="Emergency Monitor Active" tone="mint" icon={<ShieldAlert size={17} />} delayClass="motion-card-delay-2" />
          <StatusStripItem label="Document Privacy" value="In-memory only" icon={<ShieldCheck size={17} />} delayClass="motion-card-delay-3" />
        </div>
      </section>

      <section className="dashboard-grid">
        <PatientHealthProfileCard className="dashboard-profile" />
        <BloodReportOverview className="dashboard-overview" />
        <DocumentIntelligenceCard className="dashboard-document" />
        <PlainLanguageSummaryCard className="dashboard-summary" />
        <QuestionsForDoctorCard className="dashboard-questions" />
        <CriticalIndicatorsCard className="dashboard-critical" />
        <RecommendedNextActionsCard className="dashboard-actions" />
        <ClairCareJourneyCard className="dashboard-journey" />
      </section>

      <DashboardSafetyNotice />
    </div>
  );
}

function StatusStripItem({
  label,
  value,
  icon,
  tone = "white",
  delayClass = "",
}: {
  label: string;
  value: string;
  icon: ReactNode;
  tone?: "white" | "yellow" | "dark" | "mint";
  delayClass?: string;
}) {
  const toneClass = {
    dark: "bg-[var(--clair-ink)] text-white",
    yellow: "bg-[var(--clair-yellow)] text-[var(--clair-ink)]",
    mint: "bg-[var(--clair-mint)]/75 text-[var(--clair-ink)]",
    white: "border border-black/10 bg-white/45 text-[var(--clair-ink)]",
  }[tone];

  return (
    <div className={`motion-status-card ${delayClass} flex min-h-20 items-center gap-3 rounded-[1.75rem] px-4 py-3 shadow-sm backdrop-blur ${toneClass}`}>
      <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-full ${tone === "dark" ? "bg-white/10 text-white" : "bg-white/65 text-[var(--clair-ink)]"}`}>
        {icon}
      </span>
      <div className="min-w-0">
        <p className={`text-xs font-semibold ${tone === "dark" ? "text-white/65" : "text-slate-500"}`}>{label}</p>
        <p className="mt-1 text-base font-bold leading-tight">{value}</p>
      </div>
    </div>
  );
}

function PatientHealthProfileCard({ className = "" }: { className?: string }) {
  return (
    <Panel className={`motion-card-delay-1 overflow-hidden !p-0 ${className}`}>
      <div className="relative h-40 overflow-hidden 2xl:h-44">
        <img src="/images/patient-portrait.jpg" alt="Patient profile" className="h-full w-full object-cover object-[50%_24%]" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/35 via-transparent to-transparent" />
        <div className="absolute left-4 right-4 top-4 flex items-center justify-between gap-3">
          <span className="rounded-full bg-white/85 px-4 py-2 text-xs font-bold text-[var(--clair-ink)] backdrop-blur">Patient Health Workspace</span>
          <span className="motion-pulse rounded-full bg-[var(--clair-yellow)] px-4 py-2 text-xs font-bold text-[var(--clair-ink)]">Analysis Ready</span>
        </div>
      </div>
      <div className="p-3.5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-[1.6rem] font-semibold leading-tight">Maya Rao</p>
            <p className="mt-1 text-sm text-slate-500">Secure demo session</p>
          </div>
          <span className="rounded-full bg-[var(--clair-mint)] px-4 py-2 text-sm font-bold text-[var(--clair-ink)]">Ready</span>
        </div>
        <div className="mt-3 grid gap-2 text-sm">
          <PatientFact label="Last report uploaded" value="Blood Test PDF" />
          <PatientFact label="Report date" value="Oct 24, 2024" />
          <PatientFact label="Document status" value="Plain-language analysis ready" />
        </div>
      </div>
    </Panel>
  );
}

function PatientFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="motion-row flex items-center justify-between gap-4 rounded-2xl bg-white/55 px-3.5 py-2">
      <span className="text-slate-500">{label}</span>
      <span className="text-right font-bold">{value}</span>
    </div>
  );
}

function safeNextPath() {
  if (typeof window === "undefined") return "/dashboard";
  const value = new URLSearchParams(window.location.search).get("next");
  if (!value || !value.startsWith("/") || value.startsWith("//")) return "/dashboard";
  return value;
}

function SafetyDisclaimer({ className = "" }: { className?: string }) {
  return (
    <div className={`rounded-2xl border border-black/10 bg-white/55 p-3 text-xs leading-5 text-slate-600 ${className}`}>
      <p>CLAIR provides plain-language document explanation only. It does not diagnose, prescribe treatment, or replace a licensed clinician.</p>
      <p className="mt-1 font-semibold text-slate-700">Documents are processed in memory only and are not retained.</p>
    </div>
  );
}

function DashboardSafetyNotice() {
  return (
    <div className="motion-card motion-card-delay-3 flex flex-col gap-2 rounded-[1.5rem] border border-black/10 bg-white/45 px-5 py-3 text-xs leading-5 text-slate-600 shadow-sm backdrop-blur md:flex-row md:items-center md:justify-between">
      <span>CLAIR provides plain-language document explanation only. It does not diagnose, prescribe treatment, or replace a licensed clinician.</span>
      <span className="font-semibold text-slate-700">Documents are processed in memory only and are not retained.</span>
    </div>
  );
}

function BloodReportOverview({ className = "" }: { className?: string }) {
  return (
    <Panel className={`motion-card-delay-1 ${className}`}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-normal 2xl:text-3xl">Blood Report Overview</h2>
          <p className="mt-2 text-sm text-slate-500">Overall status</p>
          <p className="mt-1 text-3xl font-light 2xl:text-4xl">Mostly Stable</p>
        </div>
        <span className="rounded-full bg-[var(--clair-mint)] px-4 py-2.5 text-sm font-bold text-[var(--clair-ink)]">Not an emergency</span>
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_1fr]">
        <div>
          <p className="mb-3 text-sm font-bold text-slate-600">Needs attention</p>
          <div className="grid gap-2">
            <FindingRow label="LDL Cholesterol" value="132 mg/dL" tone="attention" />
            <FindingRow label="CRP" value="3.2 mg/L" tone="attention" />
            <FindingRow label="Vitamin D" value="Low" tone="warning" />
          </div>
        </div>
        <div>
          <p className="mb-3 text-sm font-bold text-slate-600">Normal</p>
          <div className="grid gap-2">
            <FindingRow label="Glucose" value="95 mg/dL" tone="normal" />
            <FindingRow label="HbA1c" value="5.4%" tone="normal" />
          </div>
        </div>
      </div>
      <div className="mt-5">
        <div className="motion-progress flex h-8 overflow-hidden rounded-full bg-white/65 2xl:h-9">
          <div className="motion-progress-fill w-[42%] bg-emerald-500" />
          <div className="motion-progress-fill motion-progress-delay-1 w-[36%] bg-amber-400" />
          <div className="motion-progress-fill motion-progress-delay-2 w-[22%] bg-orange-500" />
        </div>
        <div className="mt-3 grid grid-cols-3 gap-2 text-xs font-semibold text-slate-600">
          <span>Normal</span>
          <span className="text-center">Attention</span>
          <span className="text-right">Follow-up</span>
        </div>
      </div>
    </Panel>
  );
}

function FindingRow({ label, value, tone }: { label: string; value: string; tone: "attention" | "warning" | "normal" }) {
  const toneClass = {
    attention: "bg-orange-100 text-orange-800",
    warning: "bg-red-100 text-red-700",
    normal: "bg-emerald-100 text-emerald-800",
  }[tone];

  return (
    <div className="motion-row flex items-center justify-between gap-3 rounded-2xl bg-white/55 px-3 py-2">
      <span className="font-semibold">{label}</span>
      <span className={`rounded-full px-3 py-1 text-sm font-bold ${toneClass}`}>{value}</span>
    </div>
  );
}

function DocumentIntelligenceCard({ className = "" }: { className?: string }) {
  return (
    <Panel className={`motion-card-delay-1 ${className}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-2xl font-normal 2xl:text-3xl">Document Intelligence</h2>
          <p className="mt-2 text-sm text-slate-500">Blood report extraction complete</p>
        </div>
        <span className="grid h-12 w-12 place-items-center rounded-full bg-white/75"><FileText size={18} /></span>
      </div>
      <div className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
        <DocumentFact label="Uploaded file" value="blood_report.pdf" />
        <DocumentFact label="File type" value="Text-based PDF" />
        <DocumentFact label="File size" value="Under 4 MB" />
        <DocumentFact label="Processing mode" value="In-memory only" />
        <DocumentFact label="AI extraction status" value="Complete" />
        <DocumentFact label="Summary target" value="Plain language" />
      </div>
      <Link href="/documents" className="motion-hover-lift mt-4 inline-flex min-h-10 items-center justify-center gap-2 rounded-full bg-[var(--clair-ink)] px-5 py-2 text-sm font-bold text-white transition hover:bg-black">
        View Full Summary <ArrowRight size={16} />
      </Link>
    </Panel>
  );
}

function DocumentFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="motion-row grid gap-1 rounded-2xl bg-white/55 px-3 py-2">
      <span className="text-xs font-semibold text-slate-500">{label}</span>
      <span className="font-bold leading-tight">{value}</span>
    </div>
  );
}

function CriticalIndicatorsCard({ className = "" }: { className?: string }) {
  return (
    <Panel className={`motion-card-delay-2 ${className}`}>
      <h2 className="text-2xl font-normal 2xl:text-3xl">Critical Indicators</h2>
      <div className="mt-4 grid gap-2">
        <IndicatorRow label="LDL Cholesterol" value="132 mg/dL" status="High" tone="orange" />
        <IndicatorRow label="CRP" value="3.2 mg/L" status="Elevated" tone="orange" />
        <IndicatorRow label="Vitamin D" value="Low" status="Low" tone="red" />
        <IndicatorRow label="Blood Sugar" value="95 mg/dL" status="Normal" tone="green" />
      </div>
    </Panel>
  );
}

function IndicatorRow({
  label,
  value,
  status,
  tone,
}: {
  label: string;
  value: string;
  status: string;
  tone: "orange" | "red" | "green";
}) {
  const toneClass = {
    orange: "bg-orange-100 text-orange-800",
    red: "bg-red-100 text-red-700",
    green: "bg-emerald-100 text-emerald-800",
  }[tone];

  return (
    <div className="rounded-2xl bg-white/55 px-3 py-2">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="font-bold leading-tight">{label}</p>
          <p className="text-xs text-slate-500">{value}</p>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-xs font-bold ${toneClass}`}>{status}</span>
      </div>
      <div className="motion-progress mt-2 h-1.5 overflow-hidden rounded-full bg-white">
        <div className={`motion-progress-fill h-full rounded-full ${tone === "green" ? "w-[45%] bg-emerald-500" : tone === "red" ? "w-[82%] bg-red-500" : "w-[72%] bg-orange-500"}`} />
      </div>
    </div>
  );
}

function QuestionsForDoctorCard({ className = "" }: { className?: string }) {
  const questions = [
    "Is my LDL level high enough to require medication or lifestyle changes?",
    "Could elevated CRP suggest inflammation that needs further testing?",
    "Should I repeat Vitamin D or lipid testing in 90 days?",
  ];

  return (
    <Panel className={`motion-card-delay-2 ${className}`}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-normal 2xl:text-3xl">Questions for Doctor</h2>
          <p className="mt-2 text-sm text-slate-500">Use these during your next primary care visit.</p>
        </div>
        <Link href="/documents" className="motion-hover-lift inline-flex min-h-10 items-center justify-center gap-2 rounded-full bg-[var(--clair-yellow)] px-5 py-2 text-sm font-bold text-[var(--clair-ink)] transition hover:bg-[#ffd33d]">
          Prepare Visit Notes
        </Link>
      </div>
      <ol className="mt-4 grid gap-2">
        {questions.map((question, index) => (
          <li key={question} className="motion-row flex gap-3 rounded-2xl bg-white/55 p-2.5">
            <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-[var(--clair-ink)] text-sm font-bold text-white">{index + 1}</span>
            <span className="text-sm font-semibold leading-6 text-[var(--clair-ink)]">"{question}"</span>
          </li>
        ))}
      </ol>
    </Panel>
  );
}

function ClairCareJourneyCard({ className = "" }: { className?: string }) {
  const steps = [
    ["Upload PDF", "Completed", "done"],
    ["Understand Report", "Completed", "done"],
    ["Review Key Findings", "Active", "active"],
    ["Ask Doctor Questions", "Pending", "pending"],
    ["Run Symptom Triage", "Optional", "optional"],
    ["Find Provider", "Optional", "optional"],
  ] as const;

  return (
    <DarkPanel className={`motion-card-delay-3 !p-5 ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-normal">CLAIR Care Journey</h2>
          <p className="mt-1 text-sm text-white/55">Patient document-to-care path</p>
        </div>
        <span className="text-4xl font-light">3/6</span>
      </div>
      <div className="mt-5 grid gap-2.5 sm:grid-cols-2">
        {steps.map(([title, detail, state], index) => (
          <div key={title} className="motion-journey-step flex items-center gap-3 rounded-2xl bg-white/[0.04] p-2" style={{ "--motion-delay": `${160 + index * 70}ms` } as CSSProperties}>
            <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-full ${
              state === "done" ? "bg-[var(--clair-yellow)] text-[var(--clair-ink)]" : state === "active" ? "bg-[var(--clair-mint)] text-[var(--clair-ink)]" : "bg-white/10 text-white/60"
            }`}>
              {state === "done" ? <Check size={16} /> : state === "active" ? <Sparkles size={16} /> : <FileText size={16} />}
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold leading-tight">{title}</p>
              <p className="text-xs text-white/45">{detail}</p>
            </div>
            <span className={`h-3.5 w-3.5 shrink-0 rounded-full ${state === "done" ? "motion-pulse bg-[var(--clair-yellow)]" : state === "active" ? "motion-pulse bg-[var(--clair-mint)]" : "bg-white/15"}`} />
          </div>
        ))}
      </div>
    </DarkPanel>
  );
}

function PlainLanguageSummaryCard({ className = "" }: { className?: string }) {
  return (
    <Panel className={`motion-card-delay-2 ${className}`}>
      <h2 className="text-2xl font-normal 2xl:text-3xl">Plain-Language Summary</h2>
      <p className="mt-3 text-base leading-7 text-slate-700">
        Your blood report is mostly stable. Some markers related to cholesterol and inflammation are above the preferred range. These are not emergency findings, but they should be discussed with a doctor.
      </p>
      <div className="mt-4 rounded-2xl bg-[var(--clair-mint)]/70 p-3 text-sm font-semibold text-[var(--clair-ink)]">
        Emergency status: no emergency signals detected in this report summary.
      </div>
    </Panel>
  );
}

function RecommendedNextActionsCard({ className = "" }: { className?: string }) {
  const actions = [
    "Schedule follow-up with primary care physician",
    "Discuss lipid panel and CRP result",
    "Continue monitoring blood sugar",
    "Ask if Vitamin D supplementation is needed",
  ];

  return (
    <Panel className={`motion-card-delay-3 ${className}`}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-normal 2xl:text-3xl">Recommended Next Actions</h2>
          <p className="mt-2 text-sm text-slate-500">Non-urgent steps to discuss with a clinician.</p>
        </div>
        <Link href="/navigator" className="motion-hover-lift inline-flex min-h-10 items-center justify-center gap-2 rounded-full bg-[var(--clair-yellow)] px-5 py-2 text-sm font-bold text-[var(--clair-ink)] transition hover:bg-[#ffd33d]">
          Find a Provider <ArrowRight size={16} />
        </Link>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {actions.map((action) => (
          <div key={action} className="motion-row flex items-center gap-3 rounded-2xl bg-white/55 p-3">
            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-[var(--clair-mint)] text-[var(--clair-ink)]"><Check size={16} /></span>
            <span className="font-semibold leading-6">{action}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function TriageScreen({
  triage,
  setTriage,
  busy,
  runTriage,
  triageResult,
}: {
  triage: TriageRequest;
  setTriage: (updater: (current: TriageRequest) => TriageRequest) => void;
  busy: boolean;
  runTriage: () => void;
  triageResult: TriageResponse | null;
}) {
  return (
    <div className="motion-page grid gap-5">
      <div>
        <h1 className="text-5xl font-semibold">Symptom Triage Dashboard</h1>
        <p className="mt-2 text-lg text-slate-600">Clinical guidance only - no diagnosis. 16:9 web app workspace.</p>
      </div>
      <div className="grid gap-5 lg:grid-cols-[1.1fr_390px_320px]">
        <Panel className="motion-card-delay-1">
          <h2 className="text-3xl font-semibold">Clinical Assistant</h2>
          <p className="text-slate-500">Active session - Exchange 3 of 6</p>
          <label className="mt-6 grid gap-2 text-sm font-semibold text-slate-700">
            <span>Symptoms</span>
            <textarea
              aria-label="Symptoms"
              value={triage.symptoms}
              onChange={(event) => setTriage((current) => ({ ...current, symptoms: event.target.value }))}
              className="min-h-40 rounded-3xl border border-black/10 bg-white/70 p-4 outline-none focus:border-[var(--clair-ink)] focus:ring-2 focus:ring-[var(--clair-yellow)]/40"
              placeholder="Describe your symptoms and how long they have been occurring."
            />
          </label>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <Field label="Duration" value={triage.duration || ""} onChange={(value) => setTriage((current) => ({ ...current, duration: value }))} placeholder="2 days" />
            <Field label="Age range" value={triage.ageRange || ""} onChange={(value) => setTriage((current) => ({ ...current, ageRange: value }))} placeholder="35-44" />
          </div>
          <div className="mt-5 flex flex-wrap items-center gap-3">
            <Button onClick={runTriage} disabled={busy}><Sparkles size={17} />Analyze symptoms</Button>
            <span className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-500">{busy ? "Analyzing symptoms..." : "Emergency phrase scan active"}</span>
          </div>
        </Panel>
        <Panel className="motion-card-delay-2">
          <h2 className="text-3xl font-semibold">AI Triage Result</h2>
          {triageResult ? (
            <div className="mt-5 grid gap-4">
              <span className="rounded-full bg-[var(--clair-mint)] px-5 py-3 text-center font-semibold">{triageResult.urgencyLevel}</span>
              <ResultRow label="Suggested Specialty" value={triageResult.suggestedSpecialty} />
              <DarkPanel className="!p-4 motion-card-delay-2">
                <p className="text-sm text-white/65">Next Step</p>
                <p className="mt-1 text-2xl font-semibold">{triageResult.nextStepRecommendation}</p>
              </DarkPanel>
              <span className="rounded-full bg-white px-4 py-2 text-center text-sm font-semibold text-slate-700">
                {triageResult.source === "openai" ? "OpenAI triage agent completed" : "Demo safety fallback used - add OPENAI_API_KEY for live AI"}
              </span>
              <p className="rounded-3xl bg-red-50 p-3 text-sm font-semibold text-red-800">{triageResult.disclaimer}</p>
            </div>
          ) : (
            <div className="mt-6 rounded-3xl bg-white/70 p-5 text-slate-600">Run triage to see urgency, specialty, and next step guidance.</div>
          )}
        </Panel>
        <DarkPanel className="motion-card-delay-3">
          <h2 className="text-3xl font-semibold">Safety Monitor</h2>
          <div className="mt-6 grid gap-5">
            {["No diagnosis generated", "Emergency phrase scan active", "Disclaimer locked", "6-exchange limit enforced"].map((item) => (
              <div key={item} className="motion-row flex items-center gap-3 text-white/85">
                <span className="grid h-8 w-8 place-items-center rounded-full bg-[var(--clair-mint)] text-[var(--clair-ink)]"><Check size={15} /></span>
                <span>{item}</span>
              </div>
            ))}
          </div>
          <div className="mt-8 rounded-3xl bg-white p-5 text-[var(--clair-ink)]">
            <p className="font-semibold">Emergency Watch</p>
            <p className="mt-2 text-sm text-slate-500">Chest pain, cannot breathe, severe bleeding, suicidal intent.</p>
          </div>
        </DarkPanel>
      </div>
      <div className="motion-card motion-card-delay-3 rounded-full border border-red-200 bg-red-50 px-5 py-3 text-sm font-semibold text-red-800">
        MEDICAL DISCLAIMER: CLAIR provides navigation guidance only. It does not diagnose or replace emergency services.
      </div>
    </div>
  );
}

function NavigatorScreen({ providers }: { providers: Provider[] }) {
  return (
    <div className="motion-page grid gap-5">
      <div>
        <h1 className="text-5xl font-semibold">Care Navigator</h1>
        <p className="mt-2 inline-flex rounded-2xl bg-[var(--clair-mint)] px-5 py-3 font-semibold">Provider data is curated for demonstration purposes.</p>
      </div>
      <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
        <Panel className="motion-card-delay-1">
          <h2 className="text-2xl font-semibold">Smart Filters</h2>
          {[
            ["Specialty", "Dermatology"],
            ["Urgency", "Primary Care"],
            ["Distance", "Within 5 miles"],
            ["Availability", "This week"],
          ].map(([label, value]) => (
            <div key={label} className="mt-5">
              <p className="text-sm font-semibold text-slate-500">{label}</p>
              <div className="motion-row mt-2 rounded-2xl border border-black/10 bg-white/70 px-4 py-3">{value}</div>
            </div>
          ))}
        </Panel>
        <div className="grid gap-5">
          <div className="grid gap-4 lg:grid-cols-3">
            {providers.slice(0, 3).map((provider, index) => (
              <ProviderCard key={provider.id} provider={provider} index={index} />
            ))}
          </div>
          <DarkPanel className="motion-card-delay-3 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-3xl font-semibold">Selected Provider Detail</h2>
              <p className="mt-2 text-lg text-white/75">Next available: Tomorrow 10:30 AM - Specialty match: 96% - Route: Primary Care to Dermatology</p>
            </div>
            <Button variant="yellow">Confirm Visit</Button>
          </DarkPanel>
        </div>
      </div>
    </div>
  );
}

function ProviderCard({ provider, index }: { provider: Provider; index: number }) {
  return (
    <Panel className={index === 0 ? "motion-card-delay-1" : index === 1 ? "motion-card-delay-2" : "motion-card-delay-3"}>
      <div className="flex items-start gap-4">
        <img src={index === 0 ? "/images/doctor-portrait.jpg" : "/images/care-team.jpg"} alt="" className="h-16 w-16 rounded-3xl object-cover" />
        <div>
          <h2 className="text-2xl font-semibold">{provider.name}</h2>
          <p className="text-slate-500">{provider.specialty}</p>
        </div>
      </div>
      <div className="mt-8 grid gap-4 text-sm text-slate-600">
        <p className="font-semibold text-[var(--clair-ink)]">Rating {provider.rating.toFixed(1)} / 5 | 128 reviews</p>
        <p>Metropolitan Care District</p>
        <p>+1 (555) 234-8901</p>
        <div className="flex items-center justify-between pt-2">
          <span className={`font-semibold ${provider.acceptingPatients ? "text-emerald-700" : "text-red-600"}`}>{provider.acceptingPatients ? "Accepting" : "Waitlist"}</span>
          <Button className="px-5">Book Visit</Button>
        </div>
      </div>
    </Panel>
  );
}

function DocumentsScreen({
  selectedFile,
  onFile,
  busy,
  uploadDocument,
  documentSummary,
  notice,
}: {
  selectedFile: File | null;
  onFile: (event: ChangeEvent<HTMLInputElement>) => void;
  busy: boolean;
  uploadDocument: () => void;
  documentSummary: DocumentSummaryResponse | null;
  notice: string;
}) {
  return (
    <div className="motion-page grid gap-5">
      <div>
        <h1 className="text-5xl font-semibold">Document Intelligence</h1>
        <p className="mt-2 text-lg text-slate-600">Plain-language explanation for text-based PDFs up to 4 MB. Processed in memory only.</p>
      </div>
      <div className="grid items-start gap-5 lg:grid-cols-[290px_minmax(0,1fr)_430px]">
        <Panel className="motion-card-delay-1 self-start text-center">
          <div className="mx-auto grid h-24 w-24 place-items-center rounded-full bg-[var(--clair-mint)] text-[var(--clair-ink)]"><Upload size={34} /></div>
          <h2 className="mt-4 text-3xl font-semibold">Upload PDF</h2>
          <p className="mt-3 text-slate-600">Upload a real text-based medical PDF. CLAIR reads the text and analyzes that report only.</p>
          <div className="mt-6 text-left text-sm font-semibold text-slate-700">
            <label id="document-upload-label" htmlFor="document-upload" className="flex cursor-pointer items-center gap-2"><Upload size={16} /> PDF file</label>
            <div className="motion-hover-lift relative mt-2 flex min-h-12 cursor-pointer overflow-hidden rounded-full border border-black/10 bg-white/70 text-sm text-slate-700 shadow-sm transition focus-within:ring-2 focus-within:ring-[var(--clair-yellow)]/70">
              <span className="grid shrink-0 place-items-center bg-[var(--clair-ink)] px-5 font-bold text-white">
                Choose PDF
              </span>
              <span className="grid min-w-0 flex-1 place-items-center px-4 text-left">
                <span className="max-w-full truncate">{selectedFile ? selectedFile.name : "No file selected"}</span>
              </span>
              <input
                id="document-upload"
                name="file"
                aria-label="Choose PDF"
                title="Choose PDF"
                className="absolute inset-0 z-10 h-full w-full cursor-pointer opacity-0"
                type="file"
                accept=".pdf,application/pdf"
                onChange={onFile}
              />
            </div>
          </div>
          <p className="mt-3 break-words text-sm text-slate-600">{selectedFile ? `${selectedFile.name} selected.` : "Choose one text-based PDF from your laptop."}</p>
          <Button onClick={uploadDocument} disabled={busy || !selectedFile} className="mt-5 w-full"><FileText size={17} />{busy ? "Analyzing report..." : "Analyze real report"}</Button>
          <div className="mt-6 rounded-3xl bg-[var(--clair-mint)] p-4 text-sm font-semibold">Documents are processed in memory only and are not retained.</div>
        </Panel>
        <div className="grid content-start items-start gap-5">
          <Panel className="motion-card-delay-2 self-start">
            <h2 className="text-3xl font-semibold">Plain-language Summary</h2>
            <p className="mt-4 text-lg leading-8 text-slate-700" aria-live="polite">
              {documentSummary ? documentSummary.plainLanguageSummary : notice}
            </p>
            {documentSummary ? (
              <div className="mt-5 grid gap-3">
                <div className="inline-flex w-fit rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-700">
                  {documentSourceLabel(documentSummary.source)}
                </div>
                {documentSummary.warning ? <p className="rounded-2xl bg-amber-100 px-4 py-3 text-sm font-semibold text-amber-800">{documentSummary.warning}</p> : null}
              </div>
            ) : null}
          </Panel>
          <div className="grid items-start gap-5 md:grid-cols-2">
            <Panel className="motion-card-delay-3 self-start">
              <List title="Key Findings" items={documentSummary?.keyFindings ?? ["Upload a real text-based PDF report to extract findings.", "OpenAI analysis runs when OPENAI_API_KEY is configured."]} />
            </Panel>
            <DarkPanel className="motion-card-delay-3 self-start">
              <List title="Action Items" items={documentSummary?.actionItems ?? ["Choose a PDF from your laptop.", "Click Analyze real report.", "Review the extracted summary with a licensed clinician."]} />
            </DarkPanel>
          </div>
        </div>
        <DocumentResultPanel documentSummary={documentSummary} />
      </div>
    </div>
  );
}

function documentSourceLabel(source: AiResponseSource) {
  if (source === "openai") return "OpenAI document agent completed";
  if (source === "local_analysis") return "Local report extraction used - add OPENAI_API_KEY for OpenAI review";
  return "Demo fallback used - add OPENAI_API_KEY for live AI";
}

function DocumentResultPanel({ documentSummary }: { documentSummary: DocumentSummaryResponse | null }) {
  const indicators = documentSummary?.criticalIndicators?.length ? documentSummary.criticalIndicators.map(String) : [];
  return (
    <Panel className="motion-card-delay-2 self-start">
      <h2 className="text-3xl font-semibold">Critical Indicators</h2>
      {indicators.length > 0 ? (
        <div className="mt-5 grid gap-4">
          {indicators.map((indicator) => (
            <Indicator key={indicator} indicator={indicator} />
          ))}
        </div>
      ) : (
        <div className="mt-6 rounded-3xl border border-dashed border-black/15 bg-white/45 p-5">
          <p className="font-semibold text-slate-700">Awaiting uploaded report</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">After upload, CLAIR extracts indicators from the PDF text. No static lab values are shown here.</p>
        </div>
      )}
      <div className="mt-8 rounded-3xl bg-[var(--clair-mint)] p-5">
        <h3 className="text-xl font-semibold">Questions for Doctor</h3>
        <div className="mt-3 grid gap-2 text-sm text-slate-700">
          {(documentSummary?.questionsForDoctor ?? ["Upload a report to generate doctor questions from that document."]).map((question) => (
          <p key={question} className="motion-row rounded-2xl px-2 py-1">{question}</p>
          ))}
        </div>
      </div>
      {documentSummary ? <p data-testid="document-disclaimer" className="mt-5 text-sm font-semibold text-slate-500">{documentSummary.disclaimer}</p> : null}
    </Panel>
  );
}

function parseIndicator(indicator: string) {
  const [labelPart, rest = ""] = indicator.split(":");
  const [valuePart = rest, statusPart = "Review"] = rest.split(/\s+-\s+/);
  return {
    label: labelPart.trim() || "Report marker",
    value: valuePart.trim() || indicator,
    status: statusPart.trim() || "Review",
  };
}

function Indicator({ indicator }: { indicator: string }) {
  const parsed = parseIndicator(indicator);
  const isNormal = /\bnormal\b/i.test(parsed.status);
  const isAbnormal = /\b(high|elevated|low|abnormal)\b/i.test(parsed.status);
  const barClass = isNormal ? "bg-emerald-500 w-[42%]" : isAbnormal ? "bg-red-600 w-[78%]" : "bg-amber-500 w-[58%]";
  const badgeClass = isNormal ? "bg-emerald-100 text-emerald-800" : isAbnormal ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-800";

  return (
    <div className="motion-row rounded-3xl bg-white/55 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-semibold text-slate-600">{parsed.label}</p>
          <p className={`mt-2 text-2xl font-semibold ${isNormal ? "text-emerald-700" : isAbnormal ? "text-red-600" : "text-amber-700"}`}>{parsed.value}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-bold ${badgeClass}`}>{parsed.status}</span>
      </div>
      <div className="motion-progress mt-3 h-1.5 rounded-full bg-slate-200">
        <div className={`motion-progress-fill h-full rounded-full ${barClass}`} />
      </div>
    </div>
  );
}

function EmergencyScreen() {
  return (
    <div className="motion-page grid min-h-[620px] place-items-center">
      <div className="relative w-full max-w-4xl">
        <div className="absolute -left-16 top-10 hidden h-[520px] w-80 rounded-[2rem] bg-white/75 shadow-panel lg:block" />
        <div className="absolute -right-16 top-10 hidden h-[520px] w-80 rounded-[2rem] bg-white/75 shadow-panel lg:block" />
        <Panel className="motion-no-hover relative z-10 mx-auto max-w-3xl !p-12">
          <span className="motion-emergency-pulse inline-flex rounded-full bg-red-100 px-5 py-2 font-semibold text-red-700"><AlertTriangle size={17} />&nbsp; CRITICAL ALERT</span>
          <div className="mt-8 grid gap-8 md:grid-cols-[130px_1fr]">
            <div className="motion-emergency-pulse grid h-28 w-28 place-items-center rounded-full bg-red-600 text-white">HIGH</div>
            <div>
              <h1 className="text-5xl font-semibold leading-tight">Emergency Symptoms Detected</h1>
              <p className="mt-3 text-xl leading-8 text-slate-600">High-risk symptoms were identified. Please do not wait. Contact emergency services or proceed to the nearest emergency department.</p>
            </div>
          </div>
          <div className="mt-8 rounded-3xl bg-slate-100 p-5">
            <p className="font-semibold">Recommended Action</p>
            <p className="mt-1 text-lg text-slate-700">Proceed to nearest Emergency Department immediately.</p>
          </div>
          <div className="mt-8 flex flex-wrap gap-4">
            <Button variant="danger" className="motion-emergency-pulse px-8">Call Emergency Services</Button>
            <Button variant="secondary" className="px-8">I understand</Button>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function SafetyScreen({ currentUser, onLogout }: { currentUser: User | null; onLogout: () => void }) {
  const user = currentUser ?? { id: "guest", email: "patient@example.com", name: "Maya Rao", role: "patient" as const };
  return (
    <div className="motion-page grid gap-5 lg:grid-cols-[1fr_480px]">
      <div>
        <h1 className="text-5xl font-semibold">Safety, Privacy & Session Control</h1>
        <p className="mt-3 max-w-4xl text-xl leading-8 text-slate-600">A modern trust center with clear medical limits, privacy commitments, and authenticated session behavior.</p>
        <div className="mt-8 grid gap-5 md:grid-cols-2">
          {[
            ["No Diagnosis", "CLAIR gives navigation guidance only."],
            ["Emergency Override", "Critical phrases trigger blocking alert."],
            ["Curated Data", "Provider data is clearly marked demo."],
            ["Login Required", "User enters through secure demo login."],
          ].map(([title, detail]) => (
            <Panel key={title} className="motion-card-delay-1 flex min-h-32 items-center gap-4">
              <span className="grid h-14 w-14 place-items-center rounded-full bg-[var(--clair-mint)]"><Check size={18} /></span>
              <div>
                <h2 className="text-2xl font-semibold">{title}</h2>
                <p className="mt-1 text-slate-600">{detail}</p>
              </div>
            </Panel>
          ))}
        </div>
      </div>
      <Panel className="motion-card-delay-2 !p-8">
        <h2 className="text-3xl font-semibold">Profile & Logout</h2>
        <div className="mt-7 flex items-center gap-4 rounded-3xl bg-[var(--clair-mint)]/70 p-5">
          <img src="/images/patient-portrait.jpg" alt="" className="h-16 w-16 rounded-full object-cover" />
          <div>
            <p className="text-2xl font-semibold">{user.name}</p>
            <p className="text-slate-600">{user.email}</p>
          </div>
        </div>
        <div className="mt-8 grid gap-6 text-lg">
          {["Session timeout: 30 minutes", "Last login: Today 10:42 AM", "Data retention: Session only"].map((item) => (
            <p key={item}>- {item}</p>
          ))}
        </div>
        <Button variant="danger" onClick={onLogout} className="mt-12 w-full text-base">Logout Securely</Button>
        <p className="mt-7 text-sm text-slate-500">After logout, chat history and uploaded document state are cleared for this browser session.</p>
      </Panel>
    </div>
  );
}

function ResultRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="motion-row rounded-3xl border border-black/10 bg-white/70 p-4">
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <p className="mt-2 text-xl font-semibold">{value}</p>
    </div>
  );
}

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3 className="text-2xl font-semibold">{title}</h3>
      <ul className="mt-5 grid gap-3">
        {items.map((item) => {
          const cleanItem = item.replace(/^[-•]\s*/, "");
          return (
            <li key={item} className="flex gap-3 text-base leading-7">
              <span className="mt-0.5 shrink-0 text-slate-500">-</span>
              <span>{cleanItem}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function ProviderList({ providers }: { providers: Provider[] }) {
  return (
    <Panel className="motion-card-delay-2">
      <h2 className="text-2xl font-semibold">Provider matches</h2>
      <div className="mt-4 grid gap-3">
        {providers.map((provider) => (
          <article key={provider.id} className="motion-row rounded-3xl border border-black/10 bg-white/65 p-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h3 className="font-semibold text-[var(--clair-ink)]">{provider.name}</h3>
                <p className="text-sm font-semibold text-emerald-800">{provider.specialty}</p>
              </div>
              <span className="rounded-full bg-white px-3 py-1 text-sm font-bold">{provider.rating.toFixed(1)} rating</span>
            </div>
            <p className="mt-3 text-sm text-slate-600">{provider.distanceMiles} miles away. {provider.availability}.</p>
          </article>
        ))}
      </div>
    </Panel>
  );
}
