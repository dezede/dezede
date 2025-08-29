import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import Stack from "@mui/material/Stack";
import OverflowContainer from "./OverflowContainer";
import Typography from "@mui/material/Typography";
import SpaceTime from "./SpaceTime";
import PersonLabel from "./PersonLabel";
import Link from "next/link";
import Image from "next/image";
import { EPageType, TLetter, TPageResults, TSearchParams } from "../types";
import { djangoFetchData } from "../utils";
import { INDIVIDU_FIELDS, PLACE_FIELDS } from "../constants";

export default async function LetterList({
  parentPageId,
  searchParams,
}: {
  parentPageId: number;
  searchParams: TSearchParams;
}) {
  const { search = "" } = await searchParams;
  const lettersData = await djangoFetchData<
    TPageResults<
      Omit<TLetter, "transcription" | "description"> & {
        transcription_text: string;
      }
    >
  >("/api/pages/", {
    child_of: parentPageId,
    type: EPageType.LETTER,
    fields: `sender(${INDIVIDU_FIELDS}),recipients(person(${INDIVIDU_FIELDS})),writing_lieu(${PLACE_FIELDS}),writing_lieu_approx,writing_date,writing_date_approx,writing_heure,writing_heure_approx,letter_images,transcription_text`,
    search,
  });
  return (
    <Stack flexWrap="nowrap" spacing={2}>
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
          const {
            thumbnail: { full_url, width, height, alt },
          } = letter_images[0];
          return (
            <Card key={id}>
              <CardActionArea component={Link} href={slug} prefetch={false}>
                <Stack direction="row" flexWrap="nowrap">
                  <Image
                    src={full_url}
                    width={width}
                    height={height}
                    alt={alt}
                    unoptimized
                  />
                  <OverflowContainer
                    maxHeight={height}
                    overflowHeight={50}
                    sx={{ width: "100%" }}
                  >
                    <Stack flexWrap="nowrap" p={2}>
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
                      <Typography>{transcription_text}</Typography>
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
