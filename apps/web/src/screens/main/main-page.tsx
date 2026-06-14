import { Background } from "./components/background";
import { CheckPanel } from "./components/check-panel";
import { LadderShortcut } from "./components/ladder-shortcut";
import { AppHeader } from "@/shared/ui/app-header/app-header";

export function MainPage() {
  return (
    <div className="relative flex min-h-dvh flex-col overflow-hidden bg-black">
      <Background />

      <AppHeader />

      <main className="relative flex flex-1 items-center justify-center pt-[100px]">
        <div className="flex w-[1000px] flex-col gap-6">
          <section className="flex flex-col gap-12">
            <div className="flex flex-col gap-6">
              <p className="flex items-center gap-2 text-2xl font-normal leading-none text-white">
                <img
                  className="hi-cat-icon h-[25px] w-[30px]"
                  src="/images/hi-cat.webp"
                  alt=""
                  width="30"
                  height="25"
                />
                <span>Hi</span>
              </p>
              <h1 className="text-[32px] font-medium leading-none tracking-normal text-white">
                Введи никнейм Twitch и выбери категорию проверки
              </h1>
            </div>

            <CheckPanel />
          </section>

          <LadderShortcut />
        </div>
      </main>
    </div>
  );
}
