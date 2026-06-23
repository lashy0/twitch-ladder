"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/avatar";

import type { Follow } from "./types";

export const followColumns: ColumnDef<Follow>[] = [
  {
    id: "number",
    header: "#",
    size: 150,
  },
  {
    accessorKey: "displayName",
    header: "Канал",
    size: 350,
    cell: ({ row }) => {
      const follow = row.original;
      return (
        <div className="flex min-w-0 items-center gap-3">
          <Avatar className="size-[50px]">
            <AvatarImage className="object-cover" src={follow.avatarUrl ?? undefined} alt="" />
            <AvatarFallback>{follow.displayName.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <span className="truncate font-medium">{follow.displayName}</span>
        </div>
      );
    },
  },
  {
    accessorKey: "login",
    header: "Логин",
    size: 300,
    cell: ({ row }) => <span className="truncate">@{row.original.login}</span>,
  },
  {
    accessorKey: "language",
    header: "Регион",
    size: 150,
    filterFn: "equalsString",
    cell: ({ row }) => (
      <span>
        {row.original.languageEmoji} {row.original.language}
      </span>
    ),
  },
  {
    accessorKey: "followedAt",
    header: "Дата отслеживания",
    size: 300,
    sortingFn: (rowA, rowB) =>
      rowA.original.followedAtTimestamp - rowB.original.followedAtTimestamp,
  },
  {
    accessorKey: "createdAt",
    header: "Канал создан",
    size: 210,
  },
];
