import type { RoleCategory } from "./types";

const categoryLabels: Record<RoleCategory, string> = {
  mods: "Модеры",
  vips: "Виперы",
  founders: "Фаундеры",
  artists: "Художники",
};

export const roleCategories: RoleCategory[] = ["mods", "vips", "founders", "artists"];

export const roleAccent: Record<RoleCategory, { border: string; surface: string; line: string }> = {
  mods: {
    border: "border-[#6affc3]",
    surface: "bg-[#071d14]",
    line: "bg-[#6affc3]",
  },
  vips: {
    border: "border-[#e005b9]",
    surface: "bg-[#1f031a]",
    line: "bg-[#e005b9]",
  },
  founders: {
    border: "border-[#9346fe]",
    surface: "bg-[#180b29]",
    line: "bg-gradient-to-r from-[#f91ed2] to-[#9346ff]",
  },
  artists: {
    border: "border-[#1e69ff]",
    surface: "bg-[#071531]",
    line: "bg-[#1e69ff]",
  },
};

export function getRoleLabel(category: RoleCategory) {
  return categoryLabels[category];
}
