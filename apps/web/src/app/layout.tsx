import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OVSA",
  description: "객관식 밸류체인 주식 후보 검토 도구"
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
