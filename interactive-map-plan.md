# Plan for Claude Code: Interactive Lot Map (one per project)

## Goal

Add an interactive map to each project of the "terrenos" platform so visitors can
visually browse available land. The map replicates the original layout of the
project (blocks, lots, streets) as a vector drawing. Clicking a lot highlights it
and shows its details (measurements, price, status). Sold lots are blocked.

Geometry is drawn manually by the project owner as an SVG, one per project.
Everything else (lot data, status) comes from the Django database. **No AI/photo
analysis in this iteration.**

## Ground rules (read first)

1. **Read the project before proposing anything.** Do not assume any model, field,
   view, template, or setting I mention below exists. Everything here is a
   *concept* to be mapped onto what is actually in the code.
2. **Stop at each checkpoint** marked `CHECKPOINT` and report to me before
   continuing. Do not skip ahead.
3. **If a needed field or model does not exist, do not create it silently.** List
   it, propose the field name/type, and ask me whether to create it.
4. **Never modify the meaning of existing fields or data.** Migrations must be
   additive and safe for existing rows. Show me the migration before applying it.
5. **Do not touch or restyle other parts of the app.** Scope is the map, its admin
   support, its data endpoint, and its integration into the public pages.
6. **Reuse the landing page's design system** (colors, typography, spacing tokens
   from the ui-ux-pro-max output already applied to the landing). Do not invent a
   second look.
7. **Ask before adding any third-party dependency** (e.g., a pan/zoom library).
   Prefer vanilla JS if it is reasonable.
8. **Public safety:** the public endpoint and page must never expose internal data
   (buyer/owner info, costs, notes, anything not needed to display the map).

## Concepts the feature needs

Map each of these to the existing code in Phase 0:

- **Project** (the development the map belongs to)
- **Block/group** of lots (a "fracción", "manzana", or similar), if any
- **Lot**, with: number/identifier, area (m²), dimensions (e.g., width × depth),
  price, currency (if any), and **status** (at least available vs. sold;
  ideally also reserved)
- **Shape ID**: a stable string linking a lot to its shape in the SVG
  (e.g., `fr8-l3`)
- **Optional label position** per lot (for irregular shapes where the center
  looks wrong)
- **Project SVG file**: the drawn map, one per project

## Phase 0: Discovery (read-only, no changes)

Inspect and document:

- The Lot model and any related models (project, block, status choices, price,
  area, dimensions, currency). Note exact names, types, nullability, and
  choices/enums, including how "sold" is currently represented.
- How lots are currently created and edited (Django admin config, forms, views,
  DataTables screens).
- URL structure and views for projects, and whether a public project detail page
  exists or is only a dummy link from the landing page.
- The landing page: template structure, static files, CSS approach, the i18n
  mechanism (EN/PT/ES) and the "Find your land" section with its filters.
- File upload/media configuration (MEDIA settings, storage) since SVGs will be
  uploaded.
- Existing tests, and how they're run.

Output a **mapping table** with three columns: *Concept needed* | *Existing
field/model (exact name)* | *Status: exists / missing / ambiguous*.

> **CHECKPOINT 0:** Show me the mapping table and any surprises. Wait for my
> answers before Phase 1.

## Phase 1: Data model changes (only what I approve)

For every concept marked missing or ambiguous in the table:

- Propose the exact field (name, type, null/blank, default, help text).
- Ask me whether to create it, or whether an existing field should be reused.

Expected candidates (confirm against Phase 0, do not assume):

- Shape ID on Lot, unique within a project
- Optional label position (x, y) on Lot
- A reserved status, if only available/sold exist today
- SVG file on Project
- Currency, if prices have no currency

Additive migrations only, with safe defaults for existing lots. Existing lots
without a shape ID must keep working everywhere else in the app.

> **CHECKPOINT 1:** Show the proposed model changes and migrations. Apply only
> after I approve.

## Phase 2: SVG upload, validation, and admin support

