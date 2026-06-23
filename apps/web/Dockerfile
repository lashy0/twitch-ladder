FROM node:24-bookworm-slim AS base

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

FROM base AS deps

WORKDIR /app/apps/web

COPY apps/web/package.json apps/web/package-lock.json ./

RUN npm ci

FROM base AS dev

COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--prefix", "apps/web"]

FROM base AS builder

COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
COPY . .

RUN npm run build --prefix apps/web

FROM base AS runner

ENV NODE_ENV=production

WORKDIR /app/apps/web

COPY apps/web/package.json apps/web/package-lock.json ./

RUN npm ci --omit=dev

COPY --from=builder /app/apps/web/.next ./.next
COPY --from=builder /app/apps/web/public ./public
COPY --from=builder /app/apps/web/next.config.ts ./next.config.ts

EXPOSE 3000

CMD ["npm", "run", "start"]
