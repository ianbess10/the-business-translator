import { useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  Bot,
  CheckCircle2,
  Database,
  FileWarning,
  Gauge,
  Inbox,
  LayoutDashboard,
  MessageSquareWarning,
  Settings,
  ShieldAlert,
  Siren,
  Timer,
  UserCheck,
  XCircle,
} from "lucide-react";

type RiskLevel = "Low" | "Medium" | "Critical";

interface AiDiagnosis {
  symptom: string;
  root_cause: string;
  missing_information: string;
  routing: string;
  escalation_required: boolean;
}

interface TradeException {
  id: string;
  trade_ref: string;
  message_type: string;
  counterparty: string;
  value_date: string;
  risk_level: RiskLevel;
  status: string;
  raw_narrative: string;
  ai_diagnosis: AiDiagnosis;
}

const EXCEPTIONS: TradeException[] = [
  {
    id: "EX-1042",
    trade_ref: "TXN-88392",
    message_type: "MT515",
    counterparty: "Goldman Sachs Intl",
    value_date: "T+1",
    risk_level: "Medium",
    status: "Pending Review",
    raw_narrative:
      "Trade matching failed. Counterparty SSI does not match internal record for receiving agent.",
    ai_diagnosis: {
      symptom: "Trade matching failure",
      root_cause: "Mismatched Standard Settlement Instructions (SSI)",
      missing_information: "Authoritative SSI confirmation from counterparty",
      routing: "Reference Data / SSI Team",
      escalation_required: false,
    },
  },
  {
    id: "EX-1043",
    trade_ref: "TXN-88399",
    message_type: "Unstructured Email",
    counterparty: "Citadel LLC",
    value_date: "T+0",
    risk_level: "Critical",
    status: "Pending Review",
    raw_narrative:
      "URGENT: Client fund lacks sufficient USD balance to settle FX leg of the equity purchase. Market deadline in 45 minutes.",
    ai_diagnosis: {
      symptom: "Insufficient funds for settlement",
      root_cause: "Unfunded FX leg",
      missing_information: "Client funding status or credit line availability",
      routing: "Client Services / Credit Risk",
      escalation_required: true,
    },
  },
  {
    id: "EX-1044",
    trade_ref: "TXN-88405",
    message_type: "MT548",
    counterparty: "JPMorgan Chase",
    value_date: "T+2",
    risk_level: "Low",
    status: "Pending Review",
    raw_narrative: "Status settlement pending. Awaiting counterparty instruction.",
    ai_diagnosis: {
      symptom: "Unmatched trade",
      root_cause: "Late instruction from counterparty",
      missing_information: "Counterparty MT54x instruction",
      routing: "Settlements",
      escalation_required: false,
    },
  },
];

const NAV = [
  { label: "Dashboard", icon: LayoutDashboard, active: false },
  { label: "Exception Queue", icon: AlertTriangle, active: true },
  { label: "Reference Data", icon: Database, active: false },
  { label: "Analytics", icon: BarChart3, active: false },
  { label: "Settings", icon: Settings, active: false },
];

const KPIS = [
  { label: "STP Rate", value: "94.2%", hint: "Straight-through processing", icon: Gauge, valueClass: "text-cyan-300", iconClass: "border-cyan-500/30 bg-cyan-500/10 text-cyan-400", borderClass: "border-zinc-800" },
  { label: "Pending Exceptions", value: "42", hint: "In exception queue", icon: Inbox, valueClass: "text-zinc-100", iconClass: "border-zinc-700 bg-zinc-800/60 text-zinc-300", borderClass: "border-zinc-800" },
  { label: "Critical Escalations", value: "3", hint: "Require immediate review", icon: Siren, valueClass: "text-red-400", iconClass: "border-red-500/40 bg-red-500/10 text-red-400", borderClass: "border-red-500/30" },
  { label: "Avg Resolution Time", value: "18m", hint: "Rolling 24h window", icon: Timer, valueClass: "text-amber-300", iconClass: "border-amber-500/30 bg-amber-500/10 text-amber-400", borderClass: "border-zinc-800" },
];

