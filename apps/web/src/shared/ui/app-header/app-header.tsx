import { Button } from "@workspace/ui/components/button";

export function AppHeader() {
  return (
    <header className="absolute left-0 top-0 h-[100px] w-full border-b border-[#252525] bg-black/85 backdrop-blur-[25px]">
      <div className="mx-auto flex h-full w-full max-w-[1920px] items-center justify-between px-6">
        <a
          className="flex h-[41px] min-w-0 items-center gap-3 text-white"
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

        <div className="relative h-[50px] w-[133px] overflow-hidden rounded-[50px] border border-[#252525] bg-[#0B0B0B]">
          <Button
            className="absolute left-[4px] top-[4px] h-10 rounded-[100px] bg-[#9247FF] px-3 py-[10px] !text-lg !font-medium !leading-normal hover:bg-[#772CE8] active:bg-[#772CE8]"
            size="lg"
            type="button"
          >
            Войти
          </Button>
          <Button
            className="absolute left-[87px] top-[4px] size-10 rounded-full hover:bg-[#1F1F1F] active:bg-[#1F1F1F]"
            size="icon-lg"
            variant="ghost"
            aria-label="Открыть меню"
            type="button"
          >
            <span className="flex h-[11px] w-[18px] flex-col justify-between">
              <span className="block h-[3px] w-[18px] rounded-full bg-white" />
              <span className="block h-[3px] w-[18px] rounded-full bg-white" />
            </span>
          </Button>
        </div>
      </div>
    </header>
  );
}
