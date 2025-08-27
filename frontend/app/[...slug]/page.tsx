import { cache } from "react";
import { notFound } from "next/navigation";
import Typography from "@mui/material/Typography";
import { ROOT_SLUG } from "../constants";
import Stack from "@mui/material/Stack";
import { TPage, TPageDetailed, TPageResults } from "../type";
import { getRelativeUrl } from "../utils";
import WagtailBreadcrumbs from "./WagtailBreadcrumbs";
import ChildrenCards from "./ChildrenCards";

function djangoFetch(relativeUrl: string, init?: RequestInit) {
  return fetch(`http://django:8000${relativeUrl}`, {
    ...init,
    headers: {
        ...init?.headers,
        "Content-Type": "application/json",
    },
    next: { revalidate: 60 },
  });
}

async function djangoFetchData<T>(relativeUrl: string): Promise<T> {
  const response = await djangoFetch(relativeUrl);
  if (!response.ok) {
    notFound();
  }
  return await response.json();
}

async function fetchPages<T = TPage>(
  relativeUrl: string,
): Promise<TPageResults<T>> {
  return await djangoFetchData<TPageResults<T>>(relativeUrl);
}

const getPageData = cache(async function getPageData({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}): Promise<TPageDetailed> {
  let { slug } = await params;
  if (slug.length < 1 || slug[0] !== ROOT_SLUG) {
    notFound();
  } else {
    slug = slug.slice(1);
  }
  const wagtailUrl = `/${(slug ?? []).join("/")}`;
  const redirectResponse = await djangoFetch(
    `/api/pages/find/?html_path=${wagtailUrl}`,
    {
      redirect: "manual",
    },
  );
  if (redirectResponse.status !== 302) {
    notFound();
  }
  const relativeUrl = getRelativeUrl(
    redirectResponse.headers.get("location") ?? "",
  );
  return await djangoFetchData<TPageDetailed>(relativeUrl);
});

type TProps = { params: Promise<{ slug: string[] }> };

export async function generateMetadata({ params }: TProps) {
  const pageData = await getPageData({ params });
  return {
    title: pageData.meta.seo_title || pageData.title,
    description: pageData.meta.search_description,
  };
}

export default async function WagtailPage({ params }: TProps) {
  const pageData = await getPageData({ params });
  const childrenData = await fetchPages<
    TPage & { meta: { search_description: string } }
  >(`/api/pages/?child_of=${pageData.id}&fields=search_description`);
  return (
    <Stack spacing={4}>
      <WagtailBreadcrumbs pageData={pageData} />
      <Typography variant="h1">{pageData.title}</Typography>
      <ChildrenCards childrenData={childrenData.items} />
    </Stack>
  );
}
