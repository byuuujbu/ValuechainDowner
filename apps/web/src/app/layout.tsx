import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OVSA",
  description: "Objective Value-chain Stock Agent"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
