"use client";

import { ChannelMetricCard } from "@/shared/ui/channel-card";
import type { ReactNode } from "react";
import { useMemo, useState } from "react";

import { getRoleLabel, roleAccent } from "./mock-data";
import { RolesDataTable } from "./roles-data-table";
import type { RoleCategory, RoleEntry, RoleStat } from "./types";

export function RolesResults({
  initialRoles,
  profile,
  stats,
}: {
  initialRoles: RoleEntry[];
  profile: ReactNode;
  stats: RoleStat[];
}) {
  const [activeCategory, setActiveCategory] = useState<RoleCategory>("mods");
  const filteredRoles = useMemo(
    () => initialRoles.filter((role) => role.category === activeCategory),
    [activeCategory, initialRoles],
  );

  return (
    <main className="mx-auto flex w-full max-w-[1920px] items-start gap-3 px-6 pb-9 pt-[124px]">
      <aside className="flex w-[400px] shrink-0 flex-col gap-3">
        {profile}
        <RolesStatistics activeCategory={activeCategory} stats={stats} />
      </aside>
      <div className="min-w-0 flex-1">
        <RolesDataTable
          data={filteredRoles}
          activeCategory={activeCategory}
          onCategoryChange={setActiveCategory}
        />
      </div>
    </main>
  );
}

function RolesStatistics({
  activeCategory,
  stats,
}: {
  activeCategory: RoleCategory;
  stats: RoleStat[];
}) {
  const total = stats.reduce((sum, stat) => sum + stat.count, 0);

  return (
    <ChannelMetricCard
      title="Статистика ролей"
      items={stats.map((stat) => ({
        id: stat.category,
        label: getRoleLabel(stat.category),
        value: `${stat.count.toLocaleString("ru-RU")} (${stat.percent}%)`,
        percent: stat.percent,
        lineClassName:
          stat.category === activeCategory ? roleAccent[stat.category].line : "bg-[#707070]",
      }))}
      footer={{
        value: `${total.toLocaleString("ru-RU")} ролей`,
        label: "всего на канале",
      }}
    />
  );
}
