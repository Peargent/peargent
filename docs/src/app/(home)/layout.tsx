import { HomeLayout } from 'fumadocs-ui/layouts/home';
import { baseOptions } from '@/lib/layout.shared';

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <div className="light">
      <HomeLayout {...baseOptions(true)}>
        {children}
      </HomeLayout>
    </div>
  );
}
