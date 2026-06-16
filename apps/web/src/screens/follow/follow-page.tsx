import { getApiClient } from "@/shared/api/client";
import { AppHeader } from "@/shared/ui/app-header/app-header";

import { FollowResults } from "./follow-results";
import { languageEmoji, languageLabel } from "./languages";
import type { Channel, Follow, FollowResponse } from "./types";

const dateFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

async function getFollows(login: string): Promise<FollowResponse | null> {
  try {
    const { data } = await getApiClient().GET(
      "/channels/{login}/follows",
      {
        cache: "no-store",
        params: {
          path: { login },
        },
      },
    );
    return data ?? null;
  } catch {
    return null;
  }
}

function formatDate(value: string | null) {
  return value ? dateFormatter.format(new Date(value)) : "Нет данных";
}

function ProfileCard({
  channel,
  login,
  followersTotal,
  followsTotal,
}: {
  channel: Channel | null;
  login: string;
  followersTotal: number | null;
  followsTotal: number;
}) {
  const displayName = channel?.display_name || channel?.login || login;
  const twitchLogin = channel?.login || login;

  return (
    <section className="relative h-[463px] overflow-hidden rounded-[15px] border border-[#252525] bg-[#0b0b0b]">
      <a
        className="absolute left-[325px] top-[23px] block size-[50px]"
        href={`https://twitch.tv/${encodeURIComponent(twitchLogin)}`}
        target="_blank"
        rel="noreferrer"
        aria-label="Открыть канал на Twitch"
      >
        <img className="size-[50px]" src="/icons/external-link.svg" alt="" />
      </a>

      <div className="absolute left-[116px] top-[23px] flex w-[166px] flex-col items-center gap-1.5">
        <div className="flex w-full flex-col items-center gap-3">
          {channel?.avatar_url ? (
            <img
              className="size-[150px] rounded-full object-cover"
              src={channel.avatar_url}
              alt=""
            />
          ) : (
            <div className="size-[150px] rounded-full bg-[#18181b]" />
          )}
          <h1 className="w-[166px] truncate text-center text-2xl font-medium leading-[29px] text-white">
            {displayName}
          </h1>
        </div>
        <p className="w-[166px] truncate text-center text-lg font-normal leading-[22px] text-[#707070]">
          @{twitchLogin}
        </p>
      </div>

      <div className="absolute left-[23px] top-[266px] grid w-[352px] grid-cols-2 gap-3 text-center">
        <div className="col-span-2 flex h-20 flex-col justify-center gap-2 rounded-[15px] bg-[#18181b]">
          <span className="text-lg leading-[22px] text-[#707070]">дата создания</span>
          <strong className="text-xl font-medium leading-[24px] text-white">
            {formatDate(channel?.twitch_created_at ?? null)}
          </strong>
        </div>
        <Stat label="фолловеров" value={followersTotal?.toLocaleString("ru-RU") ?? "Нет данных"} />
        <Stat label="фолловов" value={followsTotal.toLocaleString("ru-RU")} />
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex h-20 flex-col justify-center gap-2 rounded-[15px] bg-[#18181b]">
      <span className="text-lg leading-[22px] text-[#707070]">{label}</span>
      <strong className="truncate px-2 text-xl font-medium leading-[24px] text-white">
        {value}
      </strong>
    </div>
  );
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
            <ProfileCard
              channel={channel}
              login={login}
              followersTotal={data.followers_total}
              followsTotal={0}
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
            <ProfileCard
              channel={channel}
              login={login}
              followersTotal={data.followers_total}
              followsTotal={data.total}
            />
          }
        />
      )}
    </div>
  );
}
