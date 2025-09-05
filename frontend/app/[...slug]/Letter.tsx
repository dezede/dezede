import Stack from "@mui/material/Stack";
import { TFindPageData, TLetter } from "../types";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { djangoFetchData } from "../utils";
import {
  ENSEMBLE_FIELDS,
  EVENT_FIELDS,
  INDIVIDU_FIELDS,
  PART_FIELDS,
  PLACE_FIELDS,
  WORK_FIELDS,
} from "../constants";
import PersonChip from "@/format/PersonChip";
import RichText from "./RichText";
import Paper from "@mui/material/Paper";
import LetterImagesReader from "./LetterImagesReader";
import SpaceTime from "@/format/SpaceTime";
import Divider from "@mui/material/Divider";
import Empty from "./Empty";

export default async function Letter({
  findPageData,
}: {
  findPageData: TFindPageData;
}) {
  const pageData = await djangoFetchData<TLetter>(
    findPageData.apiUrl,
    {},
    [
      `sender(${INDIVIDU_FIELDS})`,
      `recipients(person(${INDIVIDU_FIELDS}))`,
      `writing_lieu(${PLACE_FIELDS})`,
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
  const {
    sender,
    recipients,
    writing_lieu,
    writing_lieu_approx,
    writing_date,
    writing_date_approx,
    writing_heure,
    writing_heure_approx,
    letter_images,
    transcription,
    description,
  } = pageData;
  return (
    <Grid container direction="column" spacing={4} wrap="nowrap">
      <Grid container spacing={4}>
        <Grid size={{ xs: 12, md: 6, lg: 5 }}>
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
              <Stack spacing={1}>
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
                  >
                    <Typography color="textDisabled">De</Typography>
                    <PersonChip {...sender} />
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
                <Divider />
                {transcription ? (
                  <RichText value={transcription} />
                ) : (
                  <Empty>Transcription manquante</Empty>
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
