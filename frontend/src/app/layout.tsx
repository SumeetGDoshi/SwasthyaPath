import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider } from "@/contexts/AuthContext";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

export const metadata: Metadata = {
  title: "Swasthya Path - Smart Healthcare Intelligence",
  description: "AI-powered medical report analysis and duplicate detection for Indian healthcare. Save money, save time.",
  keywords: ["healthcare", "medical reports", "AI", "duplicate detection", "India", "lab tests"],
  authors: [{ name: "Swasthya Path Team" }],
  openGraph: {
    title: "Swasthya Path - Smart Healthcare Intelligence",
    description: "AI-powered medical report analysis and duplicate detection",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#10b981",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <AuthProvider>
          <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50 dark:from-slate-950 dark:via-slate-900 dark:to-emerald-950">
            {children}
          </main>
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  );
}


