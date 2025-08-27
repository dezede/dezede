export function getRelativeUrl(absoluteUrl: string): string {
  return new URL(absoluteUrl).pathname;
}
