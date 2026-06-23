"use client";

import { getApiClient } from "@/shared/api/client";
import { ChannelMetricCard } from "@/shared/ui/channel-card";
import { useCallback, useState } from "react";
import type { ReactNode } from "react";

import { FollowDataTable } from "./follow-data-table";
import { languageEmoji, languageLabel } from "./languages";
import type { Follow, FollowResponse } from "./types";

const dateFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

export function FollowResults({
  login,
  initialData,
  initialFollows,
  profile,
}: {
  login: string;
  initialData: FollowResponse;
  initialFollows: Follow[];
  profile: ReactNode;
}) {
  const [follows, setFollows] = useState(initialFollows);
  const [nextCursor, setNextCursor] = useState(initialData.next_cursor);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const regions = initialData.regions;

  const loadMore = useCallback(async () => {
    if (!nextCursor || isLoadingMore) return;

    setIsLoadingMore(true);
    try {
      const { data: page } = await getApiClient().GET("/channels/{login}/follows", {
        params: {
          path: { login },
          query: { limit: 100, after: nextCursor },
        },
      });
      if (!page) return;

      const nextFollows = page.items.map(mapFollow);
      setFollows((current) => uniqueFollows([...current, ...nextFollows]));
      setNextCursor(page.next_cursor);
    } finally {
      setIsLoadingMore(false);
    }
  }, [isLoadingMore, login, nextCursor]);

  return (
    <main className="mx-auto flex w-full max-w-[1920px] items-start gap-3 px-6 pb-9 pt-[124px]">
      <aside className="flex w-[400px] shrink-0 flex-col gap-3">
        {profile}
        <RegionsCard regions={regions} />
      </aside>
      <div className="min-w-0 flex-1">
        <FollowDataTable
          data={follows}
          regions={regions}
          hasMore={nextCursor !== null}
          onLoadMore={loadMore}
        />
      </div>
    </main>
  );
}

function RegionsCard({ regions }: { regions: FollowResponse["regions"] }) {
  return (
    <ChannelMetricCard
      title="Регионы фолловов"
      titleMeta={regions.length.toLocaleString("ru-RU")}
      items={regions.slice(0, 5).map((region, index) => ({
        id: region.language,
        label: `${languageEmoji(region.language)} ${languageLabel(region.language)}`,
        value: `${region.count.toLocaleString("ru-RU")} (${region.percent}%)`,
        percent: region.percent,
        lineClassName: index === 0 ? "bg-[#9247ff]" : "bg-[#707070]",
      }))}
    />
  );
}

function mapFollow(item: FollowResponse["items"][number]): Follow {
  return {
    twitchId: item.twitch_id,
    login: item.login,
    displayName: item.display_name,
    avatarUrl: item.avatar_url,
    language: item.language,
    languageLabel: languageLabel(item.language),
    languageEmoji: languageEmoji(item.language),
    followedAt: formatDate(item.followed_at),
    followedAtTimestamp: item.followed_at ? Date.parse(item.followed_at) : 0,
    createdAt: formatDate(item.twitch_created_at),
  };
}

function formatDate(value: string | null) {
  return value ? dateFormatter.format(new Date(value)) : "Нет данных";
}

function uniqueFollows(items: Follow[]) {
  return [...new Map(items.map((item) => [item.twitchId, item])).values()];
}
