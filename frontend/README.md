# Offerlight frontend

React · TypeScript · Vite · React Router · TanStack Query · CSS Modules with design tokens.

```bash
npm ci
npm run dev          # http://localhost:5173 (proxies /api to the backend)
npm test             # Vitest + Testing Library + axe
npm run e2e          # Playwright + axe (needs the app running)
npm run tokens       # regenerate src/styles/tokens.css from ../design/tokens.json
npm run api:generate # regenerate API types from the running backend
```

Specs: `../docs/07-design-system.md`, `../docs/08-screens.md`.
