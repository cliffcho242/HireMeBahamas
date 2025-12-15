import type { Metadata, Viewport } from "next";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HireMeBahamas - Find Jobs in the Bahamas",
  description:
    "The fastest job platform in the Bahamas. Find your dream job or hire the perfect candidate in seconds.",
  keywords: [
    "jobs",
    "bahamas",
    "employment",
    "hiring",
    "careers",
    "nassau",
    "freeport",
  ],
  authors: [{ name: "HireMeBahamas Team" }],
  creator: "HireMeBahamas",
  publisher: "HireMeBahamas",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "HireMeBahamas",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://hiremebahamas.com",
    siteName: "HireMeBahamas",
    title: "HireMeBahamas - Find Jobs in the Bahamas",
    description:
      "The fastest job platform in the Bahamas. Find your dream job or hire the perfect candidate in seconds.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "HireMeBahamas",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "HireMeBahamas - Find Jobs in the Bahamas",
    description: "The fastest job platform in the Bahamas.",
    images: ["/og-image.png"],
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
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        {/* Preload critical resources for Facebook traffic optimization */}
        <link
          rel="preload"
          href="/_next/static/css/app/layout.css"
          as="style"
        />
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
      <body className="antialiased scroll-smooth">
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
