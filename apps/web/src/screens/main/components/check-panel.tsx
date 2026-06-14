"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { CheckCategory, getCategoryHref, normalizeTwitchLogin } from "@/shared/lib/routes";
import { Button } from "@workspace/ui/components/button";
import { Input } from "@workspace/ui/components/input";
import { Panel } from "@workspace/ui/components/panel";

const categories: Array<{ value: CheckCategory; label: string }> = [
  { value: "follow", label: "Подписки" },
  { value: "roles", label: "Роли" },
  { value: "vod", label: "VOD" },
];

export function CheckPanel() {
  const router = useRouter();
  const [nickname, setNickname] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<CheckCategory | null>(null);
  const [error, setError] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const login = normalizeTwitchLogin(nickname);

    if (!login) {
      setError("Введите Twitch никнейм.");
      return;
    }

    if (!selectedCategory) {
      setError("Выберите категорию проверки.");
      return;
    }

    setError("");
    router.push(getCategoryHref(selectedCategory, login));
  }

  return (
    <Panel className="relative h-[302px] overflow-hidden">
      <form className="absolute inset-0" onSubmit={submit}>
        <div className="absolute left-[29px] top-[29px] flex w-[940px] items-center gap-5">
          <div className="relative h-[77px] w-[730px] shrink-0">
            <Input
              className="h-[77px] w-[730px] rounded-full border border-[#252525] bg-[#0B0B0B] px-[34px] !text-2xl !font-medium !leading-normal placeholder:!text-2xl placeholder:!font-medium placeholder:text-[#707070] focus:border-[#252525]"
              aria-describedby={error ? "nickname-error" : undefined}
              aria-invalid={Boolean(error)}
              autoComplete="off"
              name="nickname"
              onChange={(event) => {
                setNickname(event.target.value);
                if (error) {
                  setError("");
                }
              }}
              placeholder="Никнейм"
              value={nickname}
            />
            {error ? (
              <p
                className="absolute left-0 top-[82px] px-[34px] text-sm font-medium text-red-300"
                id="nickname-error"
              >
                {error}
              </p>
            ) : null}
          </div>

          <Button
            className="h-[77px] shrink-0 rounded-full bg-[#9247FF] px-[30px] !text-2xl !font-medium !leading-normal hover:bg-[#7a3ad6] active:bg-[#6b30c0]"
            size="lg"
            type="submit"
          >
            Проверить
          </Button>
        </div>

        <div className="absolute left-[29px] top-[141px] flex items-center gap-[20px]">
          {categories.map((category) => {
            const isSelected = selectedCategory === category.value;

            return (
              <button
                aria-pressed={isSelected}
                className={[
                  "h-[130px] w-[300px] shrink-0 rounded-[25px] border border-[#252525] bg-[#0B0B0B] p-[10px] !text-2xl !font-medium !leading-normal text-white transition",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-app-accent)]",
                  isSelected
                    ? "!border-[#9247FF] !bg-[#12081B]"
                    : "hover:border-[#4C4C4C] hover:bg-[#0B0B0B]",
                ].join(" ")}
                key={category.value}
                onClick={() => setSelectedCategory(category.value)}
                type="button"
              >
                {category.label}
              </button>
            );
          })}
        </div>
      </form>
    </Panel>
  );
}
