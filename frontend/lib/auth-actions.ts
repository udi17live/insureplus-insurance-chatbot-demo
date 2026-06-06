"use server"

import { cookies } from "next/headers"
import { serverApi } from "@/lib/api"

interface UserOut {
  id: string
  email: string
  full_name: string | null
}

interface AuthResponse {
  access_token: string
  token_type: string
  user: UserOut
}

async function setAuthCookie(token: string) {
  const isProd = process.env.NODE_ENV === "production"
  const jar = await cookies()
  jar.set("access_token", token, {
    httpOnly: true,
    secure: isProd,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60,
  })
}

export async function loginAction(email: string, password: string): Promise<UserOut> {
  const { data } = await serverApi.post<AuthResponse>("/auth/login", { email, password })
  await setAuthCookie(data.access_token)
  return data.user
}

export async function registerAction(
  email: string,
  password: string,
  full_name: string
): Promise<UserOut> {
  const { data } = await serverApi.post<AuthResponse>("/auth/register", {
    email,
    password,
    full_name,
  })
  await setAuthCookie(data.access_token)
  return data.user
}

export async function logoutAction(): Promise<void> {
  const jar = await cookies()
  jar.delete("access_token")
}
