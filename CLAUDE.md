# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a **zero-build-tool static web app** — a single `index.html` (~82 KB) that is both the source and the deployable artifact. There is no npm, no bundler, no transpilation. Changes to `index.html` go live on GitHub Pages within ~60 seconds of a `git push` to `main`.

A companion Python script `update.py` syncs data from Notion into `index.html` and pushes the result automatically.

### Data flow

```
Notion databases → update.py → hardcoded JS objects in index.html → GitHub Pages
```

- `update.py` queries five Notion databases via REST API, then uses regex substitution to overwrite `const ROCKS`, `const ISSUES`, `const FLOTA_SUMMARY`, and `const SYNC_DATE` declarations directly inside `index.html`.
- Scorecard weekly entries are the only data persisted client-side via `localStorage`.

### index.html structure

| Line range | Content |
|---|---|
| 7–849 | CSS (custom properties, grid layout, semaphore colors) |
| 851–1109 | HTML (header, tabs, two-hemisphere cards, EOS dashboard, modals) |
| 1110–2079 | JavaScript (DATA object, EOS data, render functions, event handlers) |

Key JS sections inside the `<script>` block:
- `DATA` — hardcoded hemisphere cards with weighted scoring (`WEIGHTS` sub-object drives `calcHemPct()`)
- `ROCKS`, `ISSUES`, `FLOTA_SUMMARY`, `SYNC_DATE` — injected by `update.py`; do not manually edit these constants
- `getScorecardData()` / `saveScorecardCell()` — localStorage persistence layer
- `semColor()` — maps string status values to CSS color tokens

### Color/status conventions

| CSS var | Hex | Meaning |
|---|---|---|
| `--rojo` | `#dc2626` | Off-track / bad |
| `--amarillo` | `#d97706` | At risk |
| `--verde` | `#16a34a` | On track / good |
| `--azul` | `#2563eb` | Informational |
| `--morado` | `#7c3aed` | Accent |

Status strings used in data: `on-track`, `at-risk`, `off-track`, `done`, `pending`, `open`, `resuelto`.

## Running the sync

Requires `NOTION_TOKEN` in the environment:

```bash
export NOTION_TOKEN=secret_...
python update.py
```

This fetches Notion data, rewrites the four injected constants in `index.html`, commits, and pushes to `main`. The deployed dashboard at `https://jesusth08-create.github.io/jesus-command-center/` updates ~60 seconds later.

## Notion database IDs (hardcoded in update.py)

| Variable | Database |
|---|---|
| `DB_ROCKS` | Q-cycle rocks tracker |
| `DB_ISSUES` | Issues / IDS list |
| `DB_FLOTA` | Fleet (trucks + trailers) |
| `DB_OOS` | Out-of-service units |
| `DB_SCORECARD` | Weekly scorecard metrics |

## EOS framework context

The UI implements the **Entrepreneurial Operating System (EOS)** for a trucking operation (Kappa). Spanish is the primary language throughout. Key concepts reflected in the data model:

- **Rocks** — quarterly priorities with owner, deadline, and status
- **Scorecard** — 8 weekly KPIs (revenue, millas, CPM, AR, OOS, cargas, cash, brokers) with 13-week rolling display
- **Issues** — IDS (Identify, Discuss, Solve) list with priority levels: `alta`, `media`, `baja`
- **V/TO** — Vision/Traction Organizer: core values, purpose, 10-year target, marketing strategy
- Two hemispheres: **Negocio** (5 business cards) and **Personal** (4 personal cards), each with weighted percentage scoring
