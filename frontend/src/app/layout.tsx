import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'NexusCRM | AI-Powered Customer Relationship Management',
  description: 'NexusCRM is an AI-powered customer relationship management platform for modern teams.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 min-h-screen text-slate-900 antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
