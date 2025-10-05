import Stack from "@mui/material/Stack";
import { TFindPageData, TLetter } from "../app/types";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { djangoFetchData } from "@/app/utils";
import {
  ENSEMBLE_FIELDS,
  EVENT_FIELDS,
  INDIVIDU_FIELDS,
  PART_FIELDS,
  PLACE_FIELDS,
  WORK_FIELDS,
} from "@/app/constants";
import PersonChip from "@/format/PersonChip";
import RichText from "@/components/RichText";
import Paper from "@mui/material/Paper";
import LetterImagesReader from "@/components/LetterImagesReader";
import SpaceTime from "@/format/SpaceTime";
import Divider from "@mui/material/Divider";
import Empty from "@/components/Empty";
import Metadata, { getFilteredRows } from "@/components/Metadata";
import PlaceChip from "@/format/PlaceChip";
import Box from "@mui/material/Box";
import OurLink from "@/components/OurLink";

export default async function Letter({
  findPageData,
}: {
  findPageData: TFindPageData;
}) {
  const {
    senders,
    recipients,
    writing_lieu,
    writing_lieu_approx,
    writing_date,
    writing_date_approx,
    writing_heure,
    writing_heure_approx,
    edition,
    storage_place,
    storage_call_number,
    source_url,
    letter_images,
    transcription,
    description,
  } = await djangoFetchData<TLetter>(
    findPageData.apiUrl,
    {},
    [
      `senders(person(${INDIVIDU_FIELDS}))`,
      `recipients(person(${INDIVIDU_FIELDS}))`,
      `writing_lieu(${PLACE_FIELDS})`,
      `storage_place(${PLACE_FIELDS})`,
      "letter_images(-thumbnail)",
      "-transcription_text",
    ],
    [
      `references__individu(${INDIVIDU_FIELDS})`,
      `references__lieu(${PLACE_FIELDS})`,
      `references__partie(${PART_FIELDS})`,
      `references__ensemble(${ENSEMBLE_FIELDS})`,
      `references__evenement(${EVENT_FIELDS})`,
      `references__oeuvre(${WORK_FIELDS})`,
    ],
  );
  const metadataRows = [
    {
      key: "edition",
      label: "Édition",
      value: edition,
    },
    {
      key: "storage",
      label: "Lieu de conservation",
      value:
        storage_place === null ? null : (
          <Stack
            direction="row"
            alignItems="baseline"
            flexWrap="wrap"
            spacing={1}
            useFlexGap
            divider={
              <Divider orientation="vertical" flexItem variant="middle" />
            }
          >
            <Box maxWidth="100%">
              <PlaceChip {...storage_place} />
            </Box>
            {storage_call_number ? <span>{storage_call_number}</span> : null}
          </Stack>
        ),
    },
    {
      key: "source_url",
      label: "URL d’origine",
      value:
        source_url === "" ? null : (
          <OurLink href={source_url}>{source_url}</OurLink>
        ),
    },
  ];
  return (
    <Grid container direction="column" spacing={4} wrap="nowrap">
      <Grid container spacing={4}>
        <Grid
          size={{ xs: 12, md: 6, lg: 5 }}
          display={
            letter_images.length === 0 ? { xs: "none", md: "block" } : undefined
          }
        >
          <Paper
            sx={{
              position: "sticky",
              top: 20,
              borderTopLeftRadius: 0,
              borderBottomLeftRadius: 0,
              overflow: "hidden",
            }}
          >
            <LetterImagesReader letterImages={letter_images} />
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 6, lg: 7 }}>
          <Paper
            sx={{
              py: 2,
              borderTopRightRadius: 0,
              borderBottomRightRadius: 0,
            }}
          >
            <Container>
              <Stack divider={<Divider />} spacing={1}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  spacing={2}
                  useFlexGap
                  flexWrap="wrap"
                >
                  <Stack
                    direction="row"
                    spacing={1}
                    flexWrap="wrap"
                    useFlexGap
                    alignItems="center"
                    maxWidth="100%"
                  >
                    <Typography color="textDisabled">De</Typography>
                    {senders.map(({ person }) => (
                      <PersonChip key={person.id} {...person} />
                    ))}
                    <Typography color="textDisabled">à</Typography>
                    {recipients.map(({ person }) => (
                      <PersonChip key={person.id} {...person} />
                    ))}
                  </Stack>
                  <SpaceTime
                    place={writing_lieu}
                    fuzzyPlace={writing_lieu_approx}
                    date={writing_date}
                    fuzzyDate={writing_date_approx}
                    time={writing_heure}
                    fuzzyTime={writing_heure_approx}
                    chip
                  />
                </Stack>
                {transcription.trim() ? (
                  <RichText value={transcription} />
                ) : (
                  <Empty>Transcription manquante</Empty>
                )}
                {getFilteredRows(metadataRows).length === 0 ? null : (
                  <Metadata rows={metadataRows} />
                )}
              </Stack>
            </Container>
          </Paper>
        </Grid>
      </Grid>
      {description ? (
        <Grid>
          <Container>
            <Paper sx={{ p: 2 }}>
              <Typography variant="overline">Description</Typography>
              <RichText value={description} />
            </Paper>
          </Container>
        </Grid>
      ) : null}
    </Grid>
  );
}
