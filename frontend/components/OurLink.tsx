"use client";

import Link, { LinkProps } from "next/link";
import { usePathname } from "next/navigation";
import { useEffect } from "react";

export default function OurLink({
  href,
  children,
  scroll,
  ...props
}: Omit<LinkProps, "href"> & {
  href: string;
  children: React.ReactNode;
} & object) {
  const pathname = usePathname();
  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [pathname]);

  return (
    <Link href={href} prefetch={false} scroll={scroll} {...props}>
      {children}
    </Link>
  );
}
