import createFetchClient from "openapi-fetch";
import type { paths } from "./v1.d.ts";
export const fetchClient = createFetchClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/v1",
});
