import { describe, expect, it } from "vitest";
import { QUESTIONS, scoreSelfCheck } from "./score";

const ids = Object.fromEntries(QUESTIONS.map((q) => [q.id, q.id]));
const all = (i: number) =>
  Object.fromEntries(QUESTIONS.filter((q) => !q.practical).map((q) => [q.id, i]));

describe("scoreSelfCheck", () => {
  it("says stay when nothing pushes", () => {
    const r = scoreSelfCheck({ ...all(0), time: 1 });
    expect(r.verdict).toBe("stay");
    expect(r.reasons).toHaveLength(0);
    expect(r.applicationsPerWeek).toBe(2);
  });

  it("suggests fixing one fixable issue first, with a specific tip", () => {
    const r = scoreSelfCheck({ ...all(0), pay: 3 });
    expect(r.verdict).toBe("fix_first");
    expect(r.fixTip).toContain("pay review");
    expect(r.reasons[0]?.dimension).toBe("Pay");
  });

  it("explores when there are a couple of moderate issues", () => {
    expect(scoreSelfCheck({ ...all(0), growth: 2, life_fit: 2 }).verdict).toBe("explore");
  });

  it("moves with several strong issues, or when the job is ending", () => {
    expect(scoreSelfCheck({ ...all(0), day_to_day: 3, growth: 3 }).verdict).toBe("move");
    expect(scoreSelfCheck({ ...all(0), security: 3 }).verdict).toBe("move");
  });

  it("always shows the wellbeing note when stress affects sleep or health", () => {
    const r = scoreSelfCheck({ ...all(0), stress: 3 });
    expect(r.wellbeingNote).toContain("GP");
    expect(r.verdict).toBe("fix_first");
  });

  it("points to salary research when unsure about pay, without counting it as a strong reason", () => {
    const r = scoreSelfCheck({ ...all(0), pay: 4 });
    expect(r.payUnsureNote).not.toBeNull();
    expect(r.verdict).toBe("stay");
  });

  it("ignores unanswered questions and rejects invalid answers", () => {
    expect(scoreSelfCheck({}).verdict).toBe("stay");
    expect(() => scoreSelfCheck({ [ids.pay!]: 9 })).toThrow();
  });

  it("asks the in-a-year question only when there are reasons", () => {
    expect(scoreSelfCheck(all(0)).inAYear).toBeNull();
    const r = scoreSelfCheck({ ...all(0), life_fit: 3, people: 3 });
    expect(r.inAYear?.question).toContain("in a year");
    expect(r.reasons.every((x) => x.durability === "lasts")).toBe(true);
    expect(r.inAYear?.glowNote).not.toBeNull();
    expect(r.inAYear?.fadesOnlyNote).toBeNull();
  });

  it("flags when the only reason is one that tends to fade, without changing the verdict", () => {
    const r = scoreSelfCheck({ ...all(0), pay: 3 });
    expect(r.verdict).toBe("fix_first");
    expect(r.reasons[0]?.durability).toBe("fades");
    expect(r.inAYear?.fadesOnlyNote).toContain("something that lasts");
    expect(r.inAYear?.glowNote).toBeNull();
  });

  it("leaves the general feeling question untagged", () => {
    const r = scoreSelfCheck({ ...all(0), day_to_day: 3, pay: 3 });
    expect(r.reasons.find((x) => x.id === "day_to_day")?.durability).toBeNull();
    expect(r.inAYear?.fadesOnlyNote).toBeNull();
  });
});
