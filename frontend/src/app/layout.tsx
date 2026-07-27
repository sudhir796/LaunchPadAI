import type { Metadata } from "next";
import { Inter, Newsreader, IBM_Plex_Mono, Manrope } from "next/font/google";
import "./globals.css";
import { PipelineProvider } from "@/context/PipelineContext";
import { AnimatedCursor } from "@/components/AnimatedCursor";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const newsreader = Newsreader({
  variable: "--font-newsreader",
  subsets: ["latin"],
  display: "swap",
  style: ["normal", "italic"],
});

const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-ibm-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
});

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  weight: ["200", "400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "LaunchPad AI — Idea-to-Investor Accelerator",
  description: "An autonomous multi-agent pipeline validating, researching, and packaging student startup ideas into investor-ready pitch decks.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${newsreader.variable} ${ibmPlexMono.variable} ${manrope.variable} h-full antialiased`}
    >
      <body className={`min-h-full flex flex-col font-sans`}>
        <PipelineProvider>
          <AnimatedCursor />
          {children}
        </PipelineProvider>
      </body>
    </html>
  );
}

