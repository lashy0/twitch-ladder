const PUBLIC_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const SERVER_API_BASE_URL =
  process.env.API_INTERNAL_BASE_URL ?? PUBLIC_API_BASE_URL;

export function getApiBaseUrl() {
  return typeof window === "undefined" ? SERVER_API_BASE_URL : PUBLIC_API_BASE_URL;
}

export function getApiUrl(path: string) {
  return `${getApiBaseUrl()}${path}`;
}
