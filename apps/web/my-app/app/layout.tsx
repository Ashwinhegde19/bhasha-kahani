import type { Metadata } from "next";
import { Fredoka } from "next/font/google";
import { Providers } from "@/components/providers";
import { Navbar } from "@/components/layout";
import "./globals.css";

const fredoka = Fredoka({
  subsets: ["latin", "latin-ext"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-fredoka",
  display: "swap",
});

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
      <body className={`${fredoka.variable} font-sans antialiased min-h-screen bg-background`}>
        <Providers>
          <Navbar />
          {children}
        </Providers>
      </body>
    </html>
  );
}
