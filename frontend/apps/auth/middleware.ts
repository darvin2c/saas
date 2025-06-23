import { NextResponse } from 'next/server'
import { withAuth } from 'next-auth/middleware'

// Este middleware se ejecutará en las rutas especificadas en matcher
export default withAuth(
  // Función que se ejecuta en rutas protegidas
  function middleware(req) {
    return NextResponse.next()
  },
  {
    callbacks: {
      // Solo se ejecuta si el usuario está autenticado
      authorized: ({ token }) => !!token
    },
  }
)

// Especifica las rutas que requieren autenticación
export const config = {
  matcher: [
    // Rutas que requieren autenticación
    '/dashboard/:path*',
    '/profile/:path*',
    // Excluye las rutas de autenticación
    '/((?!api|_next/static|_next/image|favicon.ico|login|register).*)',
  ],
}
