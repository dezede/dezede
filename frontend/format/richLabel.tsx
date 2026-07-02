import React from "react";
import { useTranslations } from "next-intl";
import Tooltip from "@mui/material/Tooltip";
import Link from "@mui/material/Link";
import OurLink from "@/components/OurLink";

// Strip HTML tags from an editor-entered string, mirroring Django's `strip_tags`
// (used by `Oeuvre.__str__`) when we need the plain-text form of a label that
// may carry inline markup.
function stripTags(html: string): string {
  return html.replace(/<[^>]*>/g, "");
}

/**
 * A node in a "rich label" — a small structured representation of a catalogue
 * label (œuvre title, section label, …). We render it two ways: to JSX for
 * display (with `<cite>`/`<em>`/tooltips/links/raw HTML), and to plain text
 * ({@link labelToText}) for the consumers that need a string (the document
 * `<title>`, Autocomplete `getOptionLabel`, {@link labelForEntity}…).
 *
 * Mirrors Django's nested HTML helpers — `cite()`, `em()`, `hlp()` (→ a
 * `title="…"` span, rendered here as a MUI tooltip), `href()` — and the
 * `strip_tags` fallback `Oeuvre.__str__` uses for the plain string.
 *
 * `text` is React-escaped; `html` is raw inline HTML an editor may have entered
 * in a CharField (Django passes these through `mark_safe`). Exactly one of
 * `text`, `html`, `children` or `tonalite` carries the content; the
 * boolean/string flags wrap it. `tooltipKey` is a key in the `work` translation
 * namespace (the characteristic type labels), resolved at render time.
 *
 * `tonalite` is a raw tonalité code (gamme + note + alteration, e.g. "Aa+") —
 * a self-contained leaf that {@link tonaliteNodes} expands, at render time, into
 * the localised phrase ("en *la* dièse mineur" / "in *A*-sharp minor"), since
 * the catalogue API sends the code untranslated.
 */
export type TLabelNode = {
  text?: string;
  html?: string;
  em?: boolean;
  cite?: boolean;
  tooltipKey?: string;
  href?: string;
  children?: TLabelNode[];
  tonalite?: string;
};

// A translator scoped to the `work` translation namespace (the shape returned by
// `useTranslations("work")` / `getTranslations("work")`).
type WorkTranslator = (key: string) => string;

// The tonalité code's alteration char (3rd) → message key; "0" (natural) is
// absent and contributes nothing.
const TONALITE_ALTERATIONS: Record<string, string> = { "-": "flat", "+": "sharp" };
// The tonalité code's gamme char (1st) → message key; "0" (undetermined) is
// absent and contributes nothing.
const TONALITE_GAMMES: Record<string, string> = { C: "major", A: "minor" };

/**
 * Expand a tonalité code into localised label nodes, with the note name
 * italicised, mirroring Django's `em(note)`. The note + alteration + gamme come
 * from the `work.tonalite` translation namespace; the (locale-specific)
 * note↔alteration glue is `alterationSeparator` (a space in French, a hyphen in
 * English: "la dièse" vs "A-sharp").
 */
export function tonaliteNodes(
  code: string,
  t: WorkTranslator,
): TLabelNode[] {
  const [gamme, note, alteration] = code;
  const nodes: TLabelNode[] = [
    { text: `${t("tonalite.connective")} ` },
    { text: t(`tonalite.notes.${note}`), em: true },
  ];
  const alterationKey = TONALITE_ALTERATIONS[alteration];
  const gammeKey = TONALITE_GAMMES[gamme];
  let rest = "";
  if (alterationKey) {
    rest += `${t("tonalite.alterationSeparator")}${t(`tonalite.alterations.${alterationKey}`)}`;
  }
  if (gammeKey) {
    rest += ` ${t(`tonalite.gammes.${gammeKey}`)}`;
  }
  if (rest) {
    nodes.push({ text: rest });
  }
  return nodes;
}

// One end of an ambitus, as sent by the API: a chromatic note index (0–11) and
// a scientific-notation octave number.
type Pitch = { note: number; octave: number };

