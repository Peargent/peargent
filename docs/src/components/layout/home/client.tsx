'use client';
import { type ComponentProps, Fragment, useState } from 'react';
import { cva } from 'class-variance-authority';
import Link from 'fumadocs-core/link';
import { cn } from '../../../lib/cn';
import { BaseLinkItem, LinkItemType } from '../shared/index';
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  NavigationMenuViewport,
} from '../../navigation-menu';
import { useNav } from 'fumadocs-ui/contexts/layout';
import { buttonVariants } from '../../ui/button';

export const navItemVariants = cva('[&_svg]:size-5', {
  variants: {
    variant: {
      main: 'inline-flex items-center gap-1.5 px-3 py-2 text-base font-medium text-gray-900 transition-colors hover:text-gray-600 data-[active=true]:text-blue-600',
      button: buttonVariants({
        color: 'secondary',
        className: 'gap-1.5 text-base font-medium text-gray-900',
      }),
      icon: buttonVariants({
        color: 'ghost',
        size: 'icon',
        className: 'w-10 h-10 [&_svg]:size-5 text-gray-900 hover:text-gray-600',
      }),
    },
  },
  defaultVariants: {
    variant: 'main',
  },
});

export function Navbar(props: ComponentProps<'div'>) {
  const [value, setValue] = useState('');
  const { isTransparent } = useNav();

  return (
    <NavigationMenu value={value} onValueChange={setValue} asChild>
      <header
        id="nd-nav"
        {...props}
        className={cn(
          'fixed top-4 z-40 left-4 right-4 mx-auto max-w-7xl backdrop-blur-lg border-gray-200 border rounded-2xl transition-all duration-300 shadow-lg',
          value.length > 0 && 'max-lg:shadow-xl',
          (!isTransparent || value.length > 0) && 'bg-white/80',
          props.className,
        )}
      >
        <NavigationMenuList
          className="flex h-14 w-full items-center px-6"
          asChild
        >
          <nav>{props.children}</nav>
        </NavigationMenuList>

        <NavigationMenuViewport />
      </header>
    </NavigationMenu>
  );
}

export { NavigationMenuItem };

export function NavigationMenuLinkItem({
  item,
  ...props
}: {
  item: LinkItemType;
  className?: string;
}) {
  if (item.type === 'custom') return <div {...props}>{item.children}</div>;

  if (item.type === 'menu') {
    const children = item.items.map((child, j) => {
      if (child.type === 'custom') {
        return <Fragment key={j}>{child.children}</Fragment>;
      }

      const {
        banner = child.icon ? (
          <div className="w-fit rounded-md border border-gray-200 bg-gray-100 p-1 [&_svg]:size-4">
            {child.icon}
          </div>
        ) : null,
        ...rest
      } = child.menu ?? {};

      return (
        <NavigationMenuLink key={`${j}-${child.url}`} asChild>
          <Link
            href={child.url}
            external={child.external}
            {...rest}
            className={cn(
              'flex flex-col gap-2 rounded-lg border border-gray-200 bg-white p-3 transition-colors hover:bg-gray-50 hover:text-gray-900',
              rest.className,
            )}
          >
            {rest.children ?? (
              <>
                {banner}
                <p className="text-[15px] font-medium text-gray-900">{child.text}</p>
                <p className="text-sm text-gray-500 empty:hidden">
                  {child.description}
                </p>
              </>
            )}
          </Link>
        </NavigationMenuLink>
      );
    });

    return (
      <NavigationMenuItem {...props}>
        <NavigationMenuTrigger className={cn(navItemVariants(), 'rounded-md')}>
          {item.url ? (
            <Link href={item.url} external={item.external}>
              {item.text}
            </Link>
          ) : (
            item.text
          )}
        </NavigationMenuTrigger>
        <NavigationMenuContent className="grid grid-cols-1 gap-2 p-4 md:grid-cols-2 lg:grid-cols-3">
          {children}
        </NavigationMenuContent>
      </NavigationMenuItem>
    );
  }

  return (
    <NavigationMenuItem {...props}>
      <NavigationMenuLink asChild>
        <BaseLinkItem
          item={item}
          aria-label={item.type === 'icon' ? item.label : undefined}
          className={cn(navItemVariants({ variant: item.type }))}
        >
          {item.type === 'icon' ? item.icon : item.text}
        </BaseLinkItem>
      </NavigationMenuLink>
    </NavigationMenuItem>
  );
}

export function MobileNavigationMenuLinkItem({
  item,
  ...props
}: {
  item: LinkItemType;
  className?: string;
}) {
  if (item.type === 'custom')
    return <div className={cn('grid', props.className)}>{item.children}</div>;

  if (item.type === 'menu') {
    const header = (
      <>
        {item.icon}
        {item.text}
      </>
    );

    return (
      <div className={cn('mb-4 flex flex-col', props.className)}>
        <p className="mb-1 text-sm text-gray-500">
          {item.url ? (
            <NavigationMenuLink asChild>
              <Link href={item.url} external={item.external}>
                {header}
              </Link>
            </NavigationMenuLink>
          ) : (
            header
          )}
        </p>
        {item.items.map((child, i) => (
          <MobileNavigationMenuLinkItem key={i} item={child} />
        ))}
      </div>
    );
  }

  return (
    <NavigationMenuLink asChild>
      <BaseLinkItem
        item={item}
        className={cn(
          {
            main: 'inline-flex items-center gap-2 py-1.5 text-gray-900 transition-colors hover:text-gray-500 data-[active=true]:font-medium data-[active=true]:text-blue-600 [&_svg]:size-4',
            icon: buttonVariants({
              size: 'icon',
              color: 'ghost',
              className: 'text-gray-900 hover:text-gray-600',
            }),
            button: buttonVariants({
              color: 'secondary',
              className: 'gap-1.5 [&_svg]:size-4 text-gray-900',
            }),
          }[item.type ?? 'main'],
          props.className,
        )}
        aria-label={item.type === 'icon' ? item.label : undefined}
      >
        {item.icon}
        {item.type === 'icon' ? undefined : item.text}
      </BaseLinkItem>
    </NavigationMenuLink>
  );
}

export function MobileNavigationMenuTrigger({
  enableHover = false,
  ...props
}: ComponentProps<typeof NavigationMenuTrigger> & {
  /**
   * Enable hover to trigger
   */
  enableHover?: boolean;
}) {
  return (
    <NavigationMenuTrigger
      {...props}
      onPointerMove={enableHover ? undefined : (e) => e.preventDefault()}
    >
      {props.children}
    </NavigationMenuTrigger>
  );
}

export function MobileNavigationMenuContent(
  props: ComponentProps<typeof NavigationMenuContent>,
) {
  return (
    <NavigationMenuContent
      {...props}
      className={cn('flex flex-col p-4', props.className)}
    >
      {props.children}
    </NavigationMenuContent>
  );
}
