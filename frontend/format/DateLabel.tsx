export function getDateLabel(
  dateString: string | null = null,
  fuzzyDate: string = "",
): string {
  if (fuzzyDate !== "") {
    return fuzzyDate;
  }
  if (dateString === null) {
    return "";
  }
  return new Date(dateString).toLocaleDateString("fr-FR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function DateLabel({
  dateString = null,
  fuzzyDate = "",
}: {
  dateString?: string | null;
  fuzzyDate?: string;
}): string | null {
  return getDateLabel(dateString, fuzzyDate);
}
