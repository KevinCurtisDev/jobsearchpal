import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { axeViolations } from "../test/axe";
import { Badge } from "./Badge";
import { Button } from "./Button";

describe("Button", () => {
  it("is a real button that responds to keyboard and click", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Start free</Button>);
    const button = screen.getByRole("button", { name: "Start free" });
    expect(button).toHaveAttribute("type", "button");
    await userEvent.tab();
    expect(button).toHaveFocus();
    await userEvent.keyboard("{Enter}");
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("has no axe violations", async () => {
    const { container } = render(
      <div>
        <Button>Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button aria-label="Save job">★</Button>
        <Badge tone="criticalSkills">Critical Skills role</Badge>
      </div>,
    );
    expect(await axeViolations(container)).toEqual([]);
  });
});
