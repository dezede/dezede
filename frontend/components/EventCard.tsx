import { useTranslations } from "next-intl";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";
import EventBusyOutlinedIcon from "@mui/icons-material/EventBusyOutlined";
import { TEvent } from "@/app/types";
import { EVENTS_BASE } from "@/app/constants";
import OurLink from "@/components/OurLink";
import SpaceTime from "@/format/SpaceTime";
import Casting from "@/format/Casting";
import Programme from "@/format/Programme";
import Characteristics from "@/format/Characteristics";
import SourcesPanel from "@/components/SourcesPanel";
import SectionLabel from "@/components/SectionLabel";

export default function EventCard({
  event,
  component = "h2",
}: {
  event: TEvent;
  component?: React.ElementType;
}) {
  const t = useTranslations("event");
  // The heading puts every date/time on one line and every place on the line
  // below, so the range dash hugs the start date instead of being pushed past a
  // wide place chip. Track the date/time and place of each end independently.
  const hasEndDateTime =
    event.fin_date !== null ||
    event.fin_date_approx !== "" ||
    event.fin_heure !== null ||
    event.fin_heure_approx !== "";
  const hasStartPlace =
    event.debut_lieu !== null || event.debut_lieu_approx !== "";
  const hasEndPlace = event.fin_lieu !== null || event.fin_lieu_approx !== "";
  const hasDistribution = event.distribution.length > 0;
  const hasProgramme = event.programme.length > 0;
  const hasSources = (event.sources?.length ?? 0) > 0;
  const hasSubtitle =
    Boolean(event.circonstance) || event.caracteristiques.length > 0;
  // The header element is an <h1> on the detail page and an <h2> in lists. Keep
  // that semantic level but override the visual size so the date/time text (which
  // inherits it via SpaceTime's fontSize="inherit") reads as a balanced title
  // next to the small place/status chips instead of dwarfing them.
  const isMainHeading = component === "h1";
  const eventHref = `${EVENTS_BASE}/id/${event.id}/`;
  return (
    <Paper
      sx={{ p: 2 }}
      itemScope
      itemType="https://schema.org/Event"
      variant="outlined"
    >
      <Stack spacing={2}>
        <Stack spacing={0.5}>
          <Box
            component={component}
            sx={{
              m: 0,
              fontSize: isMainHeading ? "1.5rem" : "1.25rem",
              fontWeight: 600,
              lineHeight: 1.3,
            }}
          >
            <Stack spacing={0.5}>
              <Stack
                direction="row"
                flexWrap="wrap"
                alignItems="center"
                useFlexGap
                spacing={1}
              >
                <Link
                  component={OurLink}
                  href={eventHref}
                  color="inherit"
                  underline="hover"
                  sx={{ display: "inline-flex" }}
                >
                  <Stack
                    direction="row"
                    flexWrap="wrap"
                    alignItems="center"
                    useFlexGap
                    spacing={1}
                  >
                    <SpaceTime
                      date={event.debut_date}
                      fuzzyDate={event.debut_date_approx}
                      time={event.debut_heure}
                      fuzzyTime={event.debut_heure_approx}
                    />
                    {hasEndDateTime ? (
                      <>
                        <Typography
                          component="span"
                          color="text.secondary"
                          fontSize="inherit"
                        >
                          —
                        </Typography>
                        <SpaceTime
                          date={event.fin_date}
                          fuzzyDate={event.fin_date_approx}
                          time={event.fin_heure}
                          fuzzyTime={event.fin_heure_approx}
                        />
                      </>
                    ) : null}
                  </Stack>
                </Link>
                {event.relache ? (
                  <Chip
                    icon={<EventBusyOutlinedIcon />}
                    label={t("relache")}
                    size="small"
                    color="secondary"
                  />
                ) : null}
                {event.programme_incomplet ? (
                  <Chip
                    label={t("programmeIncomplete")}
                    size="small"
                    variant="outlined"
                  />
                ) : null}
              </Stack>
              {hasStartPlace || hasEndPlace ? (
                <Stack
                  direction="row"
                  flexWrap="wrap"
                  alignItems="center"
                  useFlexGap
                  spacing={1}
                >
                  {hasStartPlace ? (
                    <SpaceTime
                      place={event.debut_lieu}
                      fuzzyPlace={event.debut_lieu_approx}
                      chip
                    />
                  ) : null}
                  {hasEndPlace ? (
                    <SpaceTime
                      place={event.fin_lieu}
                      fuzzyPlace={event.fin_lieu_approx}
                      chip
                    />
                  ) : null}
                </Stack>
              ) : null}
            </Stack>
          </Box>
          {hasSubtitle ? (
            <Stack
              direction="row"
              flexWrap="wrap"
              alignItems="center"
              useFlexGap
              spacing={1}
            >
              {event.circonstance ? (
                <Typography
                  itemProp="description"
                  variant="body2"
                  color="text.secondary"
                >
                  {event.circonstance}
                </Typography>
              ) : null}
              <Characteristics
                caracteristiques={event.caracteristiques}
                brackets={false}
                caps
              />
            </Stack>
          ) : null}
        </Stack>
        {hasDistribution ? (
          <Stack spacing={0.75}>
            <SectionLabel>{t("distribution")}</SectionLabel>
            <Stack
              direction="row"
              flexWrap="wrap"
              alignItems="center"
              useFlexGap
              spacing={0.5}
            >
              <Casting elements={event.distribution} />
            </Stack>
          </Stack>
        ) : null}
        {hasProgramme ? (
          <Stack spacing={0.75}>
            <SectionLabel>{t("programme")}</SectionLabel>
            <Programme elements={event.programme} />
          </Stack>
        ) : null}
        {hasSources ? <SourcesPanel groups={event.sources!} modal /> : null}
      </Stack>
    </Paper>
  );
}
