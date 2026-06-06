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

export const serverApi = {
  get: <T>(path: string) => apiFetch<T>(serverBase, path),
  post: <T>(path: string, body: unknown) =>
    apiFetch<T>(serverBase, path, { method: "POST", body: JSON.stringify(body) }),
}
