"use client"

import { useState } from "react"
import { useTheme } from "next-themes"
import { Sun, Moon, LogIn, LogOut, Loader2, SquarePen } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuthStore } from "@/lib/auth-store"
import { logoutAction } from "@/lib/auth-actions"

function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme()
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
      aria-label="Toggle theme"
    >
      <Sun className="h-4 w-4 dark:hidden" />
      <Moon className="hidden h-4 w-4 dark:block" />
    </Button>
  )
}

interface HeaderProps {
  onLoginClick?: () => void
  onNewChat?: () => void
  onLogout?: () => void
}

export function Header({ onLoginClick, onNewChat, onLogout }: HeaderProps) {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const [loggingOut, setLoggingOut] = useState(false)

  async function handleLogout() {
    setLoggingOut(true)
    try {
      await logoutAction()
      logout()
      onLogout?.()
    } finally {
      setLoggingOut(false)
    }
  }

  return (
    <header className="border-b">
      <div className="mx-auto grid h-14 max-w-225 grid-cols-3 items-center px-4">
        <div className="flex items-center gap-1">
          <ThemeToggle />
          {onNewChat && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onNewChat}
              aria-label="New chat"
              className="gap-1.5"
            >
              <SquarePen className="h-4 w-4" />
              New chat
            </Button>
          )}
        </div>
        <div className="flex justify-center">
          <span className="font-heading font-bold tracking-widest uppercase">
            InsurePlus
          </span>
        </div>
        <div className="flex items-center justify-end gap-2">
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="text-xs">
                      {(user.full_name ?? user.email).slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <div className="px-2 py-1.5 text-sm">
                  {user.full_name && (
                    <p className="font-medium">{user.full_name}</p>
                  )}
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="text-destructive"
                  disabled={loggingOut}
                  onClick={handleLogout}
                >
                  {loggingOut ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <LogOut className="mr-2 h-4 w-4" />
                  )}
                  {loggingOut ? "Signing out…" : "Sign out"}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button variant="outline" size="sm" onClick={onLoginClick}>
              <LogIn className="mr-2 h-4 w-4" />
              Login
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
