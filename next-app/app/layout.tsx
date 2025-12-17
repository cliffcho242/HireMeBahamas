import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/next";
import { Providers } from "@/lib/providers";
import "./globals.css";

// ✅ Font Optimization: Using next/font for automatic font optimization
// This provides zero layout shift and self-hosted fonts
const inter = Inter({ 
  subsets: ["latin"],
  display: "swap",
  fallback: ["system-ui", "-apple-system", "sans-serif"]
});

export const metadata: Metadata = {
  title: "Hire Me Bahamas",
  description: "Hire trusted professionals in the Bahamas",
  keywords: [
    "jobs",
    "bahamas",
    "employment",
    "hiring",
    "careers",
    "nassau",
    "freeport",
    "professionals",
  ],
  authors: [{ name: "HireMeBahamas Team" }],
  creator: "HireMeBahamas",
  publisher: "HireMeBahamas",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "Hire Me Bahamas",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://hiremebahamas.com",
    siteName: "Hire Me Bahamas",
    title: "Hire Me Bahamas",
    description: "Hire trusted professionals in the Bahamas",
    images: ["/og.png"],
  },
  twitter: {
    card: "summary_large_image",
    title: "Hire Me Bahamas",
    description: "Hire trusted professionals in the Bahamas",
    images: ["/og.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#0ea5e9" },
    { media: "(prefers-color-scheme: dark)", color: "#0f172a" },
  ],
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta
          name="apple-mobile-web-app-status-bar-style"
          content="black-translucent"
        />
      </head>
      <body className={`${inter.className} antialiased scroll-smooth`}>
        <Providers>
          {children}
          <Analytics />
          <SpeedInsights />
        </Providers>
      </body>
    </html>
  );
}
