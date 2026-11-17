import type { RouteObject } from "react-router";
import { AppShell } from "./layouts/AppShell";
import { MarketingLayout } from "./layouts/MarketingLayout";
import { Landing } from "./pages/Landing";
import { NotFound } from "./pages/NotFound";
import { PagePlaceholder } from "./pages/PagePlaceholder";

const p = (title: string, stage: string, spec: string) => (
  <PagePlaceholder title={title} stage={stage} spec={spec} />
);

/** Every screen from docs/08-screens.md. Placeholders are replaced stage by stage. */
export const routes: RouteObject[] = [
  {
    element: <MarketingLayout />,
    children: [
      { path: "/", element: <Landing /> },
      { path: "/cv-check", element: p("Free CV check", "Stage 4", "08-screens.md §Free CV check") },
      {
        path: "/linkedin-check",
        element: p("Free LinkedIn check", "Stage 4", "08-screens.md §Free LinkedIn check"),
      },
      {
        path: "/should-i-move",
        element: p("Should I move? (free self-check)", "Stage 4", "08-screens.md §Should I move?"),
      },
      { path: "/sign-in", element: p("Sign in", "Stage 1", "08-screens.md §Sign in") },
      { path: "/sign-up", element: p("Create your account", "Stage 1", "08-screens.md §Sign in") },
    ],
  },
  {
    path: "/app",
    element: <AppShell />,
    children: [
      {
        index: true,
        element: p("Where you stand", "Stage 9 (shell in Stage 1)", "08-screens.md §Home"),
      },
      { path: "cv", element: p("CV builder", "Stage 2", "08-screens.md §CV builder") },
      { path: "tailor", element: p("Tailor to a job", "Stage 3", "08-screens.md §Tailor") },
      {
        path: "linkedin",
        element: p("LinkedIn profile", "Stage 3", "08-screens.md §LinkedIn profile"),
      },
      { path: "jobs", element: p("Today's matches", "Stage 6", "08-screens.md §Job matches") },
      { path: "jobs/:id", element: p("Job detail", "Stage 6–7", "08-screens.md §Job detail") },
      {
        path: "applications",
        element: p("Applications", "Stage 7–8", "08-screens.md §Applications"),
      },
      {
        path: "insights",
        element: p("What works for you", "Stage 9", "08-screens.md §What works"),
      },
      {
        path: "interviews",
        element: p("Interview prep", "Stage 10", "08-screens.md §Interview prep"),
      },
      {
        path: "settings",
        element: p("Privacy and settings", "Stage 1", "08-screens.md §Privacy and settings"),
      },
    ],
  },
  { path: "*", element: <NotFound /> },
];
