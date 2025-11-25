import { RootProvider } from 'fumadocs-ui/provider/next';
import './global.css';
import { Inter, Instrument_Serif } from 'next/font/google';
import type { Metadata } from 'next';

const inter = Inter({
  subsets: ['latin'],
});

const instrumentSerif = Instrument_Serif({
  subsets: ['latin'],
  weight: ['400'],
});

export const metadata: Metadata = {
  metadataBase: new URL('https://peargent.online'),
  title: {
    template: '%s | Peargent',
    default: 'Peargent',
  },
  description: 'A modern, type-safe Python framework for building intelligent, production-grade AI agents.',
};

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen" style={{ '--font-instrument-serif': instrumentSerif.style.fontFamily } as React.CSSProperties}>
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  );
}
