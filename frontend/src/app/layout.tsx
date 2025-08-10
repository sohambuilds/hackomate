import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Hackathon Twin",
  description: "AI agents for autonomous hackathons",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <div className="min-h-dvh relative">
          {/* Enhanced global background orbs */}
          <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
            <div className="absolute w-[800px] h-[800px] -top-40 -left-40 bg-gradient-to-br from-blue-500/8 via-cyan-500/6 to-indigo-500/4 rounded-full blur-3xl opacity-40 animate-pulse"></div>
            <div className="absolute w-[700px] h-[700px] top-1/4 -right-40 bg-gradient-to-bl from-purple-500/7 via-pink-500/5 to-rose-500/3 rounded-full blur-3xl opacity-35 animate-pulse" style={{animationDelay: '2s'}}></div>
            <div className="absolute w-[600px] h-[600px] -bottom-40 left-1/3 bg-gradient-to-tr from-emerald-500/6 via-teal-500/4 to-cyan-500/2 rounded-full blur-3xl opacity-30 animate-pulse" style={{animationDelay: '4s'}}></div>
            <div className="absolute w-[500px] h-[500px] top-2/3 left-1/4 bg-gradient-to-r from-violet-500/5 via-indigo-500/3 to-blue-500/2 rounded-full blur-3xl opacity-25 animate-pulse" style={{animationDelay: '6s'}}></div>
            <div className="absolute w-[400px] h-[400px] top-1/2 right-1/4 bg-gradient-to-l from-amber-500/4 via-orange-500/3 to-red-500/2 rounded-full blur-3xl opacity-20 animate-pulse" style={{animationDelay: '8s'}}></div>
          </div>
          <Nav />
          {children}
          <Footer />
        </div>
      </body>
    </html>
  );
}
