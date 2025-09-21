import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import { LayoutWrapper } from "./_comps/layout-wrapper"
import { Suspense } from "react"

export const metadata: Metadata = {
  title: "SkinCare AI - Skin Cancer Detection",
  description: "Advanced AI-powered skin cancer detection and analysis",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable}`}>
        <Suspense fallback={<div>Loading...</div>}>
          <LayoutWrapper>{children}</LayoutWrapper>
        </Suspense>
        <Analytics />
      </body>
    </html>
  )
}
