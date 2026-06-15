import type { CheckCategory } from "@/shared/lib/routes";

export type AuthUser = {
  twitch_id: string;
  login: string;
  display_name: string;
  avatar_url: string | null;
};

export type AuthSession = {
  authenticated: boolean;
  user: AuthUser | null;
};

export type MenuCategory = CheckCategory | "ladder";

export const menuItems: Array<{ label: string; category: MenuCategory }> = [
  { label: "Подписки", category: "follow" },
  { label: "Роли", category: "roles" },
  { label: "VOD", category: "vod" },
  { label: "Ladder", category: "ladder" },
];

// Radix offsets from the 40px trigger, which ends 6px above the 50px pill.
export const menuContentSideOffset = 18;

export function getActiveMenuCategory(pathname: string): MenuCategory | null {
  if (pathname.startsWith("/follow/")) return "follow";
  if (pathname.startsWith("/roles/")) return "roles";
  if (pathname.startsWith("/vods/")) return "vod";
  if (pathname.startsWith("/ladder/")) return "ladder";
  return null;
}
