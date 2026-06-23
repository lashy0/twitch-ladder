import type { ApiRoleCategory, ApiRoleList } from "@/shared/api/types";

export type RoleCategory = ApiRoleCategory;
export type RoleResponse = ApiRoleList;

export type RoleEntry = {
  id: string;
  category: RoleCategory;
  login: string;
  displayName: string;
  avatarUrl: string | null;
  grantedAt: string;
  grantedAtTimestamp: number;
  createdAt: string;
};

export type RoleStat = {
  category: RoleCategory;
  count: number;
  percent: number;
};
