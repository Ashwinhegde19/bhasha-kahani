import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import { Navbar } from "@/components/layout";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bhasha Kahani - Multilingual Interactive Folktales",
  description: "Discover and enjoy interactive folktales in multiple Indian languages",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-background">
        <Providers>
          <Navbar />
          {children}
        </Providers>
      </body>
    </html>
  );
}
