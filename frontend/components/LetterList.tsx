import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import Stack from "@mui/material/Stack";
import OverflowContainer from "./OverflowContainer";
import Typography from "@mui/material/Typography";
import SpaceTime from "@/format/SpaceTime";
import { PersonLabel } from "@/format/PersonChip";
import {
  TLetter,
  TPageResults,
  TAsyncSearchParams,
  TRelatedPerson,
} from "@/app/types";
import { djangoFetchData, safeParseInt } from "@/app/utils";
import { INDIVIDU_FIELDS, PLACE_FIELDS } from "@/app/constants";
import Divider from "@mui/material/Divider";
import Empty from "./Empty";
import ImageRendition from "./ImageRendition";
import Box from "@mui/material/Box";
import OurLink from "./OurLink";

function PersonHorizontalList({ persons }: { persons: TRelatedPerson[] }) {
  return (
    <Stack
      display="inline-flex"
      direction="row"
      spacing={1}
      divider={<Divider orientation="vertical" flexItem />}
      flexWrap="wrap"
      useFlexGap
    >
      {persons.map((person) => (
        <strong key={person.id}>
          <PersonLabel {...person} />
        </strong>
      ))}
    </Stack>
  );
}

export default async function LetterList({
  parentPageId,
  searchParams,
  perPage = 10,
}: {
  parentPageId: number;
  searchParams: TAsyncSearchParams;
  perPage?: number;
}) {
  const {
    search,
    year,
    person,
    writing_place,
    tab,
    page: pageParam,
  } = await searchParams;
  const page = safeParseInt(pageParam, 1);
  const lettersData = await djangoFetchData<
    TPageResults<
      Omit<TLetter, "transcription" | "description"> & {
        transcription_text: string;
      }
    >
  >(
    `/api/correspondance/${parentPageId}/lettres/`,
    {
      search,
      year,
      person,
      writing_place,
      tab,
      offset: (page - 1) * perPage,
      limit: perPage,
    },
    [
      `senders(person(${INDIVIDU_FIELDS}))`,
      `recipients(person(${INDIVIDU_FIELDS}))`,
      `writing_lieu(${PLACE_FIELDS})`,
      "writing_lieu_approx",
      "writing_date",
      "writing_date_approx",
      "writing_heure",
      "writing_heure_approx",
      "letter_images(_,thumbnail)",
      "transcription_text",
    ],
  );
  if (lettersData.items.length === 0) {
    return <Empty>Aucune lettre ne correspond aux critères sélectionnés</Empty>;
  }
  return (
    <Stack spacing={2}>
      {lettersData.items.map(
        ({
          id,
          meta: { html_url },
          senders,
          recipients,
          writing_lieu,
          writing_lieu_approx,
          writing_date,
          writing_date_approx,
          writing_heure,
          writing_heure_approx,
          letter_images,
          transcription_text,
        }) => {
          return (
            <Card key={id}>
              <CardActionArea component={OurLink} href={html_url}>
                <Stack direction="row">
                  <Box display={{ xs: "none", sm: "block" }}>
                    {letter_images.length >= 1 ? (
                      <ImageRendition
                        rendition={letter_images[0].thumbnail}
                        style={{
                          display: "block",
                          minWidth: 200,
                          width: 200,
                          height: "auto",
                        }}
                      />
                    ) : (
                      <Empty
                        sx={{
                          minWidth: 200,
                          width: 200,
                          height: 200,
                        }}
                      >
                        Image manquante
                      </Empty>
                    )}
                  </Box>
                  <OverflowContainer
                    maxHeight={200}
                    overflowHeight={transcription_text ? 50 : 0}
                    sx={{ width: "100%" }}
                  >
                    <Stack
                      spacing={1}
                      divider={<Divider />}
                      p={2}
                      height="100%"
                    >
                      <Stack
                        direction={{ xs: "column", md: "row" }}
                        flexWrap="nowrap"
                        justifyContent="space-between"
                        spacing={2}
                      >
                        <Stack
                          direction="row"
                          spacing={1.5}
                          flexWrap="wrap"
                          useFlexGap
                        >
                          <Stack
                            direction="row"
                            spacing={1.5}
                            flexWrap="nowrap"
                          >
                            <Typography>De</Typography>
                            <PersonHorizontalList
                              persons={senders.map(({ person }) => person)}
                            />
                          </Stack>
                          {recipients.length === 0 ? null : (
                            <Stack
                              direction="row"
                              spacing={1.5}
                              flexWrap="nowrap"
                            >
                              <Typography>à</Typography>
                              <PersonHorizontalList
                                persons={recipients.map(({ person }) => person)}
                              />
                            </Stack>
                          )}
                        </Stack>
                        <SpaceTime
                          place={writing_lieu}
                          fuzzyPlace={writing_lieu_approx}
                          date={writing_date}
                          fuzzyDate={writing_date_approx}
                          time={writing_heure}
                          fuzzyTime={writing_heure_approx}
                          variant="body2"
                        />
                      </Stack>
                      {transcription_text ? (
                        <Typography textAlign="justify">
                          {transcription_text}
                        </Typography>
                      ) : (
                        <Empty sx={{ py: 0, height: "100%" }}>
                          Transcription manquante
                        </Empty>
                      )}
                    </Stack>
                  </OverflowContainer>
                </Stack>
              </CardActionArea>
            </Card>
          );
        },
      )}
    </Stack>
  );
}
