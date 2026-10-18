function isLocalApiUrl(value: string) {
  return value.includes("localhost") || value.includes("127.0.0.1");
}

function resolveBrowserApiUrl(configuredUrl: string) {
  if (
    typeof window !== "undefined" &&
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1" &&
    isLocalApiUrl(configuredUrl)
  ) {
    return `${window.location.origin}/api/v1`;
  }

  return configuredUrl;
}

export const API_URL = resolveBrowserApiUrl(
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1"
);
