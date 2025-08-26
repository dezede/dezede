import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import CustomPagination from "./CustomPagination";
import Grid from "@mui/material/Grid";

function safeParseInt(
  str: string | string[] | undefined,
  defaultValue: number = 0,
): number {
  if (typeof str === "string") {
    if (/^\d+$/.test(str)) {
      return parseInt(str);
    }
  }
  return defaultValue;
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const pageParam = (await searchParams).page;
  const page = safeParseInt(pageParam, 1);
  const url = `https://dezede.org/api/sources/?page=${page}`;
  const sourcesResponse = await fetch(url);
  const sources: {
    count: number;
    results: {
      id: number;
      str: string;
      small_thumbnail: string;
      front_url: string;
    }[];
  } = await sourcesResponse.json();
  return (
    <div>
      {sources.results.map(({ id, str, small_thumbnail, front_url }) => (
        <Card key={id}>
          <CardActionArea component="a" href={front_url} target="_blank">
            <Grid container>
              {small_thumbnail !== url ? (
                <Grid size={2}>
                  <CardMedia component="img" image={small_thumbnail} />
                </Grid>
              ) : null}
              <Grid>
                <CardContent>
                  <Typography>{str}</Typography>
                </CardContent>
              </Grid>
            </Grid>
          </CardActionArea>
        </Card>
      ))}
      <CustomPagination count={sources.count} perPage={10} page={page} />
    </div>
  );
}
