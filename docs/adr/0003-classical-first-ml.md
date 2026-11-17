# ADR 0003 · Classical methods first, generative AI last

**Status:** Accepted · 2026-10-20

## Context
Competitors rely heavily on generative AI, producing generic CVs and unexplained scores.
Users distrust match scores they can't understand. AI calls cost money and send personal
data to third parties.

## Decision
Each feature uses the simplest method that works: rules → statistics and IR → classical ML →
generative AI (writing, messy text, interview answer judgement only). Every score is
explained, calibrated, causal where advice is given, and labelled with confidence and source.
Learned models switch on behind feature flags only when their data-maturity gate is met.

## Consequences
- Lower running costs, explainable output, less personal data shared.
- Requires disciplined event logging from day one (the action log).
- Some features start simpler (rules v0) and improve as data accumulates.
