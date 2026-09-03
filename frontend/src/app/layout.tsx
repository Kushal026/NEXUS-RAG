import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "../context/AuthContext";

export const metadata: Metadata = {
  title: "NEXUS — Evidence Intelligence for AI",
  description: "Advanced evidence-backed RAG and AI research platform for retrieving, connecting, verifying, and reasoning over complex information.",
  keywords: ["AI Research", "RAG", "Evidence Intelligence", "Knowledge Graph", "Neural Search", "Contradiction Detection"],
  authors: [{ name: "NEXUS Team" }],
  openGraph: {
    title: "NEXUS — Evidence Intelligence for AI",
    description: "Advanced evidence-backed RAG and AI research platform for retrieving, connecting, verifying, and reasoning over complex information.",
    siteName: "NEXUS",
    type: "website",
  },
};


export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col font-sans antialiased selection:bg-indigo-500/20 selection:text-indigo-800">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
