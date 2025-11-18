import { RootProvider } from 'fumadocs-ui/provider/next';
import './global.css';
import { Inter, Instrument_Serif } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
});

const instrumentSerif = Instrument_Serif({
  subsets: ['latin'],
  weight: ['400'],
});

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen" style={{ '--font-instrument-serif': instrumentSerif.style.fontFamily } as React.CSSProperties}>
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  );
}
