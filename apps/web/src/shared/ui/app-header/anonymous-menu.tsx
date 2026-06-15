import {
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@workspace/ui/components/dropdown-menu";
import { cn } from "@workspace/ui/lib/utils";
import { ArrowRightIcon } from "lucide-react";
import type { FormEvent } from "react";

import { menuContentSideOffset, menuItems } from "./types";
import type { MenuCategory } from "./types";

type AnonymousMenuProps = {
  activeCategory: MenuCategory | null;
  error: string;
  nickname: string;
  onNicknameChange: (value: string) => void;
  onNavigate: (category: MenuCategory) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

export function AnonymousMenu({
  activeCategory,
  error,
  nickname,
  onNicknameChange,
  onNavigate,
  onSubmit,
}: AnonymousMenuProps) {
  return (
    <DropdownMenuContent
      align="end"
      sideOffset={menuContentSideOffset}
      className="z-[200] h-[450px] w-[320px] overflow-hidden rounded-[35px] border-[#252525] bg-black p-0 text-white shadow-[0_24px_80px_rgb(0_0_0_/_45%)]"
    >
      <form className="relative h-full" onSubmit={onSubmit}>
        <div className="absolute left-[23px] top-[23px] flex h-[50px] w-[272px] items-center gap-3 rounded-full border border-[#252525] bg-[#0B0B0B] pl-3 pr-[5px]">
          <input
            className="min-w-0 flex-1 bg-transparent text-lg font-medium leading-normal text-white outline-none placeholder:text-[#707070]"
            name="header-nickname"
            placeholder="Никнейм"
            value={nickname}
            onChange={(event) => onNicknameChange(event.target.value)}
          />
          <button
            className="flex size-10 cursor-pointer items-center justify-center rounded-full bg-[#18181B] text-white transition hover:bg-[#1F1F1F]"
            type="submit"
            data-category="ladder"
            aria-label="Открыть Ladder"
          >
            <ArrowRightIcon aria-hidden="true" />
          </button>
        </div>

        {error ? (
          <p className="absolute left-[35px] top-[77px] text-sm text-red-300">{error}</p>
        ) : null}

        <DropdownMenuSeparator className="absolute left-[-1px] top-[97px] m-0 w-[320px] bg-[#252525]" />

        <DropdownMenuGroup className="absolute left-[23px] top-[121px] flex w-[272px] flex-col p-0">
          {menuItems.map((item) => {
            const active = activeCategory === item.category;

            return (
              <DropdownMenuItem
                key={item.category}
                className={cn(
                  "flex h-[53px] w-[272px] cursor-pointer items-center rounded-[15px] px-3 py-[10px] text-2xl font-normal leading-normal outline-none transition focus:bg-[#1F1F1F]",
                  active ? "text-[#9247FF] focus:text-[#9247FF]" : "text-white focus:text-white",
                )}
                onSelect={(event) => {
                  event.preventDefault();
                  onNavigate(item.category);
                }}
              >
                {item.label}
              </DropdownMenuItem>
            );
          })}
        </DropdownMenuGroup>

        <DropdownMenuSeparator className="absolute left-[-1px] top-[357px] m-0 w-[320px] bg-[#252525]" />

        <p className="absolute left-[23px] top-[381px] w-[272px] text-lg font-normal leading-normal text-[#707070]">
          Здесь можно быстро сменить ник и категорию для проверки
        </p>
      </form>
    </DropdownMenuContent>
  );
}
