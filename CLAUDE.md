# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Django app for managing a land-subdivision ("terrenos") business in Bragado, Argentina: land plots grouped
into projects, their sales and installment payments, and the investments/expenses that make up each
project's cost. UI language is Spanish (`LANGUAGE_CODE = "es-ar"`); model/field names are English, while
`verbose_name`, form labels and template text are Spanish. Amounts are dual-currency (ARS/USD) and carry an
exchange rate.

## Layout gotcha

The Django project root is `terrenos/` (contains `manage.py`), and the settings package is `terrenos/terrenos/`.
**The virtualenv also lives at `terrenos/terrenos/`** (`bin/`, `lib/`, `pyvenv.cfg` sit next to `settings.py`).
Do not confuse venv files with project files, and exclude `terrenos/terrenos/lib/` from searches.

```bash
source terrenos/terrenos/bin/activate
python terrenos/manage.py runserver
```

## Commands

```bash
python terrenos/manage.py runserver          # dev server (login at /users/accounts/login/)
python terrenos/manage.py makemigrations
python terrenos/manage.py migrate
python terrenos/manage.py createsuperuser
python terrenos/manage.py collectstatic      # WhiteNoise serves from terrenos/staticfiles/
```

Tests: `pytest.ini` sits at the repo root but points at `testpaths = tests/`, which does not exist, and
enforces `--cov-fail-under=80` against `expense_type_details` only. Every app's `tests.py` is an empty stub.
A bare `pytest` therefore collects nothing and fails the coverage gate — run Django's own runner instead
(`python terrenos/manage.py test <app>`), or fix `pytest.ini` before adding pytest tests. `pytest.ini`'s
`DJANGO_SETTINGS_MODULE = terrenos.settings` only resolves with `terrenos/` on the path.

## Architecture

**One Django app per entity**, all in `terrenos/`, all registered in `CUSTOM_APPS` (`terrenos/terrenos/settings.py`)
and mounted at `/<app_name>/` in `terrenos/terrenos/urls.py`. Every app repeats the same shape —
`models.py`, `forms.py` (a `ModelForm` with Spanish `labels` and explicit Bootstrap `widgets`), `views.py`,
`urls.py` (with `app_name` set, so reverse as `app:index`, `app:detail`, …), and
`templates/<app>/{index,detail,create,edit,delete}.html`.

Views mix two styles deliberately: a `CreateView`/`DeleteView` class for creation, plus `@login_required`
function views for index/detail/edit/delete. Every function view is `@login_required`; there is no other
authorization layer. Several apps also carry a vestigial `create()` function view that just returns an
`HttpResponse` — the routed create is the CBV.

Domain graph:

- `Project` ← `Land` (`manual_id` + `block` identify a plot; `area` and `is_sold` are properties)
- `Land` ← `Sale` ← `SaleSummary` (individual payments: initial, cuota, saldo)
- `Project` ← `Investment` and `Project` ← `Expense` — near-identical models (`Expense` adds a `receipt`
  file upload), both categorized by `ExpenseType` (concepto) + `ExpenseTypeDetail` (detalle)
- Lookup tables: `Seller`, `Payer`, `PaymentReceiver`, `People`, `PeopleToLands`

**Exchange rates are fetched in `Model.save()`** when `exchange_rate` is blank — `Investment` hits
dolarapi blue, `Expense` hits dolarapi oficial, `SaleSummary` hits exchangerate-api. This means saving
performs a network call and silently falls back to `0.0`/`1.0` on failure; tests and bulk operations should
set `exchange_rate` explicitly.

**`projects.views.detail` is the analytical core.** It loops over every `ExpenseType`, aggregates that
type's `Investment`s with `Case`/`When` to produce ARS and USD totals (converting via `exchange_rate` in
both directions), an "accountable" total (uses `accountant_amount`/`accountant_currency` when present, else
falls back to `amount`/`currency`), an average exchange rate, per-land costs, and each type's percentage of
the project total. Results are keyed by `ExpenseType.key`, and `projects/detail.html` iterates the dict
generically — **adding a new expense type creates its table automatically; do not hardcode types in templates.**
`ExpenseType.key` / `ExpenseTypeDetail.key` are unique slugs that exist for exactly this lookup.

**`lands.views.create_multiple`** is the one hand-rolled form handler: it parses `lands[i][field]` POST keys
from `lands/create_multiple.html`, rejects duplicate `(manual_id, block, length, width)` combinations both
within the batch and against existing rows for the project, then `bulk_create`s. Note that `bulk_create`
skips `save()`, so no per-row side effects run.

Templates extend `templates/base.html` (Bootstrap 5 via `django_bootstrap5`, plus jQuery DataTables from CDN
for sortable index tables). Auth templates live in `users/templates/registration/`; `users/urls.py` includes
`django.contrib.auth.urls` under `/users/accounts/`.

## Settings and deployment

- Postgres credentials are currently **hardcoded in `settings.py`**; a commented-out Neon `DATABASE_URL`
  block sits below them for cloud migrations. `DJANGO_SECRET_KEY` and `DJANGO_TERRENOS_DEBUG` come from
  `.env` via `python-dotenv`. Note `DEBUG` is read as a raw string, so any non-empty value is truthy.
- `django_heroku.settings(locals())` runs last and overrides database/static settings when Heroku env vars
  are present. `Procfile` and `runtime.txt` (Python 3.11.5) target Heroku; `wsgi.py` exports `app` for Vercel.
- `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` are pinned to the Heroku host and localhost.

## Working notes

- Migrations in `expense_types/` and `expense_type_details/` (`0002_*_key`, `0003_alter_*_key`) currently have
  their `operations` commented out to work around a Neon migration error — check `git diff` before touching
  those apps' schema, and expect `makemigrations` to want to re-add the `key` field.
- Commit messages in this repo are written in Spanish.
- Comments in this codebase use `##` rather than `#`; commented-out code is left in place as history.
