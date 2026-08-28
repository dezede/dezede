import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import type { Metadata as TMetadata } from "next";
import { getTranslations } from "next-intl/server";
import { TEventDetail } from "@/app/types";
import { EVENTS_BASE } from "@/app/constants";
import { fetchEventsJson } from "@/app/events";
import OurLink from "@/components/OurLink";
import DetailAdminBar from "@/components/DetailAdminBar";
import EventCard from "@/components/EventCard";
import Metadata from "@/components/Metadata";
import EtatBadge from "@/components/EtatBadge";
import RichText from "@/components/RichText";
import DetailTable from "@/components/DetailTable";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ pk: string }>;
}): Promise<TMetadata> {
  const { pk } = await params;
  const t = await getTranslations();
  return {
    title: t("pages.titleTemplate", {
      name: t("pages.evenements.detailTitle", { pk }),
    }),
  };
}

export default async function EvenementDetail({
  params,
}: {
  params: Promise<{ pk: string }>;
}) {
  const { pk } = await params;
  const t = await getTranslations("pages");
  const event = await fetchEventsJson<TEventDetail>(`/api/evenements/${pk}/`);

  return (
    <Container>
      <Stack spacing={3}>
        <Button
          component={OurLink}
          href={`${EVENTS_BASE}/`}
          startIcon={<ChevronLeftIcon />}
          sx={{ alignSelf: "flex-start" }}
        >
          {t("evenements.backToAll")}
        </Button>
        <Stack
          direction="row"
          spacing={2}
          sx={{ justifyContent: "space-between", alignItems: "flex-start" }}
        >
          <EventCard event={event} component="h1" />
          <DetailAdminBar {...event} />
        </Stack>
        <EtatBadge etat={event.etat ?? null} />
        {event.recette_generale ? (
          <Metadata
            rows={[
              {
                key: "recette",
                label: t("evenements.totalRevenue"),
                value: event.recette_generale,
              },
            ]}
          />
        ) : null}
        {event.notes_publiques ? (
          <DetailTable
            rows={[
              {
                key: "notes",
                label: t("rows.notes"),
                content: <RichText value={event.notes_publiques} />,
              },
            ]}
          />
        ) : null}
      </Stack>
    </Container>
  );
}
