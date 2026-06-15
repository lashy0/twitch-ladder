import { Button } from "@workspace/ui/components/button";
import { DropdownMenuTrigger } from "@workspace/ui/components/dropdown-menu";
import { cn } from "@workspace/ui/lib/utils";
import { MenuIcon } from "lucide-react";

import type { AuthUser } from "./types";

type HeaderMenuControlProps = {
  isOpen: boolean;
  user: AuthUser | null;
  onLogin: () => void;
  onProfileClick: () => void;
};

export function HeaderMenuControl({
  isOpen,
  user,
  onLogin,
  onProfileClick,
}: HeaderMenuControlProps) {
  return (
    <div className="relative flex h-[50px] w-[320px] justify-end">
      <div
        className={cn(
          "relative h-[50px] overflow-hidden rounded-[50px] border border-[#252525] bg-[#0B0B0B]",
          user ? "w-[95px]" : "w-[133px]",
        )}
      >
        {user ? (
          <button
            className="absolute left-[4px] top-[4px] size-10 cursor-pointer overflow-hidden rounded-full border border-[#252525] bg-[#18181B]"
            type="button"
            aria-label={`Профиль ${user.display_name}`}
            onClick={onProfileClick}
          >
            {user.avatar_url ? (
              <img
                className="size-full object-cover"
                src={user.avatar_url}
                alt=""
                width="40"
                height="40"
              />
            ) : null}
          </button>
        ) : (
          <Button
            className="absolute left-[4px] top-[4px] h-10 cursor-pointer rounded-[100px] bg-[#9247FF] px-3 py-[10px] !text-lg !font-medium !leading-normal hover:bg-[#772CE8] active:bg-[#772CE8]"
            size="lg"
            type="button"
            onClick={onLogin}
          >
            Войти
          </Button>
        )}

        <DropdownMenuTrigger asChild>
          <Button
            className={cn(
              "absolute top-[4px] size-10 cursor-pointer rounded-full hover:bg-[#1F1F1F] active:bg-[#1F1F1F]",
              user ? "left-[49px]" : "left-[87px]",
              isOpen && "bg-[#1F1F1F]",
            )}
            size="icon-lg"
            variant="ghost"
            aria-expanded={isOpen}
            aria-label={isOpen ? "Закрыть меню" : "Открыть меню"}
            type="button"
          >
            <MenuIcon aria-hidden="true" strokeWidth={3} />
          </Button>
        </DropdownMenuTrigger>
      </div>
    </div>
  );
}
