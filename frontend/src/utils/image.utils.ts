/**
 * Image URL Utility Functions
 *
 * Handles conversion of relative image URLs to absolute URLs with backend base URL
 */

/**
 * Convert relative image URL to absolute URL with backend base URL
 *
 * @param relativeUrl - Relative URL from database (e.g., "/static/prompts/images/abc.jpg")
 * @returns Absolute URL (e.g., "http://localhost:12346/static/prompts/images/abc.jpg")
 *
 * @example
 * ```typescript
 * // From database: "/static/prompts/images/abc.jpg"
 * const absoluteUrl = getImageUrl("/static/prompts/images/abc.jpg");
 * // Result: "http://localhost:12346/static/prompts/images/abc.jpg"
 * ```
 */
export function getImageUrl(relativeUrl: string): string {
  // Get base URL from environment variable
  const API_URL = import.meta.env.VITE_API_URL || 'localhost:12346';
  const BASE_URL = `http://${API_URL}`;

  // Handle already absolute URLs (http:// or https://)
  if (relativeUrl.startsWith('http://') || relativeUrl.startsWith('https://')) {
    return relativeUrl;
  }

  // Ensure URL starts with "/" to avoid double slashes
  const cleanUrl = relativeUrl.startsWith('/') ? relativeUrl : `/${relativeUrl}`;

  // Combine base URL with relative path
  return `${BASE_URL}${cleanUrl}`;
}

/**
 * Convert multiple relative image URLs to absolute URLs
 *
 * @param relativeUrls - Array of relative URLs
 * @returns Array of absolute URLs
 *
 * @example
 * ```typescript
 * const urls = ["/static/img1.jpg", "/static/img2.jpg"];
 * const absoluteUrls = getImageUrls(urls);
 * // Result: ["http://localhost:12346/static/img1.jpg", "http://localhost:12346/static/img2.jpg"]
 * ```
 */
export function getImageUrls(relativeUrls: string[]): string[] {
  return relativeUrls.map(url => getImageUrl(url));
}
