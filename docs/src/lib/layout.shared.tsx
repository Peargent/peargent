import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export function baseOptions(disableThemeSwitch = false): BaseLayoutProps {
  return {
    nav: {
      title: <span className="font-semibold text-fd-foreground flex items-center lg:mb-5" style={{ fontFamily: 'var(--font-instrument-serif), serif', fontSize: '2.1rem', lineHeight: '1' }}>
        peargent.
      </span>,
      transparentMode: 'always',

    },
    links: [
      // {
      //   text: 'Docs',
      //   url: '/docs',
      // },
      // {
      //   text: 'GitHub',
      //   url: 'https://github.com/quanta-naut/peargent',
      //   external: true,
      // },
    ],
  };
}
