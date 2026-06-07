"use client"

import * as React from "react"
import ReactMarkdown from "react-markdown"
import { Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Header } from "@/components/header"
import { AuthDialog } from "@/components/auth-dialog"
import { streamChat, type ToolResultEvent } from "@/lib/chat"
import { PoliciesCard, QuoteCard, PolicyCard, type PolicyResult, type QuoteResult } from "@/components/tool-cards"
import { cn } from "@/lib/utils"

type MessageContent =
  | { type: "text"; text: string; options?: string[] }
  | { type: "policies"; data: PolicyResult[] }
  | { type: "quote"; data: QuoteResult; confirmed?: boolean }
  | { type: "policy"; data: PolicyResult }

interface Message {
  id: string
  role: "user" | "assistant"
  content: MessageContent
}

const STORAGE_KEY = "insureplus_chat"
const OPTIONS_RE = /\[OPTIONS:\s*([^\]]+)\]/i

function parseOptions(text: string): { clean: string; options: string[] } {
  const match = text.match(OPTIONS_RE)
  if (!match) return { clean: text, options: [] }
  const options = match[1].split("|").map((s) => s.trim()).filter(Boolean)
  return { clean: text.replace(OPTIONS_RE, "").trimEnd(), options }
}

function loadSession(): { messages: Message[]; threadId: string | null } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return { messages: [], threadId: null }
}

function saveSession(messages: Message[], threadId: string | null) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ messages, threadId }))
  } catch {}
}

