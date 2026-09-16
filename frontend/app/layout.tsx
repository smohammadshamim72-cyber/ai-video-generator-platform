from __future__ import annotations

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Video Generator",
  description: "Long-form AI video generation dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
