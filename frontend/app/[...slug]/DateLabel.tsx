export function DateLabel({
  dateString = null,
  fuzzyDate = "",
}: {
  dateString?: string | null;
  fuzzyDate?: string;
}): string | null {
  if (fuzzyDate !== "") {
    return fuzzyDate;
  }
  if (dateString === null) {
    return null;
  }
  return new Date(dateString).toLocaleDateString("fr-FR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}
