import { Avatar, AvatarFallback, AvatarImage } from "@workspace/ui/components/avatar";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card";
import type { ReactNode } from "react";

export type ChannelProfileCardChannel = {
  login: string;
  display_name: string | null;
  avatar_url: string | null;
  twitch_created_at: string | null;
};

export type ChannelProfileStat = {
  label: string;
  value: string;
};

export type ChannelMetricItem = {
  id: string;
  label: ReactNode;
  value: string;
  percent: number;
  lineClassName?: string;
};

export function ChannelProfileCard({
  channel,
  login,
  stats,
}: {
  channel: ChannelProfileCardChannel | null;
  login: string;
  stats: ChannelProfileStat[];
}) {
  const displayName = channel?.display_name || channel?.login || login;
  const twitchLogin = channel?.login || login;

  return (
    <Card className="relative h-[463px] overflow-hidden rounded-[15px] border-[#252525] bg-[#0b0b0b] shadow-none">
      <a
        className="absolute left-[325px] top-[23px] block size-[50px]"
        href={`https://twitch.tv/${encodeURIComponent(twitchLogin)}`}
        target="_blank"
        rel="noreferrer"
        aria-label="Открыть канал на Twitch"
      >
        <img className="size-[50px]" src="/icons/external-link.svg" alt="" />
      </a>

      <CardContent className="p-0">
        <div className="absolute left-[116px] top-[23px] flex w-[166px] flex-col items-center gap-1.5">
          <div className="flex w-full flex-col items-center gap-3">
            <Avatar className="size-[150px]">
              <AvatarImage className="object-cover" src={channel?.avatar_url ?? undefined} alt="" />
              <AvatarFallback className="bg-[#18181b] text-2xl text-white">
                {displayName.slice(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <h1 className="w-[166px] truncate text-center text-2xl font-medium leading-[29px] text-white">
              {displayName}
            </h1>
          </div>
          <p className="w-[166px] truncate text-center text-lg font-normal leading-[22px] text-[#707070]">
            @{twitchLogin}
          </p>
        </div>

        <div className="absolute left-[23px] top-[266px] grid w-[352px] grid-cols-2 gap-3 text-center">
          {stats.map((stat, index) => (
            <div
              className={
                index === 0
                  ? "col-span-2 flex h-20 flex-col justify-center gap-2 rounded-[15px] bg-[#18181b]"
                  : "flex h-20 flex-col justify-center gap-2 rounded-[15px] bg-[#18181b]"
              }
              key={stat.label}
            >
              <span className="text-lg leading-[22px] text-[#707070]">{stat.label}</span>
              <strong className="truncate px-2 text-xl font-medium leading-[24px] text-white">
                {stat.value}
              </strong>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function ChannelMetricCard({
  title,
  titleMeta,
  items,
  footer,
}: {
  title: string;
  titleMeta?: string;
  items: ChannelMetricItem[];
  footer?: {
    value: string;
    label: string;
  };
}) {
  return (
    <Card className="relative h-[457px] overflow-hidden rounded-[15px] border-[#252525] bg-[#0b0b0b] shadow-none">
      <CardHeader className="absolute left-[-1px] top-[-1px] h-[70px] w-[400px] flex-row items-center justify-between border border-[#252525] bg-[#0b0b0b] px-[23px] py-0">
        <CardTitle className="text-lg font-medium leading-[22px] text-white">{title}</CardTitle>
        {titleMeta ? (
          <span className="text-lg leading-[22px] text-[#707070]">{titleMeta}</span>
        ) : null}
      </CardHeader>

      <CardContent className="absolute left-[23px] top-[93px] flex h-[224px] w-[352px] flex-col gap-6 p-0">
        {items.map((item) => (
          <div className="flex w-full flex-col gap-2" key={item.id}>
            <div className="flex h-[22px] items-center justify-between gap-4 text-lg leading-[22px]">
              <span className="truncate font-medium">{item.label}</span>
              <span className="shrink-0 text-[#707070]">{item.value}</span>
            </div>
            <div className="relative h-2 w-full overflow-hidden rounded-[50px] bg-[#18181b]">
              <div
                className={`absolute left-0 top-0 h-2 rounded-[50px] ${
                  item.lineClassName ?? "bg-[#707070]"
                }`}
                style={{ width: `${Math.max(2, item.percent)}%` }}
              />
            </div>
          </div>
        ))}
      </CardContent>

      {footer ? (
        <CardFooter className="absolute left-[-1px] top-[341px] flex h-[115px] w-[400px] flex-col items-start border border-[#252525] bg-[#0b0b0b] p-6">
          <div className="flex w-full flex-col gap-2">
            <strong className="block h-[37px] text-[32px] font-medium leading-[37px] text-white">
              {footer.value}
            </strong>
            <span className="block text-lg leading-[22px] text-[#707070]">{footer.label}</span>
          </div>
        </CardFooter>
      ) : null}
    </Card>
  );
}
