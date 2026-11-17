# packages/ (Track E: not started)

Shared TypeScript used by the extension and the web app.

| Package | Contents |
| --- | --- |
| `core` | Pure rules and scoring, parsers, schemas, no-invention guard. No browser APIs (lint-enforced) |
| `data` | Versioned data packs built from `/content` |
| `storage` | Storage interface, IndexedDB implementation, later a remote adapter |
| `adapters` | Job-site adapters with saved HTML fixtures |
| `ui` | Design-system components and tokens shared with `frontend/` |

Design: `docs/16-chrome-extension.md` §6. Golden fixtures shared with the Python backend live in `content/fixtures/`.
