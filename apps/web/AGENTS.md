# AGENTS.md

## Scope

- These rules apply only to `apps/web`.
- Keep this file minimal: add requirements only when they are specific to this frontend and not obvious from the code.

## Stack

- Next.js App Router with React and TypeScript.
- Tailwind CSS v4.
- Shared components come from `@/components`.
- Formatting and linting use Oxfmt and Oxlint.

## Implementation Rules

- Do not call Twitch directly from the frontend. Add product data flows through `apps/api`.
- Keep route files thin; put screen composition under `src/screens` and reusable pieces under `src/shared`.
- Use `@/` for imports inside `apps/web/src`.
- Prefer existing `@/components` components before adding custom controls.
- Keep user-facing copy in Russian unless the surrounding screen already uses another language.
- Keep generated or mockup-specific assets in `public/`; do not inline large SVGs or image data into components.

## Validation

- For frontend changes, run the narrowest relevant checks:

```bash
npm run lint
npm run typecheck
```

- Run `npm run build` when changing routing, metadata, server/client boundaries, or build configuration.
