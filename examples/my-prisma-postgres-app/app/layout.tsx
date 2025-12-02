import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'My Prisma Postgres App',
  description: 'Example Next.js app with Prisma Postgres',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
