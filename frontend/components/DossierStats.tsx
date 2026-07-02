"use client";

import { useEffect, useState } from "react";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";
import { useTranslations } from "next-intl";
import { TDossierStats } from "@/app/types";
import { apiGet } from "@/app/api";
import PeriodDistribution from "./PeriodDistribution";
import ChordDiagram from "./ChordDiagram";
import Empty from "./Empty";

/**
 * Fetches and renders a dossier's statistics (works-by-period bar and the
 * composer chord diagram), mirroring the Django "Visualisations" tab.
 */
export default function DossierStats({ statsUrl }: { statsUrl: string }) {
  const t = useTranslations("dossiers");
  const [stats, setStats] = useState<TDossierStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const data = await apiGet<TDossierStats>(statsUrl);
        if (!cancelled) {
          setStats(data);
        }
      } catch {
        if (!cancelled) {
          setError(true);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [statsUrl]);

  if (loading) {
    return <Skeleton variant="rectangular" height={320} />;
  }
  if (error || stats === null) {
    return <Empty>{t("statsUnavailable")}</Empty>;
  }

  const hasPeriods = stats.oeuvres_par_periode.length > 0;
  const hasChord = stats.chord !== null;

  if (!hasPeriods && !hasChord) {
    return <Empty>{t("noStats")}</Empty>;
  }

  return (
    <Stack spacing={4}>
      {hasPeriods ? (
        <Stack spacing={1.5} component="section">
          <Typography variant="h2" sx={{ fontSize: "1.25rem" }}>
            {t("worksByPeriod", { count: stats.n_oeuvres })}
          </Typography>
          <PeriodDistribution
            periods={stats.oeuvres_par_periode}
            total={stats.n_oeuvres}
          />
        </Stack>
      ) : null}
      {hasChord ? (
        <Stack spacing={1.5} component="section" alignItems="center">
          <Typography variant="h2" sx={{ fontSize: "1.25rem", alignSelf: "flex-start" }}>
            {t("composersPlayedTogether")}
          </Typography>
          <ChordDiagram chord={stats.chord!} />
        </Stack>
      ) : null}
    </Stack>
  );
}
