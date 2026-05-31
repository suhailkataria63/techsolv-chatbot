import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Social Video RAG",
  description: "Compare two social videos and prepare transcript chat context.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
