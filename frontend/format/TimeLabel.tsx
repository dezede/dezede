export function getTimeLabel(
  timeString: string | null = null,
  fuzzyTime: string = "",
): string {
  if (fuzzyTime !== "") {
    return fuzzyTime;
  }
  if (timeString === null) {
    return "";
  }
  return new Date(`0001-01-01T${timeString}`).toLocaleTimeString("fr-FR", {
    hour: "numeric",
    minute: "numeric",
  });
}

export function TimeLabel({
  timeString = null,
  fuzzyTime = "",
}: {
  timeString?: string | null;
  fuzzyTime?: string;
}): string | null {
  return getTimeLabel(timeString, fuzzyTime);
}
