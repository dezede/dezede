import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useTranslations } from "next-intl";
import { TPeriod } from "@/app/types";

/**
 * Stacked horizontal bar of works grouped by their composer's birth period,
 * mirroring the Django dossier statistics "œuvres par période" progress bar.
 */
export default function PeriodDistribution({
  periods,
  total,
}: {
  periods: TPeriod[];
  total: number;
}) {
  const t = useTranslations("dossiers");
  if (total === 0 || periods.length === 0) {
    return null;
  }
  return (
    <Stack spacing={1.5}>
      <Box
        sx={{
          display: "flex",
          width: "100%",
          height: 32,
          borderRadius: 1,
          overflow: "hidden",
        }}
      >
        {periods.map((period) => {
          const percent = (period.count / total) * 100;
          return (
            <Tooltip
              key={period.name}
              title={t("periodTooltip", {
                name: period.name,
                count: period.count,
                percent: percent.toFixed(1),
              })}
              arrow
            >
              <Box
                sx={{
                  width: `${percent}%`,
                  backgroundColor: period.color,
                  color: period.text_color,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.75rem",
                  minWidth: 0,
                }}
              >
                {percent >= 6 ? period.count : null}
              </Box>
            </Tooltip>
          );
        })}
      </Box>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1.5 }}>
        {periods.map((period) => (
          <Stack
            key={period.name}
            direction="row"
            spacing={0.5}
            sx={{ alignItems: "center" }}
          >
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: 0.5,
                backgroundColor: period.color,
                flexShrink: 0,
              }}
            />
            <Typography variant="caption" color="text.secondary">
              {period.name}
            </Typography>
          </Stack>
        ))}
      </Box>
    </Stack>
  );
}
