import React from "react";
import { ShieldCheck, Landmark, FileText, BadgeCheck, Check } from "lucide-react";
import { useApp } from "../context/AppContext";
import { t } from "../lib/i18n";

// A 4-step readiness tracker for withdrawals:
// Verified badge -> Bank details -> Documents -> Approved
export default function PayoutStatusTracker({ account }) {
  const { user, lang } = useApp();
  const rejected = account?.status === "rejected";

  const steps = [
    {
      key: "identity",
      label: t("step_identity", lang),
      icon: ShieldCheck,
      done: user?.verified === true,
    },
    {
      key: "bank",
      label: t("step_bank_details", lang),
      icon: Landmark,
      done: !!(account && account.iban && account.holder_name),
    },
    {
      key: "documents",
      label: t("step_documents", lang),
      icon: FileText,
      done: !!(account && account.bank_statement_path && account.proof_of_address_path),
    },
    {
      key: "approved",
      label: t("step_approved", lang),
      icon: BadgeCheck,
      done: account?.status === "verified",
    },
  ];

  // The "current" step is the first not-done step.
  const currentIndex = steps.findIndex((s) => !s.done);

  return (
    <div className="glass rounded-2xl p-5" data-testid="payout-status-tracker">
      <div className="flex items-center justify-between gap-3 flex-wrap mb-4">
        <div className="font-serif-luxe text-xl">{t("payout_tracker_title", lang)}</div>
        {account?.status === "verified" && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full border text-xs bg-emerald-500/15 border-emerald-500/40 text-emerald-300">
            <BadgeCheck size={12} /> {t("step_approved", lang)}
          </span>
        )}
      </div>

      <div className="flex items-start">
        {steps.map((s, i) => {
          const isCurrent = i === currentIndex && !rejected;
          const rejectedHere = rejected && s.key === "approved";
          const state = s.done ? "done" : rejectedHere ? "rejected" : isCurrent ? "current" : "pending";
          const circle =
            state === "done"
              ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-300"
              : state === "rejected"
              ? "bg-rose-500/15 border-rose-500/50 text-rose-300"
              : state === "current"
              ? "bg-amber-500/15 border-amber-500/50 text-amber-300"
              : "bg-white/5 border-white/10 text-slate-500";
          const labelCls =
            state === "done"
              ? "text-emerald-300"
              : state === "rejected"
              ? "text-rose-300"
              : state === "current"
              ? "text-amber-200"
              : "text-slate-500";
          const Icon = s.icon;
          return (
            <React.Fragment key={s.key}>
              <div className="flex flex-col items-center flex-shrink-0 w-16 sm:w-24" data-testid={`payout-step-${s.key}`}>
                <div className={`relative w-10 h-10 rounded-full border flex items-center justify-center transition-colors ${circle}`}>
                  {state === "done" ? <Check size={18} /> : <Icon size={17} />}
                </div>
                <div className={`mt-2 text-[11px] sm:text-xs text-center leading-tight ${labelCls}`}>{s.label}</div>
              </div>
              {i < steps.length - 1 && (
                <div className={`flex-1 h-0.5 mt-5 rounded-full ${steps[i].done ? "bg-emerald-500/40" : "bg-white/10"}`} />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {rejected && account?.reason && (
        <div className="mt-4 text-xs text-rose-300" data-testid="payout-tracker-reason">{account.reason}</div>
      )}
      {account?.status !== "verified" && !rejected && currentIndex >= 0 && (
        <div className="mt-4 text-xs text-slate-400" data-testid="payout-tracker-hint">
          {t("payout_tracker_next", lang)} <span className="text-amber-200">{steps[currentIndex].label}</span>
        </div>
      )}
    </div>
  );
}
