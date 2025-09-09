"use client";

import Link, { LinkProps } from "next/link";

export default function OurLink({
  href,
  children,
  scroll = true,
  ...props
}: Omit<LinkProps, "href"> & {
  href: string;
  children: React.ReactNode;
} & object) {
  return (
    <Link
      href={href}
      prefetch={false}
      scroll={scroll}
      onNavigate={() => {
        if (scroll) {
          window.scrollTo({ top: 0 });
        }
      }}
      {...props}
    >
      {children}
    </Link>
  );
}
