"use client";

import Link, { LinkProps } from "next/link";

// The Next.js site only serves paths under the musicaLetters prefix; every other
// same-origin path (the authority catalogue, user profiles, the admin…) is served
// by the Django frontend. Client-side routing those through next/link would force
// a wasted RSC round-trip before falling back to a full load, so we render a plain
// anchor for them and reserve next/link for genuine in-app navigation.
function isInternal(href: string): boolean {
  return href.startsWith("/musicaletters") || href.startsWith("#");
}

export default function OurLink({
  href,
  children,
  scroll = true,
  ...props
}: Omit<LinkProps, "href"> & {
  href: string;
  children: React.ReactNode;
} & object) {
  if (!isInternal(href)) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    );
  }
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
