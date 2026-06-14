import type { InputHTMLAttributes } from "react";

import { cn } from "#lib/utils";

export function TextInput({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "w-full text-white outline-none",
        className,
      )}
      {...props}
    />
  );
}
