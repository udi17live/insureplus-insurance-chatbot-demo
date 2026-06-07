"use client"

import * as React from "react"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

// ── Types mirroring backend AgentPolicyOut / AgentQuoteOut ──────────────────

export interface PolicyResult {
  policy_id: string
  policy_number: string
  product_type: "motor" | "bike" | "life" | "device"
  status: string
  premium_amount: number
  currency: string
  coverage_data: Record<string, unknown>
  start_date: string | null
  end_date: string | null
}

export interface QuoteResult {
  quote_id: string
  product_type: "motor" | "bike" | "life" | "device"
  premium_amount: number
  currency: string
  coverage_summary: Record<string, unknown>
  expires_at: string | null
}

// ── Shared helpers ───────────────────────────────────────────────────────────

const PRODUCT_LABELS: Record<string, string> = {
  motor: "Motor",
  bike: "Bike",
  life: "Life",
  device: "Device",
}

function formatDate(iso: string | null) {
  if (!iso) return "—"
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })
}

function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat(undefined, { style: "currency", currency: currency || "GBP", maximumFractionDigits: 0 }).format(amount)
}

function statusColor(status: string) {
  if (status === "active") return "bg-green-500/15 text-green-700 dark:text-green-400"
  if (status === "cancelled") return "bg-red-500/15 text-red-700 dark:text-red-400"
  return "bg-muted text-muted-foreground"
}

function CardShell({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("rounded-sm border bg-background p-4 text-sm shadow-sm", className)}>
      {children}
    </div>
  )
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 py-1 border-b last:border-0">
      <span className="text-muted-foreground shrink-0">{label}</span>
      <span className="font-medium text-right">{value}</span>
    </div>
  )
}

// ── PolicyCard ───────────────────────────────────────────────────────────────

export function PolicyCard({
  policy,
  onCancel,
}: {
  policy: PolicyResult
  onCancel?: (policyId: string, policyNumber?: string) => Promise<void> | void
}) {
  const [cancelling, setCancelling] = React.useState(false)

  async function handleCancel() {
    if (!onCancel) return
    setCancelling(true)
    try {
      await onCancel(policy.policy_id, policy.policy_number)
    } finally {
      setCancelling(false)
    }
  }

  return (
    <CardShell>
      <div className="mb-3 flex items-center justify-between">
        <span className="font-semibold tracking-wide uppercase text-xs text-muted-foreground">
          {PRODUCT_LABELS[policy.product_type] ?? policy.product_type} Insurance
        </span>
        <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium capitalize", statusColor(policy.status))}>
          {policy.status}
        </span>
      </div>
      <Row label="Policy No." value={policy.policy_number} />
      <Row label="Premium" value={formatCurrency(policy.premium_amount, policy.currency)} />
      <Row label="Start" value={formatDate(policy.start_date)} />
      <Row label="End" value={formatDate(policy.end_date)} />
      {onCancel && policy.status === "active" && (
        <div className="mt-4">
          <button
            onClick={handleCancel}
            disabled={cancelling}
            className="w-full rounded-sm border border-destructive px-4 py-2 text-sm font-medium text-destructive hover:bg-destructive/10 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {cancelling && <Loader2 className="h-3 w-3 animate-spin" />}
            {cancelling ? "Cancelling…" : "Cancel Policy"}
          </button>
        </div>
      )}
    </CardShell>
  )
}

// ── PoliciesCard (list result) ───────────────────────────────────────────────

export function PoliciesCard({
  policies,
  onCancel,
}: {
  policies: PolicyResult[]
  onCancel?: (policyId: string, policyNumber?: string) => Promise<void> | void
}) {
  if (policies.length === 0) {
    return (
      <CardShell>
        <p className="text-muted-foreground text-center py-2">No policies found.</p>
      </CardShell>
    )
  }
  return (
    <div className="flex flex-col gap-3">
      {policies.map((p) => (
        <PolicyCard key={p.policy_id} policy={p} onCancel={onCancel} />
      ))}
    </div>
  )
}

// ── QuoteCard ────────────────────────────────────────────────────────────────

export function QuoteCard({
  quote,
  onConfirm,
  onDecline,
}: {
  quote: QuoteResult
  onConfirm?: () => void
  onDecline?: () => void
}) {
  const coverageItems = Object.entries(quote.coverage_summary ?? {})

  return (
    <CardShell>
      <div className="mb-3 flex items-center justify-between">
        <span className="font-semibold tracking-wide uppercase text-xs text-muted-foreground">
          {PRODUCT_LABELS[quote.product_type] ?? quote.product_type} Quote
        </span>
        <span className="text-xs text-muted-foreground">
          Expires {formatDate(quote.expires_at)}
        </span>
      </div>

      <div className="mb-3 text-center py-2 rounded-sm bg-muted">
        <p className="text-2xl font-bold">{formatCurrency(quote.premium_amount, quote.currency)}</p>
        <p className="text-xs text-muted-foreground mt-0.5">annual premium</p>
      </div>

      {coverageItems.length > 0 && (
        <div className="mt-2">
          {coverageItems.map(([k, v]) => (
            <Row key={k} label={k.replace(/_/g, " ")} value={String(v)} />
          ))}
        </div>
      )}

      {(onConfirm || onDecline) && (
        <div className="mt-4 flex gap-2">
          {onConfirm && (
            <button
              onClick={onConfirm}
              className="flex-1 rounded-sm bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition-opacity"
            >
              Confirm &amp; Purchase
            </button>
          )}
          {onDecline && (
            <button
              onClick={onDecline}
              className="flex-1 rounded-sm border border-border px-4 py-2 text-sm font-medium hover:bg-muted transition-colors"
            >
              Decline
            </button>
          )}
        </div>
      )}
    </CardShell>
  )
}
