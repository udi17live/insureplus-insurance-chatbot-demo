const clientBase = process.env.NEXT_PUBLIC_API_URL ?? ""
const serverBase = process.env.BACKEND_URL ?? clientBase

async function apiFetch<T>(base: string, path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  })

  if (!res.ok) {
    const json = await res.json().catch(() => ({}))
    throw Object.assign(new Error(json?.detail ?? `HTTP ${res.status}`), {
      response: { data: json },
    })
  }

  const text = await res.text()
  return (text ? JSON.parse(text) : undefined) as T
}

export const api = {
  get: <T>(path: string) => apiFetch<T>(clientBase, path),
  post: <T>(path: string, body: unknown) =>
    apiFetch<T>(clientBase, path, { method: "POST", body: JSON.stringify(body) }),
}

// ── Domain helpers ───────────────────────────────────────────────────────────

export interface PolicyOut {
  id: string
  user_id: string
  quote_id: string | null
  policy_number: string
  product_type: string
  status: string
  coverage_data: Record<string, unknown>
  premium_amount: number
  currency: string
  start_date: string | null
  end_date: string | null
  created_at: string
  updated_at: string
}

export interface PaymentOut {
  id: string
  user_id: string
  policy_id: string | null
  quote_id: string | null
  payment_reference: string
  amount: number
  currency: string
  status: string
  created_at: string
  updated_at: string
}

export const policiesApi = {
  list: () => api.get<PolicyOut[]>("/api/v1/policies"),
  cancel: (policyId: string) =>
    api.post<PolicyOut>(`/api/v1/policies/${policyId}/cancel`, {}),
}

export const paymentsApi = {
  confirm: (quoteId: string) =>
    api.post<PolicyOut>("/api/v1/payments/confirm", { quote_id: quoteId }),
}

export const serverApi = {
  get: <T>(path: string) => apiFetch<T>(serverBase, path),
  post: <T>(path: string, body: unknown) =>
    apiFetch<T>(serverBase, path, { method: "POST", body: JSON.stringify(body) }),
}
