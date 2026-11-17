import createClient from "openapi-fetch";

/**
 * Typed API client. Run `npm run api:generate` (with the backend running) to create
 * src/api/schema.d.ts, then use: createClient<paths>({ ... }).
 * Every state-changing request sends the CSRF token from the __Host-ol_csrf cookie.
 */
export function csrfToken(): string | undefined {
  return document.cookie
    .split("; ")
    .find((c) => c.startsWith("__Host-ol_csrf="))
    ?.split("=")[1];
}

export const api = createClient({
  baseUrl: "/api/v1",
  credentials: "include",
});

api.use({
  onRequest({ request }) {
    if (!["GET", "HEAD", "OPTIONS"].includes(request.method)) {
      const token = csrfToken();
      if (token) request.headers.set("X-CSRF-Token", token);
    }
    return request;
  },
});
