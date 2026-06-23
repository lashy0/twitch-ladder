"use client";

import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import type { ColumnFiltersState, SortingState } from "@tanstack/react-table";
import { Button } from "@/components/button";
import { Empty, EmptyHeader, EmptyTitle } from "@/components/empty";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/dropdown-menu";
import { Input } from "@/components/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/table";
import { cn } from "@/lib/utils";
import { ChevronDownIcon, FilterIcon } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { ComponentProps } from "react";

import { followColumns } from "./columns";
import { languageEmoji, languageLabel } from "./languages";
import type { Follow, FollowResponse } from "./types";

type DateOrder = "new" | "old";

export function FollowDataTable({
  data,
  regions,
  hasMore,
  onLoadMore,
}: {
  data: Follow[];
  regions: FollowResponse["regions"];
  hasMore: boolean;
  onLoadMore: () => void;
}) {
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [search, setSearch] = useState("");
  const [dateOrder, setDateOrder] = useState<DateOrder>("new");
  const [region, setRegion] = useState("ALL");
  const [sorting, setSorting] = useState<SortingState>([{ id: "followedAt", desc: true }]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const table = useReactTable({
    data,
    columns: followColumns,
    state: {
      globalFilter: search,
      sorting,
      columnFilters,
    },
    onGlobalFilterChange: setSearch,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    globalFilterFn: (row, _columnId, value) => {
      const query = String(value).trim().toLocaleLowerCase("ru-RU");
      if (!query) return true;
      return `${row.original.displayName} ${row.original.login}`
        .toLocaleLowerCase("ru-RU")
        .includes(query);
    },
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  function changeDateOrder(value: DateOrder) {
    setDateOrder(value);
    setSorting([{ id: "followedAt", desc: value === "new" }]);
  }

  function changeRegion(value: string) {
    setRegion(value);
    table.getColumn("language")?.setFilterValue(value === "ALL" ? undefined : value);
  }

  const selectedRegion = regions.find((item) => item.language === region);

  useEffect(() => {
    const target = loadMoreRef.current;
    if (!target || !hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) onLoadMore();
      },
      {
        root: scrollContainerRef.current,
        rootMargin: "300px 0px",
      },
    );
    observer.observe(target);
    return () => observer.disconnect();
  }, [hasMore, onLoadMore]);

  return (
    <div className="flex min-w-0 flex-col gap-3">
      <div className="flex items-center gap-3">
        <Input
          className="h-[50px] w-[400px] rounded-full border-[#252525] px-6 !text-lg font-medium shadow-none placeholder:font-medium placeholder:text-[#707070] focus-visible:border-[#252525] focus-visible:ring-0 md:!text-lg"
          placeholder="Поиск"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <Button className="h-[50px] rounded-full px-6 text-lg" variant="outline">
              <FilterIcon data-icon="inline-start" />
              {dateOrder === "new" ? "Новые" : "Старые"}
              <ChevronDownIcon data-icon="inline-end" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            align="start"
            className="w-[185px] rounded-[20px] border-[#252525] bg-[#0b0b0b] p-3"
            sideOffset={12}
          >
            <DropdownMenuGroup>
              <FilterItem active={dateOrder === "new"} onSelect={() => changeDateOrder("new")}>
                Новые
              </FilterItem>
              <FilterItem active={dateOrder === "old"} onSelect={() => changeDateOrder("old")}>
                Старые
              </FilterItem>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <Button className="h-[50px] rounded-full px-6 text-lg" variant="outline">
              <FilterIcon data-icon="inline-start" />
              {selectedRegion
                ? `${languageEmoji(selectedRegion.language)} ${languageLabel(selectedRegion.language)}`
                : "Все регионы"}
              <ChevronDownIcon data-icon="inline-end" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            align="start"
            className="w-[205px] rounded-[20px] border-[#252525] bg-[#0b0b0b] p-3"
            sideOffset={12}
          >
            <DropdownMenuGroup>
              <FilterItem active={region === "ALL"} onSelect={() => changeRegion("ALL")}>
                Все регионы
              </FilterItem>
              {regions.map((item) => (
                <FilterItem
                  key={item.language}
                  active={region === item.language}
                  onSelect={() => changeRegion(item.language)}
                >
                  {languageEmoji(item.language)} {languageLabel(item.language)}
                </FilterItem>
              ))}
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div
        className="h-[870px] overflow-auto rounded-[15px] border border-[#252525] bg-[#0b0b0b] [scrollbar-width:none] [&>[data-slot=table-container]]:overflow-visible [&::-webkit-scrollbar]:hidden"
        ref={scrollContainerRef}
      >
        <Table className="w-[1460px] min-w-[1460px] table-fixed border-separate border-spacing-0 text-lg">
          <TableHeader className="[&_tr]:border-[#252525]">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow
                className="h-[54px] border-[#252525] hover:bg-transparent"
                key={headerGroup.id}
              >
                {headerGroup.headers.map((header) => (
                  <TableHead
                    className="sticky top-0 z-10 h-[54px] bg-[#0b0b0b] p-0 pl-6 pt-[15px] align-top text-lg font-medium leading-normal text-white shadow-[inset_0_-1px_0_#252525]"
                    key={header.id}
                    style={{ width: header.getSize() }}
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row, rowIndex) => (
                <TableRow
                  className="h-[82px] border-0 align-top hover:bg-transparent [&:hover>td]:bg-[#101013] [&>td]:h-[66px] [&>td]:border-b [&>td]:border-[#252525]"
                  key={row.id}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell
                      className={cn(
                        "px-6 font-normal",
                        cell.column.id === "number" && "font-medium",
                      )}
                      key={cell.id}
                    >
                      {cell.column.id === "number"
                        ? rowIndex + 1
                        : flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell className="h-56 p-0" colSpan={followColumns.length}>
                  <Empty className="border-0 p-6">
                    <EmptyHeader>
                      <EmptyTitle className="text-[#707070]">Ничего не найдено</EmptyTitle>
                    </EmptyHeader>
                  </Empty>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <div aria-hidden="true" className="h-px" ref={loadMoreRef} />
      </div>
    </div>
  );
}

function FilterItem({
  active,
  className,
  ...props
}: ComponentProps<typeof DropdownMenuItem> & { active: boolean }) {
  return (
    <DropdownMenuItem
      className={cn(
        "h-[46px] rounded-[10px] px-3 text-lg text-[#707070] focus:bg-[#1f1f1f] focus:text-white",
        active && "text-white",
        className,
      )}
      {...props}
    />
  );
}
