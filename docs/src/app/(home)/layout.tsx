import { HomeLayout } from '@/components/layout/home';

export default function Layout({ children }: LayoutProps<'/'>) {
  const homeOptions = {
    nav: {
      title: <span className="font-semibold text-gray-900" style={{ fontFamily: 'var(--font-instrument-serif), serif', fontSize: '2.1rem' }}>
        peargent.
      </span>,
      transparentMode: 'always' as 'always' | 'top' | 'none',
    },
    links: [
      {
        text: 'Docs',
        url: '/docs',
      },
      {
        text: 'GitHub',
        url: 'https://github.com/quanta-naut/peargent',
        external: true,
      },
    ],
  };

  return (
    <HomeLayout {...homeOptions}>
      {children}
    </HomeLayout>
  );
}
