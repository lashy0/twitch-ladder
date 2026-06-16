import createClient from "openapi-fetch";

import { getApiBaseUrl } from "@/shared/lib/api";
import type { paths } from "./schema";

export function getApiClient() {
  const baseUrl = getApiBaseUrl().replace(/\/$/, "");
  return createClient<paths>({
    baseUrl: `${baseUrl}/api/v1`,
  });
}
