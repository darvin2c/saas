'use client'

import { useSession } from "next-auth/react"

export function AuthStatus() {
  const { data: session, status } = useSession()

  if (status === "loading") {
    return <div className="text-sm text-muted-foreground">Cargando sesión...</div>
  }

  if (status === "authenticated") {
    return (
      <div className="flex items-center gap-2">
        <div className="text-sm">
          <p className="font-medium">Autenticado como:</p>
          <p className="text-muted-foreground">{session.user?.email}</p>
        </div>
      </div>
    )
  }

  return <div className="text-sm text-muted-foreground">No autenticado</div>
}
