import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Debate Engine | Multi-Agent Reasoning Arena",
  description: "A collaborative multi-agent debate system powered by LangGraph, featuring evidence retrieval, fallacy detection, and automated scoring.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>
        <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
          <header className="glass">
            <div className="container" style={{ height: "64px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <div style={{ 
                  width: "12px", 
                  height: "12px", 
                  borderRadius: "50%", 
                  backgroundColor: "var(--color-accent)",
                  boxShadow: "0 0 10px var(--color-accent)"
                }} />
                <span style={{ fontSize: "1.25rem", fontWeight: "700", letterSpacing: "-0.5px" }}>
                  AI <span style={{ color: "var(--color-accent)" }}>DEBATE</span> ENGINE
                </span>
              </div>
              <div style={{ display: "flex", gap: "20px", fontSize: "0.9rem", color: "var(--text-secondary)" }}>
                <span>Multi-Agent Reasoning System</span>
              </div>
            </div>
          </header>
          
          <main style={{ flex: "1", display: "flex", flexDirection: "column" }}>
            {children}
          </main>
          
          <footer style={{ borderTop: "1px solid var(--border-color)", padding: "20px 0", background: "rgba(7, 10, 19, 0.5)", fontSize: "0.85rem", color: "var(--text-muted)", textAlign: "center" }}>
            <div className="container">
              © {new Date().getFullYear()} AI Debate Engine — Powered by LangGraph, FastAPI & Next.js
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