- Let the admin upload an SVG per project.
- **Sanitize on upload**: strip scripts, event-handler attributes,
  `foreignObject`, external references, and anything else that could execute or
  load remote content. SVGs are user-uploaded content shown to the public.
- **SVG conventions** (document them in a short README in the repo so I can follow
  them when drawing):
  - Lot shapes carry an `id` equal to the lot's shape ID.
  - Streets, block labels, north arrow, and outline live in a separate
    non-interactive group.
  - Any tracing background image is not required and is stripped or ignored
    on publish.
- **Consistency report** shown in the admin after upload (and viewable later):
  shape IDs in the SVG with no matching lot, and lots with no shape in the SVG.
  Warn, do not block saving.

## Phase 3: Public data endpoint

- A read-only JSON endpoint per project returning only what the map needs: shape
  ID, lot number, block, area, dimensions, price, currency, status, optional label
  position.
- Respect existing visibility rules (e.g., unpublished or archived projects must
  not be exposed).
- Sensible caching, and the response should reflect status changes made in the
  admin without code changes.

## Phase 4: Frontend map component

Inline the project SVG and paint each lot by status using the landing's design
tokens. Behavior:

- **States:** available, reserved (if it exists), sold. Sold lots use a hatch
  pattern plus a text label ("Vendido"), never color alone, and are not
  selectable (or only show their sold status).
- **Hover/focus** highlights a lot; **click/tap** selects it, raises it visually
  above neighbors, and opens the detail panel: desktop side panel, mobile bottom
  sheet. Detail shows lot number, block, area, dimensions, price, status.
- **Pan and zoom** (wheel and drag on desktop, pinch on mobile), a reset button,
  and zoom-to-lot on selection for small screens.
- **Keyboard accessibility:** lots are focusable, Enter/Space selects, Escape
  closes the panel, visible focus states.
- **Legend** for the three states, and a small note that the map is a
  "plano referencial" (the official plan is the legal reference).
- **Label placement:** lot numbers at the optional stored position, else the
  shape's center.
- **Filters:** integrate with the "Find your land" filters so that lots not
  matching dim on the map, and offer a list-view alternative.
- **i18n:** all UI text in EN/PT/ES using the project's existing mechanism.
  Prices and areas formatted per language.
- **Reduced motion** respected; no animation that blocks interaction.
- Responsive at 375, 768, 1024, and 1440 px. The plan can be tall and narrow, so
  verify it is usable on phones.

> **CHECKPOINT 2:** Before building the CTA, ask me:
> - What should "Consultar este lote" do: scroll to the contact form with the lot
>   prefilled, open WhatsApp with a prewritten message (and what number), or both?
> - Which currency to display, and should reserved lots be selectable?

## Phase 5: Integration

- Place the map on the project's detail page. If it's only a dummy link today,
  ask me whether to create a minimal real detail page for the map or embed the map
  in the landing page's projects section.
- If a project has no SVG yet, show a graceful fallback (e.g., the lot list only),
  not a broken page.
- Decide with me how multiple projects are navigated (separate pages vs. a
  switcher on the map section).

## Phase 6: Verification

- Create sample data and a **sample SVG** for a simple regular project so the
  whole flow can be demonstrated end to end. Clearly mark it as sample data and
  tell me how to remove it.
- Tests for: SVG sanitization, the consistency report, the endpoint (including
  that it excludes private data and hides non-public projects), and
  status-to-display mapping.
- Run the existing test suite and confirm nothing else broke.
- Manual checklist: responsive sizes, keyboard-only use, reduced motion,
  contrast, all three languages, a project with a missing SVG, and a lot with no
  shape.

## Out of scope for this iteration

- Any LLM or photo-analysis feature
- A polygon-drawing editor in the admin
- Restyling the rest of the application
- Real payment, reservation, or checkout flows

## What to report back when done

1. Summary of what was added or changed (models, migrations, admin, endpoint,
   templates, static files).
2. The SVG drawing conventions README, and instructions for uploading a new
   project's SVG.
3. Anything you decided differently from this plan, and why.
4. Open questions or follow-ups.
