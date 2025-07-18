import type { Metadata } from "next";
import React from "react";
import TrpcProvider from '@/lib/trpc/provider';
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";


export const metadata: Metadata = {
  title: "GEO2Reports",
  description: "A platform for generating reports from GEO datasets.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <TrpcProvider>
          <div className="flex flex-col min-h-screen">
            <React.Suspense fallback={null}>
              <Header />
              <main className="container mx-auto flex flex-col grow gap-4 my-4">
                {children}
              </main>
              <Footer />
            </React.Suspense>
          </div>
        </TrpcProvider>
      </body>
    </html>
  );
}
