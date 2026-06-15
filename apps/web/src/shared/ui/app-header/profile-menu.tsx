import {
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@workspace/ui/components/dropdown-menu";
import { LogOutIcon } from "lucide-react";

import { menuContentSideOffset } from "./types";
import type { AuthUser } from "./types";

type ProfileMenuProps = {
  user: AuthUser;
  isLoggingOut: boolean;
  onLogout: () => void;
};

export function ProfileMenu({ user, isLoggingOut, onLogout }: ProfileMenuProps) {
  return (
    <DropdownMenuContent
      align="end"
      sideOffset={menuContentSideOffset}
      className="z-[200] h-[195px] w-[320px] overflow-hidden rounded-[25px] border-[#252525] bg-black p-0 text-white shadow-[0_24px_80px_rgb(0_0_0_/_45%)]"
    >
      <div className="flex h-[117px] items-center gap-3 px-[23px]">
        <div className="size-[70px] overflow-hidden rounded-full border border-[#252525] bg-[#18181B]">
          {user.avatar_url ? (
            <img
              className="size-full object-cover"
              src={user.avatar_url}
              alt=""
              width="70"
              height="70"
            />
          ) : null}
        </div>
        <div className="flex min-w-0 flex-col gap-[5px]">
          <p className="truncate text-2xl font-normal leading-normal text-white">
            {user.display_name}
          </p>
          <p className="truncate text-lg font-normal leading-normal text-[#707070]">
            @{user.login}
          </p>
        </div>
      </div>

      <DropdownMenuSeparator className="m-0 bg-[#252525]" />

      <DropdownMenuGroup className="px-[11px] pt-[11px]">
        <DropdownMenuItem
          className="flex h-[53px] w-full cursor-pointer items-center gap-2 rounded-[15px] px-3 py-[10px] text-left text-2xl font-normal leading-normal text-[#F96868] outline-none transition focus:bg-[#280D0D] focus:text-[#F96868] data-[disabled]:cursor-default data-[disabled]:opacity-60"
          disabled={isLoggingOut}
          onSelect={(event) => {
            event.preventDefault();
            onLogout();
          }}
        >
          <LogOutIcon aria-hidden="true" />
          <span>{isLoggingOut ? "Выходим..." : "Выйти"}</span>
        </DropdownMenuItem>
      </DropdownMenuGroup>
    </DropdownMenuContent>
  );
}
