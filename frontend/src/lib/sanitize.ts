/** Allow only HTTPS image URLs with a valid host. */
export function sanitizeImageUrl(url: string | undefined | null): string {
  if (!url) return "";
  try {
    const parsed = new URL(url.trim());
    if (parsed.protocol !== "https:" || !parsed.hostname) return "";
    return url.trim();
  } catch {
    return "";
  }
}