function MessageBubble({
  m,
  isLast,
  streaming,
  onOption,
  onConfirm,
  onCancel,
}: {
  m: Message
  isLast: boolean
  streaming: boolean
  onOption: (opt: string) => void
  onConfirm: (quoteId: string) => void
  onCancel: (policyId: string) => Promise<void> | void
}) {
  const isUser = m.role === "user"

  if (m.content.type === "policies") {
    return (
      <div className="flex justify-start">
        <div className="w-full max-w-[85%]">
          <PoliciesCard policies={m.content.data} onCancel={onCancel} />
        </div>
      </div>
    )
  }

  if (m.content.type === "quote") {
    const { data: quoteData, confirmed } = m.content
    return (
      <div className="flex justify-start">
        <div className="w-full max-w-[85%]">
          <QuoteCard
            quote={quoteData}
            onConfirm={confirmed ? undefined : () => onConfirm(quoteData.quote_id)}
            onDecline={confirmed ? undefined : () => onOption("decline")}
          />
        </div>
      </div>
    )
  }

  if (m.content.type === "policy") {
    return (
      <div className="flex justify-start">
        <div className="w-full max-w-[85%]">
          <PolicyCard policy={m.content.data} />
        </div>
      </div>
    )
  }

  const { clean, options } = parseOptions(m.content.text)
  const showOptions = !isUser && isLast && !streaming && options.length > 0

  return (
    <div className={cn("flex flex-col", isUser ? "items-end" : "items-start")}>
      <div
        className={cn(
          "max-w-[75%] rounded-sm px-4 py-2.5 text-sm",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
        )}
      >
        {clean ? (
          isUser ? (
            clean
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-1 last:mb-0">{children}</p>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                ul: ({ children }) => <ul className="mb-1 ml-4 list-disc">{children}</ul>,
                ol: ({ children }) => <ol className="mb-1 ml-4 list-decimal">{children}</ol>,
                li: ({ children }) => <li className="mb-0.5">{children}</li>,
              }}
            >
              {clean}
            </ReactMarkdown>
          )
        ) : (
          <span className="text-muted-foreground animate-pulse">···</span>
        )}
      </div>
      {showOptions && (
        <div className="mt-2 flex flex-wrap gap-2">
          {options.map((opt) => (
            <button
              key={opt}
              onClick={() => onOption(opt)}
              className="rounded-full border border-border bg-background px-3 py-1.5 text-sm hover:bg-muted transition-colors"
            >
              {opt}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default function Page() {
  const [messages, setMessages] = React.useState<Message[]>([])
  const [input, setInput] = React.useState("")
  const [streaming, setStreaming] = React.useState(false)
  const [threadId, setThreadId] = React.useState<string | null>(null)
  const [authOpen, setAuthOpen] = React.useState(false)
  const pendingMessage = React.useRef<string | null>(null)
  const bottomRef = React.useRef<HTMLDivElement>(null)
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)
  const initialized = React.useRef(false)

  React.useEffect(() => {
    if (initialized.current) return
    initialized.current = true
    const session = loadSession()
    setMessages(session.messages)
    setThreadId(session.threadId)
  }, [])

  React.useEffect(() => {
    if (!initialized.current) return
    saveSession(messages, threadId)
  }, [messages, threadId])

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  function autoResize() {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }

  function startNewChat() {
    setMessages([])
    setThreadId(null)
    setInput("")
    if (textareaRef.current) textareaRef.current.style.height = "auto"
    localStorage.removeItem(STORAGE_KEY)
  }

  async function sendMessage(override?: string) {
    const text = override ?? input.trim()
    if (!text || streaming) return

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: { type: "text", text },
    }
    setMessages((prev) => [...prev, userMsg])
    if (!override) {
      setInput("")
      if (textareaRef.current) textareaRef.current.style.height = "auto"
    }
    setStreaming(true)

    const assistantId = crypto.randomUUID()
    setMessages((prev) => [
      ...prev,
      { id: assistantId, role: "assistant", content: { type: "text", text: "" } },
    ])

    function handleToolResult(event: ToolResultEvent) {
      if (event.tool === "agent_list_policies") {
        const policies = event.result as PolicyResult[]
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "assistant", content: { type: "policies", data: policies } },
        ])
      } else if (event.tool === "agent_create_quote") {
        const quote = event.result as QuoteResult
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "assistant", content: { type: "quote", data: quote } },
        ])
      } else if (event.tool === "agent_confirm_payment" || event.tool === "agent_cancel_policy") {
        const policy = event.result as PolicyResult
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "assistant", content: { type: "policy", data: policy } },
        ])
      }
    }

    try {
      await streamChat({
        message: text,
        threadId,
        onThread: (id) => setThreadId(id),
        onToken: (token) =>
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId && m.content.type === "text"
                ? { ...m, content: { type: "text", text: m.content.text + token } }
                : m
            )
          ),
        onToolResult: handleToolResult,
        onAuthRequired: () => {
          pendingMessage.current = text
          setMessages((prev) => prev.filter((m) => m.id !== assistantId))
          setAuthOpen(true)
        },
      })
    } finally {
      setStreaming(false)
    }
  }

  function handleConfirmQuote(quoteId: string) {
    setMessages((prev) =>
      prev.map((m) =>
        m.content.type === "quote" && m.content.data.quote_id === quoteId
          ? { ...m, content: { type: "quote" as const, data: m.content.data, confirmed: true } }
          : m
      )
    )
    sendMessage("yes, please confirm my quote and create the policy")
  }

  function handleCancelPolicy(policyId: string) {
    sendMessage(`please cancel policy ${policyId}`)
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const lastIdx = messages.length - 1

  return (
    <div className="flex h-svh flex-col">
      <Header onLoginClick={() => setAuthOpen(true)} onNewChat={messages.length > 0 ? startNewChat : undefined} onLogout={startNewChat} onMyPolicies={() => sendMessage("show my policies")} />
      <AuthDialog
        open={authOpen}
        onOpenChange={setAuthOpen}
        onSuccess={() => {
          const msg = pendingMessage.current
          if (msg) {
            pendingMessage.current = null
            sendMessage(msg)
          }
        }}
      />
      <main className="mx-auto flex w-full max-w-225 flex-1 flex-col overflow-hidden px-4">
        <div className="flex-1 overflow-y-auto py-6">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <p className="text-muted-foreground text-sm">
                Ask anything about your insurance needs.
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-6">
              {messages.map((m, i) => (
                <MessageBubble
                  key={m.id}
                  m={m}
                  isLast={i === lastIdx}
                  streaming={streaming}
                  onOption={(opt) => sendMessage(opt)}
                  onConfirm={handleConfirmQuote}
                  onCancel={handleCancelPolicy}
                />
              ))}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        <div className="border-t py-4">
          <div className="flex items-center gap-2 rounded-sm border bg-background px-3 py-2">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={(e) => { setInput(e.target.value); autoResize() }}
              onKeyDown={onKeyDown}
              placeholder="Message InsurePlus..."
              disabled={streaming}
              className="flex-1 resize-none bg-transparent py-1 text-sm leading-normal outline-none placeholder:text-muted-foreground disabled:opacity-50"
            />
            <Button
              size="icon"
              onClick={() => sendMessage()}
              disabled={!input.trim() || streaming}
              className="shrink-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="mt-2 text-center text-xs text-muted-foreground">
            InsurePlus can make mistakes. Verify important information.
          </p>
        </div>
      </main>
    </div>
  )
}
