import { render, screen } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router";
import { describe, expect, it } from "vitest";
import { routes } from "./routes";
import { axeViolations } from "./test/axe";

function renderAt(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] });
  return render(<RouterProvider router={router} />);
}

describe("routes", () => {
  it("renders the landing page headline", () => {
    renderAt("/");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/offers received/i);
  });

  it("renders the app shell with a skip link and current nav item", async () => {
    const { container } = renderAt("/app/cv");
    expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveAttribute(
      "href",
      "#main",
    );
    expect(screen.getByRole("link", { name: "CV builder" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("main")).toBeInTheDocument();
    expect(await axeViolations(container)).toEqual([]);
  });

  it("shows not found for unknown routes", () => {
    renderAt("/nope");
    expect(screen.getByRole("heading", { name: "Page not found" })).toBeInTheDocument();
  });
});
