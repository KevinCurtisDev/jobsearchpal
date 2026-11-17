/**
 * "Should I move?" self-check — scoring.
 *
 * Runs entirely in the browser: answers are never sent or stored (docs/13 §12).
 * The result is a direction with its reasons, never a numeric score: false precision
 * would mislead, and the reasons are what help people decide (CLAUDE.md rule 5).
 */
import content from "./questions.json";

export type Verdict = "stay" | "fix_first" | "explore" | "move";

export interface Question {
  id: string;
  dimension: string;
  text: string;
  options: { label: string; push?: number; hours?: number; unsure?: boolean }[];
  fixable?: boolean;
  practical?: boolean;
  /** Does dissatisfaction here last (we don't adapt to it) or fade (we adapt to the fix)? */
  durability?: Durability;
}

export type Durability = "lasts" | "fades";

export interface Reason {
  id: string;
  dimension: string;
  answer: string;
  strength: "strong" | "moderate";
  durability: Durability | null;
  durabilityLabel: string | null;
}

/** The "would this still bother you in a year?" reflection (hedonic adaptation, gently). */
export interface InAYear {
  question: string;
  glowNote: string | null;
  fadesOnlyNote: string | null;
}

export interface SelfCheckResult {
  verdict: Verdict;
  title: string;
  body: string;
  reasons: Reason[];
  fixTip: string | null;
  wellbeingNote: string | null;
  payUnsureNote: string | null;
  applicationsPerWeek: number | null;
  inAYear: InAYear | null;
}

export const QUESTIONS = content.questions as Question[];

/** answers: question id → index of the chosen option. Unanswered questions are ignored. */
export function scoreSelfCheck(answers: Record<string, number>): SelfCheckResult {
  const year = content.in_a_year;
  const reasons: Reason[] = [];
  let wellbeing = false;
  let payUnsure = false;
  let hours: number | null = null;

  for (const q of QUESTIONS) {
    const idx = answers[q.id];
    if (idx === undefined) continue;
    const opt = q.options[idx];
    if (!opt) throw new Error(`invalid answer ${idx} for ${q.id}`);
    if (q.practical) {
      hours = opt.hours ?? null;
      continue;
    }
    if (q.id === "stress" && opt.push === 3) wellbeing = true;
    if (opt.unsure) payUnsure = true;
    if ((opt.push ?? 0) >= 2) {
      reasons.push({
        id: q.id,
        dimension: q.dimension,
        answer: opt.label,
        strength: opt.push === 3 ? "strong" : "moderate",
        durability: q.durability ?? null,
        durabilityLabel: q.durability ? year.labels[q.durability] : null,
      });
    }
  }

  const strong = reasons.filter((r) => r.strength === "strong");
  const moderate = reasons.filter((r) => r.strength === "moderate");
  const fixableIds = new Set(QUESTIONS.filter((q) => q.fixable).map((q) => q.id));

  let verdict: Verdict;
  if (strong.length >= 2 || (strong.length >= 1 && moderate.length >= 2)) {
    verdict = "move";
  } else if (reasons.length === 1 && fixableIds.has(reasons[0]!.id)) {
    verdict = "fix_first";
  } else if (reasons.length >= 1) {
    verdict = "explore";
  } else {
    verdict = "stay";
  }
  // Losing the job outright is not something to "fix first".
  if (strong.some((r) => r.id === "security")) verdict = "move";

  const tips = content.fix_tips as Record<string, string>;
  const first = reasons[0];
  const v = content.verdicts[verdict];
  const perApp = content.expectations.hours_per_application;

  // Information, not a verdict change: the treadmill informs *what* to move towards.
  const fadesOnly = reasons.length > 0 && reasons.every((r) => r.durability === "fades");
  const inAYear: InAYear | null =
    reasons.length === 0
      ? null
      : {
          question: year.question,
          glowNote: verdict === "explore" || verdict === "move" ? year.glow_note : null,
          fadesOnlyNote: fadesOnly ? year.fades_only_note : null,
        };

  return {
    verdict,
    title: v.title,
    body: v.body,
    reasons: [...strong, ...moderate],
    fixTip: verdict === "fix_first" && first ? (tips[first.id] ?? null) : null,
    wellbeingNote: wellbeing ? content.wellbeing_note : null,
    payUnsureNote: payUnsure ? content.pay_unsure_note : null,
    applicationsPerWeek: hours === null ? null : Math.max(1, Math.floor(hours / perApp)),
    inAYear,
  };
}
