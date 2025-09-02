import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import Stack from "@mui/material/Stack";
import OverflowContainer from "./OverflowContainer";
import Typography from "@mui/material/Typography";
import SpaceTime from "@/format/SpaceTime";
import { PersonLabel } from "@/format/PersonChip";
import Link from "next/link";
import { TLetter, TPageResults, TAsyncSearchParams } from "../types";
import { djangoFetchData, safeParseInt } from "../utils";
import { INDIVIDU_FIELDS, PLACE_FIELDS } from "../constants";
import Divider from "@mui/material/Divider";
import Empty from "./Empty";
import ImageRendition from "./ImageRendition";

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
      `sender(${INDIVIDU_FIELDS})`,
      `recipients(person(${INDIVIDU_FIELDS}))`,
      `writing_lieu(${PLACE_FIELDS})`,
      "writing_lieu_approx",
      "writing_date",
      "writing_date_approx",
      "writing_heure",
      "writing_heure_approx",
      "letter_images",
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
          meta: { slug },
          sender,
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
              <CardActionArea component={Link} href={slug} prefetch={false}>
                <Stack direction="row" flexWrap="nowrap">
                  {letter_images.length >= 1 ? (
                    <ImageRendition
                      rendition={letter_images[0].thumbnail}
                      style={{
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
                  <OverflowContainer
                    maxHeight={200}
                    overflowHeight={50}
                    sx={{ width: "100%" }}
                  >
                    <Stack spacing={1} p={2}>
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        spacing={2}
                      >
                        <Typography>
                          De{" "}
                          <strong>
                            <PersonLabel {...sender} />
                          </strong>{" "}
                          à{" "}
                          {recipients.map(({ person }) => (
                            <strong key={person.id}>
                              <PersonLabel {...person} />
                            </strong>
                          ))}
                        </Typography>
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
                      <Divider />
                      <Typography textAlign="justify">
                        {transcription_text}
                      </Typography>
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
