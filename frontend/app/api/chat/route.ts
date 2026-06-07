import { cookies } from "next/headers"
import { NextRequest } from "next/server"

const BACKEND_URL = process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_API_URL ?? ""

export async function POST(req: NextRequest) {
  const jar = await cookies()
  const token = jar.get("access_token")?.value

  console.log("[chat proxy] token present:", !!token, "| BACKEND_URL:", BACKEND_URL)

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const body = await req.text()

  const upstream = await fetch(`${BACKEND_URL}/chat/message`, {
    method: "POST",
    headers,
    body,
  })

  console.log("[chat proxy] upstream status:", upstream.status)

  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  })
}
