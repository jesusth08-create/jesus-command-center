# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Dashboard de vida — vista de halcón. Foto rápida del estado de cada área de la vida de Jesús Torres (negocio y personal). Objetivo: claridad visual instantánea de qué mueve y qué está estancado. No reemplaza el Plan 90 Días ni el Second Brain en Notion; es la capa visual que los conecta.

Publicado en GitHub Pages: `https://jesusth08-create.github.io/jesus-command-center/`

---

## Architecture

This is a **zero-build-tool static web app** — a single `index.html` (~82 KB) that is both the source and the deployable artifact. There is no npm, no bundler, no transpilation. Changes to `index.html` go live on GitHub Pages within ~60 seconds of a `git push` to `main`.

A companion Python script `update.py` syncs data from Notion into `index.html` and pushes the result automatically.

### Data flow

```
Notion databases → update.py → hardcoded JS objects in index.html → GitHub Pages
```

`update.py` queries five Notion databases via REST API, then uses regex substitution to overwrite `const ROCKS`, `const ISSUES`, `const FLOTA_SUMMARY`, and `const SYNC_DATE` directly inside `index.html`. Scorecard weekly entries are the only data persisted client-side via `localStorage`.

### index.html structure

| Line range | Content |
|---|---|
| 7–849 | CSS (custom properties, grid layout, semaphore colors) |
| 851–1109 | HTML (header, tabs, two-hemisphere cards, EOS dashboard, modals) |
| 1110–2079 | JavaScript (DATA object, EOS data, render functions, event handlers) |

Key JS sections inside the `<script>` block:
- `DATA` — hardcoded hemisphere cards with weighted scoring (`WEIGHTS` sub-object drives `calcHemPct()`)
- `ROCKS`, `ISSUES`, `FLOTA_SUMMARY`, `SYNC_DATE` — injected by `update.py`; **do not manually edit these constants**
- `getScorecardData()` / `saveScorecardCell()` — localStorage persistence layer
- `semColor()` — maps string status values to CSS color tokens

---

## The 10 Areas

### HEMISFERIO NEGOCIO (5 áreas)

| # | Área | Tipo | Definición del 100% |
|---|---|---|---|
| 1 | Kappa Operación | Proyecto | 7 trailers en función: 3 trucks con chofer + 3 trailers rentados a OOs + 1 almacenaje |
| 2 | Kappa Finanzas | Hábito mensual | Semáforo de salud (verde = ingreso neto positivo con margen real) |
| 3 | OOs + Trailers activos | Proyecto | 5 OOs bajo autoridad Kappa usando equipo Kappa. Meta mínima verde: 3 OOs |
| 4 | Trucking Academy — Producto | Proyecto | MVP lanzado + 3+ ventas con margen positivo |
| 5 | Marca Personal | Hábito | Contenido y posicionamiento como referente hispano en trucking |

### HEMISFERIO PERSONAL (4 áreas)

| # | Área | Tipo | Definición del 100% |
|---|---|---|---|
| 6 | Finanzas Personales | Hábito mensual | Semáforo (verde = ingresos > gastos, mes a mes mejorando) |
| 7 | Salud Física + Mental | Hábito semanal | 5+ días activos/semana (ejercicio o caminata) |
| 8 | Metas / Legado | Indicador de dirección | Verde = acción concreta esta semana hacia una meta personal |
| 9 | Aprendizaje / Crecimiento | Hábito semanal | 1+ libro o audiolibro por semana |

### Weighted Task Completion (WTC)

Each area's percentage is calculated as:

```javascript
% Área = (Σ peso × completado) / (Σ peso total) × 100
```

Tasks have weights 1–5 by impact. Avoids treating "update Facebook copy" (peso 1) the same as "close large broker" (peso 5). The `WEIGHTS` object inside `DATA` drives `calcHemPct()`.

---

## Color / Status Conventions

### CSS semaphore vars

| CSS var | Hex | Meaning |
|---|---|---|
| `--rojo` | `#dc2626` | Off-track / bad |
| `--amarillo` | `#d97706` | At risk |
| `--verde` | `#16a34a` | On track / good |
| `--azul` | `#2563eb` | Informational |
| `--morado` | `#7c3aed` | Accent |

### Status strings in JS data

`on-track`, `at-risk`, `off-track`, `done`, `pending`, `open`, `resuelto`

### Brand palette (logos, future use)

| Marca | Color | Hex |
|---|---|---|
| Kappa Delivery | Rojo | `#E8281A` |
| The Trucking Academy | Dorado | `#F5C518` |
| Jesús Torres | Navy | `#1B3A6B` |

---

## Notion Databases

### DB_ROCKS — `1809896607c8426e9209f615fa4e11ee`

Rocks trimestrales. `update.py` filters for `Trimestre = "Q2 2026"` (update each quarter).

| Field | Type | Notes |
|---|---|---|
| `Rock` | title | Name of the rock |
| `Trimestre` | select | Q1/Q2/Q3/Q4 2026 |
| `Status` | select | On Track · En Proceso · Off Track · Completo |
| `Owner` | select | Jesús · Claude · Manus |
| `% Avance` | number | 0–100 |
| `Fecha Límite` | date | Deadline |
| `Notas` | text | Progress notes |

