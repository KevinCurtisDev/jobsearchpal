# extension/ (Track E: not started)

The Hearback Chrome extension: free for life, local only, no AI, no backend, no account.

**Status:** waiting for owner approval of `docs/16-chrome-extension.md` and decisions #22, #23, #24, #27.
No code is written here yet. Phase E0 (decisions and spikes) comes first.

Planned layout (see `docs/16` §6): background worker, content scripts (Tier A sites only),
side panel, popup, options dashboard, offscreen documents, `editions/` (local, connect, ai).

Rules: `CLAUDE.md` rules E1 to E10. The local edition makes no network requests (CI network audit).
