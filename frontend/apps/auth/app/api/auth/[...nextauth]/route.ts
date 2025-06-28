import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { NextAuthOptions } from "next-auth";

console.log(process.env.NEXT_PUBLIC_API_URL)

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          // Conectar con la API de autenticación
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          })

          const data = await response.json()

          if (!response.ok) {
            return null;
          }

          const userData = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me`, {
            headers: {
              'Authorization': `Bearer ${data.access_token}`,
            },
          })

          const user = await userData.json()

          // Retornar el usuario con los datos necesarios
          return {
            id: user.id,
            user: user,
            email: user.email,
            name: user.first_name ? `${user.first_name} ${user.last_name || ''}` : user.email,
            // Incluir el token de acceso para usarlo en llamadas a la API
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
            tokenType: data.token_type,
          };
        } catch (error) {
          console.error("Error durante la autenticación:", error);
          return null;
        }
      }
    }),
  ],
  pages: {
    signIn: '/login',
    signOut: '/',
    error: '/login', // Error code passed in query string as ?error=
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 días
  },
  callbacks: {
    async jwt({ token, user }) {
      // Añadir datos adicionales al token JWT si es necesario
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      // Enviar propiedades al cliente
      if (session.user) {
        session.user.id = token.id as string;
        session.accessToken = token.accessToken as string;
      }
      return session;
    },
  },
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
