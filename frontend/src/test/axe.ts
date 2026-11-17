import axe from "axe-core";

/** Runs axe on a rendered container. Colour contrast is checked in Playwright (real browser). */
export async function axeViolations(container: Element) {
  const results = await axe.run(container, { rules: { "color-contrast": { enabled: false } } });
  return results.violations.map((v) => `${v.id}: ${v.help}`);
}
