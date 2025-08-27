import { cache } from "react";
import { notFound } from "next/navigation";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActionArea from "@mui/material/CardActionArea";
import MuiLink from "@mui/material/Link";
import Link from "next/link";
import Breadcrumbs from "@mui/material/Breadcrumbs";
import { ROOT_SLUG } from "../constants";
import Stack from "@mui/material/Stack";
import HomeIcon from "@mui/icons-material/Home";
import Grid from "@mui/material/Grid";

enum EPageType {
  LETTER_INDEX = "correspondence.LetterIndex",
  LETTER_CORPUS = "correspondence.LetterCorpus",
  LETTER = "correspondence.Letter",
}

type TPage = {
  id: number;
  meta: {
    type: EPageType;
    detail_url: string;
    html_url: string;
    slug: string;
    first_published_at: string;
  };
  title: string;
};

type TPageDetailed = Omit<TPage, "meta"> & {
  meta: TPage["meta"] & {
    show_in_menus: boolean;
    seo_title: string;
    search_description: string;
  };
};

type TPageResults<T = TPage> = {
  meta: {
    total_count: number;
  };
  items: T[];
};

function djangoFetch(relativeUrl: string, init?: RequestInit) {
  return fetch(`http://django:8000${relativeUrl}`, init);
}

function getRelativeUrl(absoluteUrl: string): string {
  return new URL(absoluteUrl).pathname;
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
  const jsonResponse = await djangoFetch(relativeUrl);
  if (!jsonResponse.ok) {
    notFound();
  }
  return (await jsonResponse.json()) as TPageDetailed;
});

type TProps = { params: Promise<{ slug: string[] }> };

export async function generateMetadata({ params }: TProps) {
  const pageData = await getPageData({ params });
  return {
    title: pageData.meta.seo_title || pageData.title,
    description: pageData.meta.search_description,
  };
}

async function getPagesData<T = TPage>(
  relativeUrl: string,
): Promise<TPageResults<T>> {
  const response = await djangoFetch(relativeUrl);
  return await response.json();
}

export default async function WagtailPage({ params }: TProps) {
  const pageData = await getPageData({ params });
  const pathname = getRelativeUrl(pageData.meta.html_url);
  const ancestorsData = await getPagesData(
    `/api/pages/?ancestor_of=${pageData.id}`,
  );
  const childrenData = await getPagesData<
    TPage & { meta: { search_description: string } }
  >(`/api/pages/?child_of=${pageData.id}&fields=search_description`);
  return (
    <Stack spacing={4}>
      {ancestorsData.items.length > 0 ? (
        <Breadcrumbs>
          {ancestorsData.items.map(({ id, title }, index) => (
            <MuiLink
              key={id}
              component={Link}
              href={`/${ROOT_SLUG}/${pathname
                .split("/")
                .slice(1, index + 1)
                .join("/")}`}
              prefetch={false}
              underline="hover"
            >
              <Stack direction="row" spacing={0.5}>
                {index === 0 ? <HomeIcon /> : null}
                <Typography>{title}</Typography>
              </Stack>
            </MuiLink>
          ))}
          <Typography>{pageData.title}</Typography>
        </Breadcrumbs>
      ) : null}
      <Typography variant="h1">{pageData.title}</Typography>
      <Grid container>
        {childrenData.items.map(
          ({ id, title, meta: { slug, search_description } }) => (
            <Grid key={id} size={{ xs: 12, sm: 6, lg: 4 }}>
              <Card>
                <CardActionArea component={Link} href={slug} prefetch={false}>
                  <CardContent>
                    <Stack spacing={2}>
                      <Typography variant="h2">{title}</Typography>
                      {search_description ? (
                        <Typography variant="body2">
                          {search_description}
                        </Typography>
                      ) : null}
                    </Stack>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ),
        )}
      </Grid>
    </Stack>
  );
}
