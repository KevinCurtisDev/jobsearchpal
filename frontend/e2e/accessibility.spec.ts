import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const pages = ["/", "/sign-in", "/app", "/app/cv", "/app/jobs", "/app/interviews", "/app/settings"];

for (const path of pages) {
  test(`no axe violations (WCAG 2.2 AA) on ${path}`, async ({ page }) => {
    await page.goto(path);
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();
    expect(results.violations).toEqual([]);
  });
}

test("skip link moves focus to main content", async ({ page }) => {
  await page.goto("/app");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to main content" })).toBeFocused();
});

// Stage 1: passkey sign-in using a virtual authenticator, e.g.
// const cdp = await page.context().newCDPSession(page);
// await cdp.send("WebAuthn.enable");
// await cdp.send("WebAuthn.addVirtualAuthenticator", { options: { protocol: "ctap2",
//   transport: "internal", hasResidentKey: true, hasUserVerification: true, isUserVerified: true } });
