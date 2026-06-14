"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { getLadderHref, normalizeTwitchLogin } from "@/shared/lib/routes";


export function LadderShortcut() {
  const router = useRouter();
  const [error, setError] = useState("");

  function openLadder() {
    const input = document.querySelector<HTMLInputElement>('input[name="nickname"]');
    const login = normalizeTwitchLogin(input?.value ?? "");

    if (!login) {
      setError("Введите Twitch никнейм, чтобы открыть Ladder.");
      input?.focus();
      return;
    }

    setError("");
    router.push(getLadderHref(login));
  }

  return (
    <div className="relative h-[220px] overflow-hidden rounded-[var(--radius-app-panel)] border border-[var(--color-app-border)] bg-[var(--color-app-panel)]">
      <button
        className="absolute left-[29px] top-[29px] h-[160px] w-[940px] overflow-hidden rounded-[25px] border border-[#252525] bg-[#0B0B0B] text-left transition hover:border-[#4C4C4C] hover:bg-[#0B0B0B] active:border-[#9247FF] active:bg-[#12081B] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-app-accent)]"
        onClick={openLadder}
        type="button"
      >
        <span className="absolute left-[29px] top-[29px] flex size-[100px] items-center justify-center rounded-[15px] bg-[#18181B]">
          <img src="/icons/cup.svg" alt="" width="48" height="48" />
        </span>

        <span className="absolute left-[153px] top-[38px] flex w-[762px] flex-col gap-3 font-medium leading-normal">
          <span className="block h-[28px] !text-2xl text-white">Ladder</span>
          <span className="block !text-lg text-[#707070]">
            Топ самых активных пользователей чата выбранного стримера по данным всех загруженных и
            актуальных VOD
          </span>
          {error ? (
            <span className="mt-3 block text-sm font-medium text-red-300">{error}</span>
          ) : null}
        </span>
      </button>
    </div>
  );
}
