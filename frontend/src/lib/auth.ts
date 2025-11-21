// lib/auth.ts
import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

// Helper function to get the correct API URL
const getApiBaseUrl = () => {
  // For server-side (Docker container), use the service name
  if (typeof window === 'undefined') {
    return process.env.API_BASE_URL || "http://backend:8000";
  }
  // For client-side (browser), use localhost
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
};

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          throw new Error("Missing credentials");
        }

        try {
          const apiBaseUrl = getApiBaseUrl();
          const loginUrl = `${apiBaseUrl}/api/v1/auth/login`;

          console.log("Attempting login to:", loginUrl);

          const response = await fetch(loginUrl, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              username: credentials.username,
              password: credentials.password,
            }),
          });

          console.log("Login response status:", response.status);

          if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            console.error("Login failed:", response.status, errorData);
            
            if (response.status === 401) {
              throw new Error("Invalid username or password");
            } else if (response.status === 500) {
              throw new Error("Server error. Please try again later.");
            } else {
              throw new Error(errorData?.detail || "Login failed");
            }
          }

          const data = await response.json();
          console.log("Login successful for user:", data.user?.username);

          if (data.access_token && data.user) {
            return {
              id: data.user.id.toString(),
              email: data.user.email,
              name: data.user.full_name || data.user.username,
              username: data.user.username,
              accessToken: data.access_token,
            };
          }

          console.log("No access token in response");
          throw new Error("Invalid response from server");
        } catch (error: any) {
          console.error("Login error:", error.message);
          throw new Error(error.message || "Login failed");
        }
      },
    }),
  ],

  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },

  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken;
        token.username = user.username;
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      session.user.id = token.id as string;
      session.user.username = token.username as string;
      session.user.name = token.name as string;
      session.user.email = token.email as string;
      return session;
    },
  },

  pages: {
    signIn: "/login",
    error: "/login",
  },

  secret: process.env.NEXTAUTH_SECRET,
  debug: process.env.NODE_ENV === "development",
};