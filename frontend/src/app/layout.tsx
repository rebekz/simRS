import type { Metadata } from "next";
import { Plus_Jakarta_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const plus_jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta",
  display: "swap",
});

const ibm_plex = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-ibm-plex",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SIMRS - Sistem Informasi Manajemen Rumah Sakit",
  description: "Sistem Informasi Manajemen Rumah Sakit untuk fasilitas kesehatan Indonesia",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className={`${plus_jakarta.variable} ${ibm_plex.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