**Status mapping (`update.py` → dashboard):** `On Track` → `on-track` · `En Proceso` → `at-risk` · `Off Track` → `off-track` · `Completo` → `done`

### DB_ISSUES — `aa154cb6e36143069cb455114e7ed77b`

IDS list. `update.py` filters `Status ≠ "Resuelto"`, sorted by priority.

| Field | Type | Notes |
|---|---|---|
| `Issue` | title | Description of the issue |
| `Fecha` | date | Date logged |
| `Prioridad` | select | Alta · Media · Baja |
| `Owner` | select | Jesús · Claude · Manus · Sistema |
| `Status` | select | Abierto · En Proceso · Resuelto |
| `Solución` | text | Resolution notes |

### DB_SCORECARD — `52a416dba38044cb91935d1e0ac8db23`

Weekly financial KPIs. Key: `Semana` is the title field formatted as `YYYY-MM-DD`.

| Field | Type | Description |
|---|---|---|
| `Semana` | title | Week start date e.g. `2026-05-26` |
| `Revenue` | number ($) | Total weekly income |
| `Millas` | number | Total miles driven |
| `CPM` | number ($) | Cost per mile (Revenue / Millas) |
| `Cargas` | number | Loads completed |
| `Cash Balance` | number ($) | BofA balance at week close |
| `OOs Activos` | number | Active owner-operators |
| `Amazon Relay` | checkbox | AR loads ran this week |
| `Brokers Nuevos` | number | New brokers contacted or closed |
| `Notas` | text | Free notes |

### DB_FLOTA — `2facdb6122b9408d9938f4261760401f`

Fleet status. Each row = one unit (truck or trailer).

| Field | Type | Values |
|---|---|---|
| `Unidad` | title | e.g. `Truck 02`, `Trailer 27-822` |
| `Tipo` | select | Truck · Trailer |
| `Status` | select | Activo · Rentado · En Taller · Disponible · Inactivo |
| `Chofer / OO` | text | Driver or OO name |
| `Combinación` | text | e.g. `Truck 02 + Trailer 27-822` |
| `Próx Mantenimiento` | date | Next maintenance date |
| `Notas` | text | Free notes |

### DB_OOS — `bb2a81214910492b9adbb525b6978bdc`

Out-of-service units. Used by `update.py` to compute `FLOTA_SUMMARY.oos_count`.

---

## Running the Sync

Requires `NOTION_TOKEN` in the environment:

```bash
export NOTION_TOKEN=secret_...
python update.py
```

Fetches all five Notion databases, rewrites `ROCKS`, `ISSUES`, `FLOTA_SUMMARY`, and `SYNC_DATE` constants in `index.html`, then runs `git commit` + `git push` to `main` with message `sync: Notion → dashboard YYYY-MM-DD`. Dashboard updates on GitHub Pages ~60 seconds later.

---

## EOS Framework Context

The UI implements **EOS (Entrepreneurial Operating System)** for Kappa Delivery LLC. Spanish is the primary language throughout. The weekly operating rhythm is the **War Room = Level 10 Meeting**: Scorecard → Rocks → Issues/IDS.

### V/TO (Vision/Traction Organizer)

- **Core Values:** Lealtad · Trabajo duro · Responsabilidad total · Aprendizaje continuo · Hacer lo correcto
- **Core Focus / Propósito:** Que un hispano que empieza desde abajo pueda construir libertad real en el trucking.
- **Nicho:** Carrier y recurso #1 en español para owner-operators hispanos bajo autoridad sólida.
- **10-Year Target:** Kappa genera cashflow sin que Jesús maneje. ~$5M revenue anual · 15+ OOs · 7 trailers en renta · The Trucking Academy como activo digital independiente.
- **1-Year Plan (mayo 2027):** 4 OOs activos · $15,000/mes cashflow neto · 7 trailers rentados · Jesús fuera del truck.
- **Proven Process:** "El Camino Kappa" — Onboarding → Despacho → Cobro/Factoring → Crecimiento del OO.

### Key EOS concepts in the data model

- **Rocks** — quarterly priorities. Owner + deadline + % avance + status. `update.py` only pulls the current quarter.
- **Scorecard** — 9 weekly KPIs with 13-week rolling display in the UI.
- **Issues** — IDS (Identify, Discuss, Solve). Priority: `alta`, `media`, `baja`.
- **War Room** — weekly Level 10 meeting. Sunday ritual: upload statements, update área scores, review dashboard.

---

## Planned Features (v2)

Approved improvements to implement (from design doc in Notion):

1. **Bloque "Hoy"** — single critical action above the hemispheres, generated by reading full dashboard state.
2. **Modo Domingo** — guided Sunday ritual flow: upload Kappa statement → upload personal statement → update book → mark active days → show comparative summary vs. prior week.
3. **Histórico 12 semanas** — weekly auto-snapshot; chart showing verde/amarillo/rojo trend per area over time.
4. **Alerta de incoherencia** — rule: if Kappa Operación is high but Kappa Finanzas is red for 2+ months, flag it explicitly.
5. **"Última actualización" por tarjeta** — if 14+ days without update, card turns gray with "Datos viejos — ¿sigue siendo verdad?".

Explicitly excluded from v2: push notifications, annual goal comparison, loadboard integrations, sharing with team.
