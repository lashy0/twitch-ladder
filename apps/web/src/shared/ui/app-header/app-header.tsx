"use client";

import { DropdownMenu } from "@workspace/ui/components/dropdown-menu";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { getApiUrl } from "@/shared/lib/api";
import { getCategoryHref, getLadderHref, normalizeTwitchLogin } from "@/shared/lib/routes";

import { AnonymousMenu } from "./anonymous-menu";
import { HeaderMenuControl } from "./header-menu-control";
import { ProfileMenu } from "./profile-menu";
import { getActiveMenuCategory } from "./types";
import type { AuthSession, MenuCategory } from "./types";

export function AppHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [session, setSession] = useState<AuthSession>({ authenticated: false, user: null });
  const [nickname, setNickname] = useState("");
  const [menuError, setMenuError] = useState("");
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const user = session.user;
  const activeCategory = getActiveMenuCategory(pathname);

  useEffect(() => {
    let ignore = false;

    async function loadSession() {
      try {
        const response = await fetch(getApiUrl("/api/v1/auth/me"), {
          credentials: "include",
        });
        if (!response.ok) return;

        const nextSession = (await response.json()) as AuthSession;
        if (!ignore) {
          setSession(nextSession);
          if (nextSession.user) setNickname(nextSession.user.login);
        }
      } catch {
        // Anonymous navigation remains available while the API is unavailable.
      }
    }

    loadSession();
    return () => {
      ignore = true;
    };
  }, []);

  function login() {
    window.location.href = getApiUrl("/api/v1/auth/twitch/login");
  }

  async function logout() {
    setIsLoggingOut(true);
    try {
      await fetch(getApiUrl("/api/v1/auth/logout"), {
        credentials: "include",
        method: "POST",
      });
      setSession({ authenticated: false, user: null });
      setNickname("");
      setIsOpen(false);
    } finally {
      setIsLoggingOut(false);
    }
  }

  function navigateFromMenu(category: MenuCategory) {
    const login = normalizeTwitchLogin(nickname);
    if (!login) {
      setMenuError("Введите никнейм.");
      return;
    }

    const href =
      category === "ladder" ? getLadderHref(login) : getCategoryHref(category, login);
    setIsOpen(false);
    router.push(href);
  }

  function submitMenu(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const submitter = (event.nativeEvent as SubmitEvent).submitter;
    const category = submitter?.getAttribute("data-category") as MenuCategory | null;

    if (category) navigateFromMenu(category);
  }

  return (
    <header className="pointer-events-auto fixed left-0 top-0 z-[100] h-[100px] w-full border-b border-[#252525] bg-black/85 backdrop-blur-[25px]">
      <div className="flex h-full w-full items-center justify-between px-6">
        <a
          className="flex h-[41px] min-w-0 cursor-pointer items-center gap-3 text-white"
          href="/"
          aria-label="Twitch Ladder"
        >
          <span className="flex h-8 w-[30px] shrink-0 items-center justify-center">
            <img src="/icons/logo.svg" alt="" width="30" height="32" />
          </span>
          <span className="truncate text-[32px] font-semibold leading-[39px] tracking-normal">
            Twitch Ladder
          </span>
        </a>

        <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
          <HeaderMenuControl
            isOpen={isOpen}
            user={user}
            onLogin={login}
            onProfileClick={() => setIsOpen((value) => !value)}
          />

          {user ? (
            <ProfileMenu user={user} isLoggingOut={isLoggingOut} onLogout={logout} />
          ) : (
            <AnonymousMenu
              activeCategory={activeCategory}
              error={menuError}
              nickname={nickname}
              onNicknameChange={(value) => {
                setNickname(value);
                setMenuError("");
              }}
              onNavigate={navigateFromMenu}
              onSubmit={submitMenu}
            />
          )}
        </DropdownMenu>
      </div>
    </header>
  );
}
