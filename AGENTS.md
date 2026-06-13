# AGENTS.md

## Project Shape

- This is a monorepo with `apps/api` for the FastAPI backend and `apps/web` for the frontend.
- Keep product-specific logic in the app layer instead of making the frontend call Twitch directly.
- Treat Twitch as an external data source. Store only local projections needed by the product.

## Monorepo Rules

- Keep app-specific architecture rules in each app folder's `AGENTS.md`.
- Do not duplicate detailed backend or frontend conventions in this root file.
- Prefer small, focused changes that match the package being edited.
- Do not introduce cross-app coupling unless the user explicitly asks for it.

## Data Source Rules

- Prefer official Twitch Helix when it can provide the required data.
- Use unofficial Twitch GraphQL only through a dedicated adapter.
- Do not let GraphQL query shape leak into frontend contracts.
