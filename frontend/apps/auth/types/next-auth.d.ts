import NextAuth from "next-auth";
import { operations } from "@/api/types/v1";

declare module "next-auth" {
  interface Session {
    id: string;
    email: string;
    name: string;
    image?: string;
    user: User;
    accessToken?: string;
    refreshToken?: string;
    tokenType?: string;
  }

  interface User extends operations['login_user_auth_login_post']['responses']['200']['content']['application/json']['user'] {}

}

declare module "next-auth/jwt" {
  interface JWT {
    id: string;
    email: string;
    name: string;
    image?: string;
    accessToken?: string;
    refreshToken?: string;
    tokenType?: string;
  }
}
