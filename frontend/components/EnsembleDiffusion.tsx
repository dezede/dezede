import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { useTranslations } from "next-intl";
import { TTerritoireDiffusion } from "@/app/types";

// Same palette and geometry as the Django `include/ensemble_diffusion.html`.
const COLORS = ["#5bc0de", "#5cb85c", "#f0ad4e", "#ec8055", "#d9534f"];
const SIZE = 300;
const REAL_SIZE = SIZE + 2;
const CENTER = REAL_SIZE / 2;

/**
 * The geographic "diffusion" of an ensemble's events: nested, colour-coded
 * circles (a bullseye) sized by the share of events held in each territory.
 * Port of the Django `ensemble_diffusion.html` SVG. Only shown when the events
 * span more than one territory, as in the original.
 */
export default function EnsembleDiffusion({
  territoires,
}: {
  territoires: TTerritoireDiffusion[];
}) {
  const t = useTranslations("events");
  if (territoires.length <= 1) {
    return null;
  }
  const total = territoires[0].count;
  if (!total) {
    return null;
  }
  // Largest first so smaller circles paint on top, leaving concentric rings.
  const rings = territoires
    .filter((territoire) => territoire.exclusive_count > 0)
    .map((territoire, index) => {
      const radius = (territoire.count / total) * (SIZE / 2);
      const ratio = ((territoire.exclusive_count / total) * 100).toFixed(1);
      return {
        ...territoire,
        radius,
        color: COLORS[index % COLORS.length],
        ratio,
        last: false,
      };
    });
  if (rings.length === 0) {
    return null;
  }
  rings[rings.length - 1].last = true;

  return (
    <Box component="section">
      <Typography variant="h2" sx={{ fontSize: "1.5rem", mb: 1 }}>
        {t("diffusion")}
      </Typography>
      <Box
        component="svg"
        width={REAL_SIZE}
        height={REAL_SIZE}
        viewBox={`0 0 ${REAL_SIZE} ${REAL_SIZE}`}
        sx={{ maxWidth: "100%", height: "auto" }}
        role="img"
        aria-label={t("diffusionAriaLabel")}
      >
        {rings.map((ring) => (
          <g key={ring.nom}>
            <title>
              {t("diffusionRing", {
                name: ring.nom,
                ratio: ring.ratio,
                count: ring.exclusive_count,
              })}
            </title>
            <circle cx={CENTER} cy={CENTER} r={ring.radius} fill={ring.color} />
            <text
              x={CENTER}
              y={ring.last ? CENTER : CENTER - ring.radius + 14}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize={12}
              fill="#1a1a1a"
            >
              {ring.nom}
            </text>
          </g>
        ))}
      </Box>
    </Box>
  );
}
