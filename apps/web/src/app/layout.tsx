import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Twitch Ladder",
  description: "Local Twitch analytics for VODs, chat activity, and ladder rankings.",
  icons: {
    icon: "/icons/logo.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
