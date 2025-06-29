import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"
import { $fetchClientV1 } from "./api/api-v1"
import type { JWT } from "next-auth/jwt"
import type { Session } from "next-auth"

// Extend the built-in types for NextAuth.js
declare module "next-auth" {
  interface User {
    id: string
    name?: string
    email?: string
    image?: string
    access_token?: string
    refresh_token?: string
    token_type?: string
  }

  interface Session {
    user?: User
    access_token?: string
    refresh_token?: string
    token_type?: string
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    access_token?: string
    refresh_token?: string
    token_type?: string
  }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      // You can specify which fields should be submitted, by adding keys to the `credentials` object.
      // e.g. domain, username, password, 2FA token, etc.
      credentials: {
        email: {},
        password: {},
      },
      authorize: async (credentials) => {
        try {
          const response = await $fetchClientV1.POST('/login', {
              body: {
                  email: credentials.email as string,
                  password: credentials.password as string,
              }
          })
          
          if (response.data) {
              // Transform the token response into a User object
              const tokenData = response.data
              
              // Create a User object with required id and optional properties
              const user = {
                id: credentials.email as string, // Using email as ID or you could use a JWT claim
                email: credentials.email as string,
                // Store tokens in the user object to access them later
                access_token: tokenData.access_token,
                refresh_token: tokenData.refresh_token,
                token_type: tokenData.token_type
              }
              
              return user
          }
          
          return null
        } catch (error) {
          console.error('Authentication error:', error)
          return null
        }
      },
    }),
  ],
  session:{
    strategy: "jwt",
    maxAge: 60 * 60 * 24 * 30
  },
  pages:{
    signIn: "/login",
  },
  callbacks: {
    // Add this to include the tokens in the JWT
    jwt: async ({ token, user }) => {
      if (user) {
        // Add user tokens to the JWT
        token.access_token = user.access_token
        token.refresh_token = user.refresh_token
        token.token_type = user.token_type
      }
      return token
    },
    // Add this to include the tokens in the session
    session: async ({ session, token }) => {
          if (token) {
        // Add token data to the session
        session.access_token = token.access_token
        session.refresh_token = token.refresh_token
        session.token_type = token.token_type
      }
      return session
    }
  }
})