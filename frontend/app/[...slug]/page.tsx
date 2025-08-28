import { cache } from "react";
import { notFound } from "next/navigation";
import Typography from "@mui/material/Typography";
import { ROOT_SLUG } from "../constants";
import Stack from "@mui/material/Stack";
import { EPageType, TFindPage, TPage, TPageDetailed } from "../types";
import {
  djangoFetch,
  djangoFetchData,
  fetchPages,
  getRelativeUrl,
  safeParseInt,
} from "../utils";
import WagtailBreadcrumbs from "./WagtailBreadcrumbs";
import ChildrenCards from "./ChildrenCards";
import dynamic from "next/dynamic";
import Container from "@mui/material/Container";

const Letter = dynamic(() => import("./Letter"));

const findPage = cache(async function findPage({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}): Promise<TFindPage> {
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
  return {
    id: safeParseInt(redirectResponse.headers.get("X-Page-Id")),
    apiUrl: getRelativeUrl(redirectResponse.headers.get("location") ?? ""),
    type: (redirectResponse.headers.get("X-Page-Type") ??
      "wagtailcore.Page") as EPageType,
    title: redirectResponse.headers.get("X-Page-Title") ?? "",
    description: redirectResponse.headers.get("X-Page-Description") ?? "",
  };
});

type TProps = { params: Promise<{ slug: string[] }> };

export async function generateMetadata({ params }: TProps) {
  const { title, description } = await findPage({ params });
  return { title, description };
}

export default async function WagtailPage({ params }: TProps) {
  const findPageData = await findPage({ params });
  switch (findPageData.type) {
    case EPageType.LETTER:
      return <Letter findPageData={findPageData} />;
  }

  const [pageData, childrenData] = await Promise.all([
    djangoFetchData<TPageDetailed>(findPageData.apiUrl),
    await fetchPages<TPage & { meta: { search_description: string } }>(
      `/api/pages/?child_of=${findPageData.id}&fields=search_description`,
    ),
  ]);
  return (
    <Container>
      <Stack spacing={4}>
        <WagtailBreadcrumbs pageData={pageData} />
        <Typography variant="h1">{pageData.title}</Typography>
        <ChildrenCards childrenData={childrenData.items} />
      </Stack>
    </Container>
  );
}