function RiskBadge({ level }: { level: RiskLevel }) {
  const styles: Record<RiskLevel, string> = {
    Low: "border-zinc-600 bg-zinc-800 text-zinc-300",
    Medium: "border-amber-500/40 bg-amber-500/10 text-amber-300",
    Critical: "border-red-500/50 bg-red-500/15 text-red-400",
  };
  return (
    <span className={`inline-flex rounded border px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide ${styles[level]}`}>
      {level}
    </span>
  );
}

export default function App() {
  const [selectedId, setSelectedId] = useState(EXCEPTIONS[0].id);
  const [feedback, setFeedback] = useState<string | null>(null);

  const selected = useMemo(
    () => EXCEPTIONS.find((ex) => ex.id === selectedId) ?? EXCEPTIONS[0],
    [selectedId],
  );

  const diagnosis = selected.ai_diagnosis;

  return (
    <div className="flex h-full min-h-screen bg-zinc-950 text-zinc-100">
      {/* LEFT SIDEBAR */}
      <aside className="flex w-56 shrink-0 flex-col border-r border-zinc-800 bg-zinc-950">
        <div className="border-b border-zinc-800 px-4 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded border border-cyan-500/40 bg-cyan-500/10">
              <Activity className="h-4 w-4 text-cyan-400" strokeWidth={2.25} />
            </div>
            <div className="min-w-0 leading-tight">
              <p className="truncate text-[11px] font-semibold uppercase tracking-[0.14em] text-cyan-400">
                Ops Desk
              </p>
              <p className="truncate text-xs text-zinc-400">The Business Translator</p>
            </div>
          </div>
        </div>

        <nav className="flex flex-1 flex-col gap-0.5 p-2">
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.label}
                type="button"
                className={`flex items-center gap-2.5 rounded px-3 py-2 text-left text-[13px] transition-colors ${
                  item.active
                    ? "bg-zinc-800/80 text-zinc-50 shadow-[inset_2px_0_0_0_#22d3ee]"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
                }`}
              >
                <Icon className="h-4 w-4 shrink-0 opacity-80" strokeWidth={1.75} />
                <span className="font-medium">{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="border-t border-zinc-800 px-4 py-3">
          <p className="font-mono text-[10px] uppercase tracking-wider text-zinc-500">
            Session · OPS-IBESS
          </p>
          <p className="mt-0.5 text-[11px] text-zinc-400">Human-accountable review mode</p>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        {/* TOP KPI HEADER */}
        <header className="border-b border-zinc-800 bg-zinc-950/80 px-4 py-3">
          <div className="mb-2.5 flex items-end justify-between gap-4">
            <div>
              <h1 className="text-sm font-semibold tracking-tight text-zinc-100">
                Back Office Settlement & Exception Management
              </h1>
              <p className="text-[11px] text-zinc-500">
                AI prepares the decision record · Operations remains accountable
              </p>
            </div>
            <div className="hidden items-center gap-2 sm:flex">
              <span className="inline-flex items-center gap-1.5 rounded border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-emerald-400">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                Live Desk
              </span>
              <span className="font-mono text-[10px] text-zinc-500">2026-08-12 · LONDON</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 lg:grid-cols-4">
            {KPIS.map((kpi) => {
              const Icon = kpi.icon;
              return (
                <div
                  key={kpi.label}
                  className={`flex items-center gap-3 rounded border ${kpi.borderClass} bg-zinc-900/70 px-3 py-2.5`}
                >
                  <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded border ${kpi.iconClass}`}>
                    <Icon className="h-4 w-4" strokeWidth={1.75} />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-[10px] font-medium uppercase tracking-[0.12em] text-zinc-500">
                      {kpi.label}
                    </p>
                    <p className={`font-mono text-lg font-semibold leading-none ${kpi.valueClass}`}>
                      {kpi.value}
                    </p>
                    <p className="mt-0.5 truncate text-[10px] text-zinc-600">{kpi.hint}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </header>

        <main className="flex min-h-0 flex-1 flex-col lg:flex-row">
          {/* EXCEPTION QUEUE — Pitch Step 1 */}
          <section className="flex min-h-0 flex-1 flex-col border-r border-zinc-800 bg-zinc-950/40">
            <div className="flex items-center justify-between border-b border-zinc-800 px-3 py-2">
              <div>
                <h2 className="text-xs font-semibold uppercase tracking-[0.14em] text-zinc-300">
                  Exception Queue
                </h2>
                <p className="text-[11px] text-zinc-500">
                  Unstructured noise your ops team works all day
                </p>
              </div>
              <span className="rounded border border-zinc-700 bg-zinc-900 px-2 py-0.5 font-mono text-[10px] text-zinc-400">
                FILTER: OPEN
              </span>
            </div>

            <div className="min-h-0 flex-1 overflow-auto">
              <table className="w-full border-collapse text-left text-[12px]">
                <thead className="sticky top-0 z-10 bg-zinc-900">
                  <tr className="border-b border-zinc-800 text-[10px] uppercase tracking-[0.12em] text-zinc-500">
                    <th className="px-3 py-2 font-medium">Trade ID</th>
                    <th className="px-3 py-2 font-medium">Msg Type</th>
                    <th className="px-3 py-2 font-medium">Counterparty</th>
                    <th className="px-3 py-2 font-medium">Value Date</th>
                    <th className="px-3 py-2 font-medium">Status</th>
                    <th className="px-3 py-2 font-medium">Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {EXCEPTIONS.map((ex) => {
                    const isSelected = ex.id === selected.id;
                    const isCritical = ex.risk_level === "Critical";
                    return (
                      <tr
                        key={ex.id}
                        onClick={() => {
                          setSelectedId(ex.id);
                          setFeedback(null);
                        }}
                        className={`cursor-pointer border-b border-zinc-800/80 transition-colors ${
                          isSelected
                            ? "bg-cyan-500/10 shadow-[inset_2px_0_0_0_#22d3ee]"
                            : isCritical
                              ? "bg-red-500/[0.04] hover:bg-red-500/10"
                              : "hover:bg-zinc-900/80"
                        }`}
                      >
                        <td className="px-3 py-2.5">
                          <div className={`font-mono text-[12px] font-medium ${isCritical ? "text-red-300" : "text-zinc-100"}`}>
                            {ex.id}
                          </div>
                          <div className="font-mono text-[10px] text-zinc-500">{ex.trade_ref}</div>
                          <div className={`mt-1 max-w-[220px] truncate font-mono text-[10px] ${isCritical ? "text-red-400/80" : "text-zinc-600"}`}>
                            {ex.raw_narrative}
                          </div>
                        </td>
                        <td className="px-3 py-2.5 font-mono text-zinc-300">{ex.message_type}</td>
                        <td className="px-3 py-2.5 text-zinc-200">{ex.counterparty}</td>
                        <td className="px-3 py-2.5 font-mono text-zinc-300">{ex.value_date}</td>
                        <td className="px-3 py-2.5 text-zinc-400">{ex.status}</td>
                        <td className="px-3 py-2.5">
                          <RiskBadge level={ex.risk_level} />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          {/* AI DECISION RECORD — Pitch Steps 2–4 */}
          <section className="flex min-h-0 w-full flex-col bg-zinc-950/70 lg:w-[48%] lg:max-w-xl lg:shrink-0">
            <div className="flex items-center justify-between border-b border-zinc-800 px-3 py-2">
              <div className="flex items-center gap-2">
                <Bot className="h-3.5 w-3.5 text-cyan-400" strokeWidth={2} />
                <div>
                  <h2 className="text-xs font-semibold uppercase tracking-[0.14em] text-zinc-300">
                    AI Decision Record
                  </h2>
                  <p className="text-[11px] text-zinc-500">
                    {selected.id} · Trade Exception Intelligence
                  </p>
                </div>
              </div>
              <span className="rounded border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 font-mono text-[10px] text-cyan-300">
                v1.5
              </span>
            </div>

            <div className="min-h-0 flex-1 space-y-3 overflow-auto p-3">
              {/* A — Raw Input */}
              <div className="rounded border border-zinc-800 bg-zinc-900/50">
                <div className="flex items-center gap-2 border-b border-zinc-800 px-3 py-2">
                  <FileWarning className="h-3.5 w-3.5 text-zinc-400" />
                  <h3 className="text-[10px] font-semibold uppercase tracking-[0.14em] text-zinc-400">
                    A · Raw Input
                  </h3>
                </div>
                <div className="space-y-2 px-3 py-3">
                  <div className="flex flex-wrap gap-x-4 gap-y-1 font-mono text-[10px] text-zinc-500">
                    <span>MSG: {selected.message_type}</span>
                    <span>CPTY: {selected.counterparty}</span>
                    <span>VD: {selected.value_date}</span>
                  </div>
                  <pre className={`whitespace-pre-wrap rounded border p-3 font-mono text-[12px] leading-relaxed ${
                    selected.risk_level === "Critical"
                      ? "border-red-500/30 bg-red-950/30 text-red-100"
                      : "border-zinc-800 bg-black/40 text-zinc-200"
                  }`}>
                    {selected.raw_narrative}
                  </pre>
                </div>
              </div>

              {/* B — AI Diagnosis (Pitch Step 3: Translation) */}
              <div className="rounded border border-cyan-500/20 bg-cyan-500/[0.03]">
                <div className="flex items-center gap-2 border-b border-cyan-500/20 px-3 py-2">
                  <Bot className="h-3.5 w-3.5 text-cyan-400" />
                  <h3 className="text-[10px] font-semibold uppercase tracking-[0.14em] text-cyan-300">
                    B · AI Diagnosis — The Translation
                  </h3>
                  <span className="ml-auto text-[10px] text-zinc-500">Advisory only</span>
                </div>

                <div className="grid gap-2 p-3">
                  {/* Symptom vs Missing Info — pitch highlight pair */}
                  <div className="grid gap-2 sm:grid-cols-2">
                    <div className="rounded border border-zinc-700 bg-zinc-950/80 px-3 py-2.5">
                      <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-zinc-500">
                        Symptom
                      </p>
                      <p className="mt-1 text-[13px] font-medium leading-snug text-zinc-100">
                        {diagnosis.symptom}
                      </p>
                      <p className="mt-1.5 text-[10px] text-zinc-600">What broke</p>
                    </div>
                    <div className="rounded border border-cyan-500/40 bg-cyan-500/10 px-3 py-2.5 ring-1 ring-cyan-400/20">
                      <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-cyan-400">
                        Missing Information Required
                      </p>
                      <p className="mt-1 text-[13px] font-medium leading-snug text-cyan-50">
                        {diagnosis.missing_information}
                      </p>
                      <p className="mt-1.5 text-[10px] text-cyan-600/80">What is needed next</p>
                    </div>
                  </div>

                  <div className="rounded border border-zinc-800/80 bg-zinc-950/60 px-3 py-2">
                    <p className="text-[10px] font-medium uppercase tracking-[0.12em] text-zinc-500">
                      Root Cause
                    </p>
                    <p className="mt-0.5 text-[13px] leading-snug text-zinc-100">
                      {diagnosis.root_cause}
                    </p>
                  </div>

                  <div className="rounded border border-zinc-800/80 bg-zinc-950/60 px-3 py-2">
                    <p className="text-[10px] font-medium uppercase tracking-[0.12em] text-zinc-500">
                      Recommended Routing
                    </p>
                    <p className="mt-0.5 text-[13px] leading-snug text-zinc-100">
                      {diagnosis.routing}
                    </p>
                  </div>

                  <div className="rounded border border-zinc-800/80 bg-zinc-950/60 px-3 py-2">
                    <p className="text-[10px] font-medium uppercase tracking-[0.12em] text-zinc-500">
                      Escalation Status
                    </p>
                    <div className="mt-1.5 flex items-center gap-2">
                      {diagnosis.escalation_required ? (
                        <span className="inline-flex items-center gap-1.5 rounded border border-red-500/50 bg-red-500/15 px-2 py-1 text-[11px] font-semibold uppercase tracking-wide text-red-300">
                          <ShieldAlert className="h-3.5 w-3.5" />
                          Yes — Escalate
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 rounded border border-emerald-500/40 bg-emerald-500/10 px-2 py-1 text-[11px] font-semibold uppercase tracking-wide text-emerald-300">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          No — Standard Route
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* C — Human Action Bar (Pitch Step 4) */}
              <div className="rounded border-2 border-amber-500/40 bg-amber-500/[0.06] shadow-[0_0_24px_-8px_rgba(245,158,11,0.35)]">
                <div className="flex items-center gap-2 border-b border-amber-500/25 px-3 py-2.5">
                  <UserCheck className="h-4 w-4 text-amber-300" />
                  <div>
                    <h3 className="text-[10px] font-semibold uppercase tracking-[0.14em] text-amber-200">
                      C · Human Action — Accountability
                    </h3>
                    <p className="text-[11px] text-amber-100/70">
                      The AI prepares the record; the human professional remains accountable.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 p-3">
                  <button
                    type="button"
                    onClick={() => setFeedback(`Approved & routed to ${diagnosis.routing}`)}
                    className="inline-flex items-center justify-center gap-1.5 rounded border border-emerald-500/40 bg-emerald-500/15 px-2.5 py-2.5 text-[11px] font-semibold text-emerald-200 transition hover:bg-emerald-500/25"
                  >
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Approve & Route
                  </button>
                  <button
                    type="button"
                    onClick={() => setFeedback("AI diagnosis rejected — returned for rework")}
                    className="inline-flex items-center justify-center gap-1.5 rounded border border-red-500/40 bg-red-500/10 px-2.5 py-2.5 text-[11px] font-semibold text-red-200 transition hover:bg-red-500/20"
                  >
                    <XCircle className="h-3.5 w-3.5" />
                    Reject AI Diagnosis
                  </button>
                  <button
                    type="button"
                    onClick={() =>
                      setFeedback(`Info requested: ${diagnosis.missing_information}`)
                    }
                    className="inline-flex items-center justify-center gap-1.5 rounded border border-zinc-600 bg-zinc-800/80 px-2.5 py-2.5 text-[11px] font-semibold text-zinc-200 transition hover:bg-zinc-700"
                  >
                    <MessageSquareWarning className="h-3.5 w-3.5" />
                    Request Info
                  </button>
                  <button
                    type="button"
                    onClick={() =>
                      setFeedback("Escalated to management — control review required")
                    }
                    className="inline-flex items-center justify-center gap-1.5 rounded border border-amber-500/40 bg-amber-500/15 px-2.5 py-2.5 text-[11px] font-semibold text-amber-200 transition hover:bg-amber-500/25"
                  >
                    <ArrowUpRight className="h-3.5 w-3.5" />
                    Escalate to Management
                  </button>
                </div>

                {feedback && (
                  <div className="mx-3 mb-3 rounded border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-[11px] text-emerald-200">
                    <span className="font-semibold uppercase tracking-wide">Operator decision logged · </span>
                    {feedback}
                  </div>
                )}
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
