"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

import { TChord } from "@/app/types";
import { getPersonLabel } from "@/format/PersonChip";

// Angle 0 points to 12 o'clock and increases clockwise (as in d3.chord).
function polar(
  cx: number,
  cy: number,
  radius: number,
  angle: number,
): [number, number] {
  return [cx + radius * Math.sin(angle), cy - radius * Math.cos(angle)];
}

function annularSector(
  cx: number,
  cy: number,
  a0: number,
  a1: number,
  rIn: number,
  rOut: number,
): string {
  const [x0, y0] = polar(cx, cy, rOut, a0);
  const [x1, y1] = polar(cx, cy, rOut, a1);
  const [x2, y2] = polar(cx, cy, rIn, a1);
  const [x3, y3] = polar(cx, cy, rIn, a0);
  const large = a1 - a0 > Math.PI ? 1 : 0;
  return (
    `M ${x0} ${y0} A ${rOut} ${rOut} 0 ${large} 1 ${x1} ${y1} ` +
    `L ${x2} ${y2} A ${rIn} ${rIn} 0 ${large} 0 ${x3} ${y3} Z`
  );
}

function ribbon(
  cx: number,
  cy: number,
  r: number,
  s0: number,
  s1: number,
  t0: number,
  t1: number,
): string {
  const [sx0, sy0] = polar(cx, cy, r, s0);
  const [sx1, sy1] = polar(cx, cy, r, s1);
  const [tx0, ty0] = polar(cx, cy, r, t0);
  const [tx1, ty1] = polar(cx, cy, r, t1);
  const sLarge = s1 - s0 > Math.PI ? 1 : 0;
  const tLarge = t1 - t0 > Math.PI ? 1 : 0;
  return (
    `M ${sx0} ${sy0} ` +
    `A ${r} ${r} 0 ${sLarge} 1 ${sx1} ${sy1} ` +
    `Q ${cx} ${cy} ${tx0} ${ty0} ` +
    `A ${r} ${r} 0 ${tLarge} 1 ${tx1} ${ty1} ` +
    `Q ${cx} ${cy} ${sx0} ${sy0} Z`
  );
}

/**
 * Chord diagram of composer co-occurrences in a dossier's events (one arc per
 * composer, ribbons weighted by shared events), replicating the Django stats
 * chord diagram. Arcs are coloured by the composer's birth period.
 */
