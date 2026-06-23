# Twitch Ladder

## Run

Create a local env file first:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Fill required secrets in `.env`, especially Postgres and Twitch values.

Run the full stack:

```bash
docker compose up --build
```

Run the frontend service with its compose dependencies:

```bash
docker compose up --build web
```

Run only the frontend container:

```bash
docker compose up --build --no-deps web
```

Web opens at `http://localhost:3000`, API at `http://localhost:8000`.

For local Node development without Docker:

```bash
cd apps/web
npm install
npm run dev
```