/**
 * Format an ambitus (lowest–highest pitch) as localised label nodes, each note
 * name italicised and followed by its octave number, joined by an en dash —
 * mirroring Django's `Oeuvre.ambitus_html`. The note names come from the
 * `work.ambitus.notes` translation namespace (12 chromatic degrees, with
 * enharmonic spellings, e.g. "do dièse / ré bémol" / "C♯ / D♭").
 */
export function ambitusNodes(
  ambitus: { lower: Pitch; upper: Pitch },
  t: WorkTranslator,
): TLabelNode[] {
  const pitch = (p: Pitch): TLabelNode => ({
    text: `${t(`ambitus.notes.${p.note}`)} ${p.octave}`,
    em: true,
  });
  return [pitch(ambitus.lower), { text: " – " }, pitch(ambitus.upper)];
}

function nodeToText(node: TLabelNode, t?: WorkTranslator): string {
  if (node.tonalite !== undefined) {
    // Without a translator (e.g. the emptiness check in `getWorkDescription`),
    // fall back to the raw code so the characteristic still reads as non-empty;
    // every display path passes `t` and renders the localised phrase.
    return t ? labelToText(tonaliteNodes(node.tonalite, t), t) : node.tonalite;
  }
  if (node.children !== undefined) {
    return labelToText(node.children, t);
  }
  if (node.html !== undefined) {
    return stripTags(node.html);
  }
  return node.text ?? "";
}

export function labelToText(nodes: TLabelNode[], t?: WorkTranslator): string {
  return nodes.map((node) => nodeToText(node, t)).join("");
}

function renderNode(
  node: TLabelNode,
  key: React.Key,
  t: (key: string) => string,
): React.ReactNode {
  let content: React.ReactNode;
  if (node.children !== undefined) {
    content = <LabelNodes nodes={node.children} />;
  } else if (node.html !== undefined) {
    content = <span dangerouslySetInnerHTML={{ __html: node.html }} />;
  } else {
    content = node.text ?? "";
  }
  if (node.em) {
    content = <em>{content}</em>;
  }
  if (node.cite) {
    // Django styles `cite` as `font-style: normal`, so keep it non-italic.
    content = <cite style={{ fontStyle: "normal" }}>{content}</cite>;
  }
  if (node.tooltipKey !== undefined) {
    content = (
      <Tooltip title={t(node.tooltipKey)} arrow disableInteractive>
        <span>{content}</span>
      </Tooltip>
    );
  }
  if (node.href !== undefined) {
    content = (
      <Link
        component={OurLink}
        href={node.href}
        color="inherit"
        underline="hover"
      >
        {content}
      </Link>
    );
  }
  return <React.Fragment key={key}>{content}</React.Fragment>;
}

export function LabelNodes({ nodes }: { nodes: TLabelNode[] }) {
  // Characteristic tooltip labels — and the tonalité vocabulary — live in the
  // `work` translation namespace.
  const t = useTranslations("work");
  // Expand tonalité leaves into their localised nodes before rendering; nested
  // ones (inside `children`) are handled by the recursive `LabelNodes` call in
  // `renderNode`.
  const expanded = nodes.flatMap((node) =>
    node.tonalite !== undefined ? tonaliteNodes(node.tonalite, t) : [node],
  );
  return <>{expanded.map((node, index) => renderNode(node, index, t))}</>;
}

/**
 * Concatenate node lists, inserting `separator` (a plain-text node) between
 * non-empty ones — so the spacing is identical whether rendered to JSX or text.
 */
export function joinNodes(
  lists: TLabelNode[][],
  separator: string,
): TLabelNode[] {
  const result: TLabelNode[] = [];
  for (const list of lists.filter((list) => list.length > 0)) {
    if (result.length > 0 && separator) {
      result.push({ text: separator });
    }
    result.push(...list);
  }
  return result;
}

/**
 * Node equivalent of {@link joinWithLast}: "a, b et c" (with a non-breaking
 * space after "et"), used for enumerations of section labels.
 */
export function joinNodesWithLast(lists: TLabelNode[][]): TLabelNode[] {
  const nonEmpty = lists.filter((list) => list.length > 0);
  const result: TLabelNode[] = [];
  nonEmpty.forEach((list, index) => {
    if (index > 0) {
      result.push({ text: index === nonEmpty.length - 1 ? " et " : ", " });
    }
    result.push(...list);
  });
  return result;
}
