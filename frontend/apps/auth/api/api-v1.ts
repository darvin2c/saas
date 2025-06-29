import createFetchClient from "openapi-fetch";
import type { paths } from "./types/v1.js";
import createClient from "openapi-react-query";

export const $fetchClientV1 = createFetchClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/v1",
});

export const $apiV1 = createClient($fetchClientV1);
