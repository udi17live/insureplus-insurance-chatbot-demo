const base = process.env.NEXT_PUBLIC_API_URL ?? ""

export type ToolName = "agent_list_policies" | "agent_create_quote" | "agent_cancel_policy"

export interface ToolResultEvent {
  tool: ToolName
  result: unknown
}

export interface StreamChatOptions {
  message: string
  threadId: string | null
  onThread: (id: string) => void
  onToken: (token: string) => void
  onToolResult?: (event: ToolResultEvent) => void
  onAuthRequired?: () => void
}

export async function streamChat({ message, threadId, onThread, onToken, onToolResult, onAuthRequired }: StreamChatOptions) {
  const res = await fetch(`${base}/chat/message`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId }),
  })

  if (!res.ok) {
    const json = await res.json().catch(() => ({}))
    throw new Error(json?.detail ?? `HTTP ${res.status}`)
  }

  const reader = res.body?.getReader()
  if (!reader) return

  const decoder = new TextDecoder()
  let buffer = ""
  let currentEvent = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n")
    buffer = lines.pop() ?? ""

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim()
        continue
      }
      if (!line.startsWith("data: ")) {
        currentEvent = ""
        continue
      }
      const data = line.slice(6)

      if (currentEvent === "thread") {
        onThread(data.trim())
        currentEvent = ""
        continue
      }

      if (currentEvent === "auth_required") {
        onAuthRequired?.()
        currentEvent = ""
        continue
      }

      if (currentEvent === "tool_result") {
        try {
          const parsed = JSON.parse(data) as ToolResultEvent
          onToolResult?.(parsed)
        } catch {}
        currentEvent = ""
        continue
      }

      if (data === "[DONE]") return
      onToken(data)
    }
  }
}
