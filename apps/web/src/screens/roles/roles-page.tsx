import { getApiClient } from "@/shared/api/client";
import { ChannelProfileCard } from "@/shared/ui/channel-card";
import { AppHeader } from "@/shared/ui/app-header/app-header";

import { RolesResults } from "./roles-results";
import type { RoleResponse } from "./types";

const dateFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

async function getRoles(login: string): Promise<RoleResponse | null> {
  try {
    const { data } = await getApiClient().GET("/channels/{login}/roles", {
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

export async function RolesPage({ login }: { login: string }) {
  const data = await getRoles(login);

  if (!data) {
    return (
      <div className="min-h-dvh bg-black text-white">
        <AppHeader />
        <main className="mx-auto w-full max-w-[1920px] px-6 pb-9 pt-[124px]">
          <section className="flex min-h-[870px] flex-col items-center justify-center rounded-[15px] border border-[#252525] bg-[#0b0b0b] px-6 text-center">
            <h1 className="text-2xl font-medium text-white">Не удалось получить роли</h1>
            <p className="mt-3 max-w-[560px] text-lg leading-relaxed text-[#707070]">
              Twitch временно не отвечает или не предоставляет список ролей этого канала.
            </p>
          </section>
        </main>
      </div>
    );
  }

  const roles = data.items.map((role) => ({
    id: `${role.category}-${role.twitch_id}`,
    category: role.category,
    login: role.login,
    displayName: role.display_name,
    avatarUrl: role.avatar_url,
    grantedAt: formatDate(role.granted_at),
    grantedAtTimestamp: role.granted_at ? Date.parse(role.granted_at) : 0,
    createdAt: formatDate(role.twitch_created_at),
  }));

  return (
    <div className="min-h-dvh bg-black text-white">
      <AppHeader />
      <RolesResults
        initialRoles={roles}
        profile={
          <ChannelProfileCard
            channel={data.channel}
            login={login}
            stats={[
              {
                label: "дата создания",
                value: formatDate(data.channel.twitch_created_at),
              },
              {
                label: "фолловеров",
                value: data.followers_total?.toLocaleString("ru-RU") ?? "Нет данных",
              },
              {
                label: "фолловов",
                value: data.follows_total?.toLocaleString("ru-RU") ?? "Нет данных",
              },
            ]}
          />
        }
        stats={data.stats}
      />
    </div>
  );
}
