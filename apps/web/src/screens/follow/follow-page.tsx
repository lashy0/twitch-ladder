import { getApiClient } from "@/shared/api/client";
import { ChannelProfileCard } from "@/shared/ui/channel-card";
import { AppHeader } from "@/shared/ui/app-header/app-header";

import { FollowResults } from "./follow-results";
import { languageEmoji, languageLabel } from "./languages";
import type { Follow, FollowResponse } from "./types";

const dateFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

async function getFollows(login: string): Promise<FollowResponse | null> {
  try {
    const { data } = await getApiClient().GET("/channels/{login}/follows", {
      cache: "no-store",
      params: {
        path: { login },
      },
    });
    return data ?? null;
  } catch {
    return null;
  }
}

function formatDate(value: string | null) {
  return value ? dateFormatter.format(new Date(value)) : "Нет данных";
}

function EmptyFollows() {
  return (
    <section className="flex min-h-[870px] flex-col items-center justify-center rounded-[15px] border border-[#252525] bg-[#0b0b0b] px-6 text-center">
      <h2 className="text-2xl font-medium text-white">Нет данных о фолловах</h2>
      <p className="mt-3 max-w-[510px] text-lg leading-relaxed text-[#707070]">
        Twitch не предоставил информацию о подписках этого пользователя или данные ещё не были
        собраны.
      </p>
    </section>
  );
}

function FollowError() {
  return (
    <section className="flex min-h-[870px] flex-col items-center justify-center rounded-[15px] border border-[#252525] bg-[#0b0b0b] px-6 text-center">
      <h2 className="text-2xl font-medium text-white">Не удалось получить данные</h2>
      <p className="mt-3 max-w-[510px] text-lg leading-relaxed text-[#707070]">
        Twitch временно не отвечает или запретил доступ к списку подписок.
      </p>
    </section>
  );
}

export async function FollowPage({ login }: { login: string }) {
  const data = await getFollows(login);
  const channel = data?.channel ?? null;
  const follows: Follow[] =
    data?.items.map((item) => ({
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
    })) ?? [];

  return (
    <div className="min-h-dvh bg-black text-white">
      <AppHeader />
      {!data ? (
        <main className="mx-auto w-full max-w-[1920px] px-6 pb-9 pt-[124px]">
          <FollowError />
        </main>
      ) : data.total === 0 ? (
        <main className="mx-auto flex w-full max-w-[1920px] items-start gap-3 px-6 pb-9 pt-[124px]">
          <aside className="w-[400px] shrink-0">
            <ChannelProfileCard
              channel={channel}
              login={login}
              stats={[
                {
                  label: "дата создания",
                  value: formatDate(channel?.twitch_created_at ?? null),
                },
                {
                  label: "фолловеров",
                  value: data.followers_total?.toLocaleString("ru-RU") ?? "Нет данных",
                },
                { label: "фолловов", value: "0" },
              ]}
            />
          </aside>
          <div className="min-w-0 flex-1">
            <EmptyFollows />
          </div>
        </main>
      ) : (
        <FollowResults
          login={login}
          initialData={data}
          initialFollows={follows}
          profile={
            <ChannelProfileCard
              channel={channel}
              login={login}
              stats={[
                {
                  label: "дата создания",
                  value: formatDate(channel?.twitch_created_at ?? null),
                },
                {
                  label: "фолловеров",
                  value: data.followers_total?.toLocaleString("ru-RU") ?? "Нет данных",
                },
                { label: "фолловов", value: data.total.toLocaleString("ru-RU") },
              ]}
            />
          }
        />
      )}
    </div>
  );
}
