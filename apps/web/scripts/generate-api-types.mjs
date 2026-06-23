import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";

const require = createRequire(import.meta.url);

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const input = process.env.OPENAPI_INPUT ?? `${apiBaseUrl.replace(/\/$/, "")}/openapi.json`;
const output = "src/shared/api/schema.ts";
const packagePath = require.resolve("openapi-typescript/package.json");
const cliPath = join(dirname(packagePath), "bin", "cli.js");

const result = spawnSync(
  process.execPath,
  [cliPath, input, "--output", output, "--export-type"],
  { stdio: "inherit" },
);

if (result.status !== 0) {
  process.exit(result.status ?? 1);
}
