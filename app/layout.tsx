import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "MULTIMAKINA | Telemetría vehicular",
  description: "Panel de gestión, telemetría OBD-II y diagnóstico vehicular.",
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="es"><body>{children}</body></html>
}
