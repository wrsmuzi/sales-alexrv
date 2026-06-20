import './globals.css';
import type { Metadata } from 'next';
import Navbar from './Navbar';

export const metadata: Metadata = {
  title: 'AlexRV-Dev Sales Engine',
  description: 'AI-powered high-ticket client acquisition',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-dubai-dark text-white">
        <Navbar />
        {children}
      </body>
    </html>
  );
}
