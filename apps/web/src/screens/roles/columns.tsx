"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/avatar";

import type { RoleEntry } from "./types";

export const roleColumns: ColumnDef<RoleEntry>[] = [
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
      const role = row.original;
      return (
        <div className="flex min-w-0 items-center gap-3">
          <Avatar className="size-[50px]">
            <AvatarImage className="object-cover" src={role.avatarUrl ?? undefined} alt="" />
            <AvatarFallback>{role.displayName.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <span className="truncate font-medium">{role.displayName}</span>
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
    accessorKey: "grantedAt",
    header: "Дата выдачи",
    size: 300,
    sortingFn: (rowA, rowB) => rowA.original.grantedAtTimestamp - rowB.original.grantedAtTimestamp,
  },
  {
    accessorKey: "createdAt",
    header: "Канал создан",
    size: 360,
  },
];
