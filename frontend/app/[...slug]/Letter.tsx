import Stack from "@mui/material/Stack";
import {
  EBlockType,
  EModelType,
  TBlock,
  TFindPage,
  TImage,
  TPageDetailed,
  TRelated,
  TRelatedPerson,
} from "../types";
import WagtailBreadcrumbs from "./WagtailBreadcrumbs";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { djangoFetchData } from "../utils";
import { INDIVIDU_FIELDS } from "../constants";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import Image from "next/image";
import PersonLink from "./PersonChip";

export default async function Letter({
  findPageData,
}: {
  findPageData: TFindPage;
}) {
  const pageData = await djangoFetchData<
    TPageDetailed & {
      sender: TRelatedPerson;
      recipients: (TRelated<EModelType.LETTER_RECIPIENT> & {
        person: TRelatedPerson;
      })[];
      writing_lieu: TRelated<EModelType.LIEU>;
      writing_lieu_approx: string;
      writing_date: string;
      writing_date_approx: string;
      letter_images: (TRelated<EModelType.LETTER_IMAGE> & {
        name: string;
        image: TImage;
        thumbnail: TImage;
        references: TBlock<EBlockType.LIEU>[];
      })[];
      transcription: string;
      description: string;
    }
  >(
    `${findPageData.apiUrl}?fields=sender(${INDIVIDU_FIELDS}),recipients(person(${INDIVIDU_FIELDS}))`,
  );
  const { title, sender, recipients, letter_images } = pageData;
  return (
    <Grid container direction="column">
      <Grid>
        <Container>
          <Stack spacing={4}>
            <WagtailBreadcrumbs pageData={pageData} />
            <Typography variant="h1">{title}</Typography>
          </Stack>
        </Container>
      </Grid>
      <Grid>
        <Container>
          <Stack spacing={1}>
            <Typography>
              Expéditeur : <PersonLink {...sender} />
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Typography>Destinataires :</Typography>
              {recipients.map(({ person }) => (
                <PersonLink key={person.id} {...person} />
              ))}
            </Stack>
          </Stack>
          {letter_images.map(
            ({ id, image: { full_url, width, height, alt } }) => (
              <Image
                key={id}
                src={full_url}
                width={width}
                height={height}
                alt={alt}
                unoptimized
              />
            ),
          )}
        </Container>
      </Grid>
    </Grid>
  );
}
