import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  [
    "inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all outline-none",
    "focus-visible:border-[var(--color-app-accent)] focus-visible:ring-4 focus-visible:ring-[rgb(145_70_255_/_18%)]",
    "disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-red-400 aria-invalid:ring-red-400/20",
    "[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  ],
  {
    variants: {
      variant: {
        default:
          "bg-[var(--color-app-accent)] text-white hover:bg-[var(--color-app-accent-hover)] active:bg-[var(--color-app-accent-active)]",
        destructive: "bg-red-600 text-white hover:bg-red-600/90 focus-visible:ring-red-400/20",
        outline:
          "border border-white/10 bg-[var(--color-app-surface)] text-white shadow-xs hover:bg-[var(--color-app-surface-hover)]",
        secondary:
          "bg-[var(--color-app-panel)] text-white hover:bg-[var(--color-app-border)]",
        ghost: "text-white hover:bg-white/[0.08] active:bg-white/[0.05]",
        link: "text-[var(--color-app-accent)] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        xs: "h-6 gap-1 rounded-md px-2 text-xs has-[>svg]:px-1.5 [&_svg:not([class*='size-'])]:size-3",
        sm: "h-8 gap-1.5 rounded-md px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9",
        "icon-xs": "size-6 rounded-md [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

type ButtonProps = ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  };

export function Button({
  asChild = false,
  className,
  size = "default",
  variant = "default",
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      data-size={size}
      data-slot="button"
      data-variant={variant}
      {...props}
    />
  );
}

export { buttonVariants };
