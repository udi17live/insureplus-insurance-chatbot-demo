"use server"

import { cookies } from "next/headers"
import api from "@/lib/api"

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

function setAuthCookie(token: string) {
  const isProd = process.env.NODE_ENV === "production"
  cookies().set("access_token", token, {
    httpOnly: true,
    secure: isProd,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60,
  })
}

export async function loginAction(email: string, password: string): Promise<UserOut> {
  const { data } = await api.post<AuthResponse>("/auth/login", { email, password })
  setAuthCookie(data.access_token)
  return data.user
}

export async function registerAction(
  email: string,
  password: string,
  full_name: string
): Promise<UserOut> {
  const { data } = await api.post<AuthResponse>("/auth/register", {
    email,
    password,
    full_name,
  })
  setAuthCookie(data.access_token)
  return data.user
}

export async function logoutAction(): Promise<void> {
  cookies().delete("access_token")
}
