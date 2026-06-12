import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "Family Budget Assistant",
  description: "AI-powered family shopping optimizer for Bulgaria",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="bg">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
