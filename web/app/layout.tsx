import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Artify - Paris Cultural Events',
  description: 'Discover and explore cultural events in Paris',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <head>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}

