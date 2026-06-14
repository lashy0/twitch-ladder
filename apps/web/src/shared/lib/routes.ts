export type CheckCategory = "follow" | "roles" | "vod";

export function normalizeTwitchLogin(value: string) {
  return value.trim().toLowerCase();
}

export function getCategoryHref(category: CheckCategory, login: string) {
  const encodedLogin = encodeURIComponent(login);

  if (category === "follow") {
    return `/follow/${encodedLogin}`;
  }

  if (category === "roles") {
    return `/roles/${encodedLogin}`;
  }

  return `/vods/${encodedLogin}`;
}

export function getLadderHref(login: string) {
  return `/ladder/${encodeURIComponent(login)}`;
}
