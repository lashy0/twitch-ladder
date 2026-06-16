import type { ApiFollowList } from "@/shared/api/types";

type FollowList = ApiFollowList;

export type Channel = Pick<
  FollowList["channel"],
  "login" | "display_name" | "avatar_url" | "twitch_created_at"
>;

export type Follow = {
  twitchId: string;
  login: string;
  displayName: string;
  avatarUrl: string | null;
  language: string;
  languageLabel: string;
  languageEmoji: string;
  followedAt: string;
  followedAtTimestamp: number;
  createdAt: string;
};

export type FollowResponse = FollowList;
