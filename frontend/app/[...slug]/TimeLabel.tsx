export function TimeLabel({
  timeString = null,
  fuzzyTime = "",
}: {
  timeString?: string | null;
  fuzzyTime?: string;
}): string | null {
  if (fuzzyTime !== "") {
    return fuzzyTime;
  }
  if (timeString === null) {
    return null;
  }
  return new Date(`0001-01-01T${timeString}`).toLocaleTimeString("fr-FR", {
    hour: "numeric",
    minute: "numeric",
  });
}