export default function ChordDiagram({ chord }: { chord: TChord }) {
  const t = useTranslations("dossiers");
  const tCommon = useTranslations("common");
  const { nodes, matrix } = chord;
  const n = nodes.length;
  // Format each author's name through the shared frontend helper so the chord
  // diagram follows the active locale, like the rest of the site's chips.
  const labels = nodes.map((node) => getPersonLabel(node.individu, tCommon));
  const size = 620;
  const cx = size / 2;
  const cy = size / 2;
  const outerR = 250;
  const band = 14;
  const ribbonR = outerR - band - 2;
  const labelFontSize = 18;
  const labelGap = 8;

  // Click (or press Enter/Space) an author to isolate the chords touching it;
  // repeat to hide them instead; click the background to reset (mirrors the
  // Django diagram).
  const [sel, setSel] = useState<{ idx: number; hidden: boolean } | null>(null);
  const selectAuthor = (idx: number): void => {
    setSel((prev) =>
      prev && prev.idx === idx
        ? { idx, hidden: !prev.hidden }
        : { idx, hidden: false },
    );
  };
  const handleAuthorKeyDown = (
    e: React.KeyboardEvent<SVGGElement>,
    idx: number,
  ): void => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      e.stopPropagation();
      selectAuthor(idx);
    }
  };

  const rowTotals = matrix.map((row) => row.reduce((a, b) => a + b, 0));
  const grandTotal = rowTotals.reduce((a, b) => a + b, 0);
  if (grandTotal === 0) {
    return null;
  }

  const pad = Math.min(0.04, (2 * Math.PI) / (n * 4));
  const available = 2 * Math.PI - n * pad;

  // Group angular spans, and per-target sub-arc spans within each group.
  const groupStart: number[] = [];
  const groupEnd: number[] = [];
  const sub: { start: number; end: number }[][] = [];
  let cursor = 0;
  for (let i = 0; i < n; i++) {
    const span = (rowTotals[i] / grandTotal) * available;
    groupStart[i] = cursor;
    groupEnd[i] = cursor + span;
    sub[i] = [];
    let inner = cursor;
    for (let j = 0; j < n; j++) {
      const sliceAngle =
        rowTotals[i] > 0 ? (matrix[i][j] / rowTotals[i]) * span : 0;
      sub[i][j] = { start: inner, end: inner + sliceAngle };
      inner += sliceAngle;
    }
    cursor = groupEnd[i] + pad;
  }

  const ribbons: {
    d: string;
    color: string;
    title: string;
    i: number;
    j: number;
  }[] = [];
  for (let i = 0; i < n; i++) {
    for (let j = i; j < n; j++) {
      if (matrix[i][j] === 0 && matrix[j][i] === 0) {
        continue;
      }
      const value = matrix[i][j] + (i === j ? 0 : matrix[j][i]);
      ribbons.push({
        d: ribbon(
          cx,
          cy,
          ribbonR,
          sub[i][j].start,
          sub[i][j].end,
          sub[j][i].start,
          sub[j][i].end,
        ),
        color: nodes[i].color,
        title: `${labels[i]} ↔ ${labels[j]} : ${value}`,
        i,
        j,
      });
    }
  }

  // Per-ribbon opacity given the current selection.
  const ribbonOpacity = (i: number, j: number): number => {
    if (sel === null) {
      return 0.55;
    }
    const connected = i === sel.idx || j === sel.idx;
    if (sel.hidden) {
      return connected ? 0 : 0.55;
    }
    return connected ? 0.55 : 0;
  };

  // Compute a tight bounding box of the actual content (the arc ring plus each
  // visible label radiating outward) instead of reserving the widest label's
  // width on all four sides. A square viewBox padded symmetrically left empty
  // bands above/below the ring whenever the longest labels pointed left/right.
  // Folding every content point into the bounds keeps it tight without ever
  // clipping an arc, ribbon, or label.
  let minX = cx - outerR;
  let maxX = cx + outerR;
  let minY = cy - outerR;
  let maxY = cy + outerR;
  const halfFont = labelFontSize / 2;
  for (let i = 0; i < n; i++) {
    if (groupEnd[i] - groupStart[i] < 1e-4) {
      continue;
    }
    const mid = (groupStart[i] + groupEnd[i]) / 2;
    const labelWidth = labels[i].length * labelFontSize * 0.6;
    const [nx, ny] = polar(cx, cy, outerR + labelGap, mid);
    const [fx, fy] = polar(cx, cy, outerR + labelGap + labelWidth, mid);
    for (const [px, py] of [
      [nx, ny],
      [fx, fy],
    ]) {
      minX = Math.min(minX, px - halfFont);
      maxX = Math.max(maxX, px + halfFont);
      minY = Math.min(minY, py - halfFont);
      maxY = Math.max(maxY, py + halfFont);
    }
  }
  const margin = 4;
  minX -= margin;
  minY -= margin;
  maxX += margin;
  maxY += margin;
  const viewBox = `${minX} ${minY} ${maxX - minX} ${maxY - minY}`;

  return (
    <svg
      viewBox={viewBox}
      width="100%"
      style={{ maxWidth: 960, height: "auto" }}
      role="group"
      aria-label={t("chordDiagramAria")}
      onClick={() => setSel(null)}
    >
      {ribbons.map((r, index) => (
        <path
          key={index}
          d={r.d}
          fill={r.color}
          fillOpacity={ribbonOpacity(r.i, r.j)}
          style={{ transition: "fill-opacity 0.2s" }}
        >
          <title>{r.title}</title>
        </path>
      ))}
      {nodes.map((node, i) => {
        if (groupEnd[i] - groupStart[i] < 1e-4) {
          return null;
        }
        const mid = (groupStart[i] + groupEnd[i]) / 2;
        const [lx, ly] = polar(cx, cy, outerR + labelGap, mid);
        const degrees = (mid * 180) / Math.PI;
        const flip = degrees > 180;
        return (
          <g
            key={node.id}
            style={{ cursor: "pointer" }}
            role="button"
            tabIndex={0}
            aria-label={t("selectAuthorAria", { name: labels[i] })}
            aria-pressed={sel !== null && sel.idx === i && !sel.hidden}
            onClick={(e) => {
              e.stopPropagation();
              selectAuthor(i);
            }}
            onKeyDown={(e) => handleAuthorKeyDown(e, i)}
          >
            <path
              d={annularSector(
                cx,
                cy,
                groupStart[i],
                groupEnd[i],
                outerR - band,
                outerR,
              )}
              fill={node.color}
            >
              <title>{labels[i]}</title>
            </path>
            <text
              x={lx}
              y={ly}
              fontSize={labelFontSize}
              textAnchor={flip ? "end" : "start"}
              transform={`rotate(${flip ? degrees + 90 : degrees - 90} ${lx} ${ly})`}
              style={{ dominantBaseline: "middle", userSelect: "none" }}
            >
              {labels[i]}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
