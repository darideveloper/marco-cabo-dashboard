<!-- context7 -->
Always use the Context7 MCP server when I need library/API documentation, code generation, setup or configuration steps without me having to explicitly ask. Use the `resolve-library-id` and `query-docs` MCP tools to fetch current documentation.
<!-- context7 -->

<!-- ponytail -->
Always load the ponytail skill at session start (call skill({ name: "ponytail" })). Enforce minimal/YAGNI solutions by default. Use full intensity unless /ponytail lite or /ponytail ultra is specified.
<!-- ponytail -->

# Mar Co. Cabo Dashboard — Agent Guide

> Private transfer booking backend for Los Cabos. Django 4.2 + DRF API + Jazzmin admin. No public frontend in this repo — landing lives at `LANDING_HOST` (e.g. `https://marco-cabo.com/booking`).

## 1. Tech Stack

| Layer | Choice | Where |
|-------|--------|-------|
| Runtime | `python:3.12-slim`, `Django==4.2.7`, `gunicorn` | `Dockerfile:8`, `requirements.txt:2` |
| API | `djangorestframework==3.15.2`, `django-filter==24.3`, `TokenAuthentication` + `SessionAuthentication` | `project/settings.py:359-368` |
| DB | `psycopg`/`psycopg2-binary` Postgres (`DB_ENGINE=django.db.backends.postgresql_psycopg2`), `sqlite3` when `python manage.py test` | `project/settings.py:100-128`, `.env.dev/.prod/.testing` |
| Admin | `django-jazzmin==3.0.1`, `whitenoise==6.2.0`, SASS -> `core/static/core/css/custom.css` | `project/settings.py:169-305` |
| Storage | Local `staticfiles`/`media` vs S3 `django-storages`+`boto3` toggled by `STORAGE_AWS` | `project/settings.py:316-350`, `project/storage_backends.py:1-19` |
| Integrations | Stripe proxy `STRIPE_API_HOST` via `requests` (`utils/stripe.py:6`), `openpyxl` Excel export, `selenium==4.20.0` | `utils/stripe.py:1-46`, `travels/admin.py:106-192` |
| Env | `python-dotenv` loads `.env` then `.env.{ENV}` (`ENV=prod/dev/testing`) | `project/settings.py:11-15`, `.env:1` |
| I18n | `LANGUAGE_CODE='es-mx'`, `TIME_ZONE='America/Mexico_City'` | `project/settings.py:154-156` |

No `pyproject.toml`, no `docker-compose.yml`, no `Makefile`. Single `requirements.txt:1-29`.

## 2. Project Structure

```
manage.py
project/                 # Django project (settings/urls/wsgi/asgi/storage_backends)
  settings.py:1-370      # env loading, INSTALLED_APPS, JAZZMIN, DRF, storage
  urls.py:1-41           # DefaultRouter + api/sales + api/sales/done
core/                    # app: pagination, static (SASS/JS/imgs), management commands
  pagination.py:1-7      # CustomPageNumberPagination (page-size, max 1000)
  management/commands/apps_loaddata.py:1-29
  management/commands/load_pricing.py:1-114  # parses pricing.csv -> Pricing rows
  static/core/css/_base.sass, _admin.sass, custom.sass -> custom.css
  static/core/js/custom.js:1-68  # AdminSetup image rendering
  tests_base/test_models.py:1-265, test_views.py:1-170, test_admin.py:1-107
travels/                 # main domain app
  models.py:1-257        # 9 models (see §4)
  serializers.py:1-144   # SaleSerializer (atomic), SaleDoneSerializer, PricingSerializer
  views.py:1-245         # 5 ReadOnly ViewSets + SaleViewSet(APIView) + SaleDoneView
  admin.py:1-248         # SaleAdmin.export_to_excel, TransferAdmin, etc.
  fixtures/travels/*.json # Zone, Location, Vehicle, ServiceType
  migrations/0001_...0039_sale_vip_code.py
  tests/test_models.py, test_views.py:1-1154, test_admin.py:1-433
utils/
  stripe.py:1-46         # get_payment_link() -> POST STRIPE_API_HOST
  handlers.py:1-22       # custom_exception_handler
  export-template.xlsx   # admin export template (row 5 headers, data from row 6)
v2-flowchart.mermaid:1-94 # canonical booking flow
openspec/
  config.yaml            # spec-driven, see §7
  changes/<name>/        # proposal.md, design.md, tasks.md, specs/*/
  specs/                 # (empty, specs live inside changes per spec-driven)
json_data/               # ignored examples: SaleViewSet.json, StripeApi.json
```

Templates: none (`TEMPLATES DIRS=[]`, `APP_DIRS=True` but no `*.html` — API + admin only).

## 3. Environment & Running

```bash
# env selection: .env contains ENV=prod/dev/testing -> loads .env.{ENV}
cat .env            # ENV=prod
cat .env.dev        # DEBUG=True, HOST=http://127.0.1:8000, STORAGE_AWS=False, DB localhost
cat .env.prod       # DEBUG=True (fix before prod!), STORAGE_AWS=True, DB 5.78.126.131:9020

python manage.py migrate
python manage.py apps_loaddata        # loads Zone/Location/Vehicle/ServiceType fixtures
python manage.py load_pricing         # deletes & recreates ~1956 Pricing rows from pricing.csv
python manage.py runserver
python manage.py test                 # uses sqlite testing.sqlite3 (project/settings.py:100-108)
python manage.py test travels.tests.test_views.SaleViewSetTestCase -v 2

# Docker (all args baked as ARG->ENV, see Dockerfile:13-63)
docker build -t marco-cabo --build-arg SECRET_KEY=... --build-arg DB_HOST=... .
docker run -p 80:80 marco-cabo  # gunicorn --bind 0.0.0.0:80 project.wsgi:application
```

Gotchas:
- `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` split by `","` — missing env crashes (`project/settings.py:38`).
- `PAGE_SIZE` env overrides pagination (`core/pagination.py:5 page_size=12` vs settings `PAGE_SIZE`).
- `IS_TESTING = sys.argv[1]=="test"` switches DB and `collect_billing_address=False` in `utils/stripe.py:38`.
- `Dockerfile:83-86` runs `collectstatic/makemigrations/migrate/apps_loaddata/load_pricing` at **build time** (should be runtime). `86` has lowercase `run` typo.

## 4. Domain & Booking Flow

Canonical flow `v2-flowchart.mermaid:1-94`:

```
POST /api/sales/ (service_type, client_name/email, location, vehicle, vip_code?)
  -> SaleSerializer.validate (trim vip_code, value__iexact + active=True -> 401 if bad, atomic)
  -> create Client (phone=None), Pricing.get(location,vehicle,service_type), Sale(paid=False, stripe_code=uuid4, total)
  -> get_payment_link(product_name="Mar Co. Cabo Transportation", total, description=get_summary(), email, sale_id=stripe_code)
     -> POST STRIPE_API_HOST {user, url, url_success=LANDING_HOST/confirmation/{sale_id}, products, email, collect_phone/billing_address}
  -> 201 {payment_link}

Stripe redirect ONLY on success -> LANDING_HOST/confirmation/{stripe_code}

GET /api/sales/?stripe_code=UUID -> {id, service_type, location, vehicle, total, stripe_code, vip_code, client}

POST /api/sales/done/ (sale_stripe_code, client_phone, passengers, arrival_* , departure_* if Round Trip)
  -> SaleDoneSerializer -> find Sale, if paid -> 400, else update client.phone/sale.passengers/details, paid=True, create Transfer arrival (+ departure)
  -> 200 Sale confirmed; admin export_to_excel -> XLSX
```

Security: `stripe_code` UUID `travels/models.py:162-167`, `paid` guard blocks double-submit, Stripe failure = no redirect.

## 5. Data Model (`travels/models.py:1-257`)

| Model | Key fields | Notes |
|-------|------------|-------|
| `Zone:6` | `name unique` | `locations` property = `Location.objects.filter(zone=self)` (N+1 risk) |
| `Location:29` | `name unique, zone FK CASCADE` | `unique_together (name,zone)`, hotels + postal codes (zone "Codigo Postal") |
| `Client:49` | `name, last_name?, email, phone?` | `__str__` `email - phone` (phone may be None) |
| `VipCode:80` | `value(10) unique, active` | tracking only, no discount |
| `Vehicle:99` | `name unique, passengers Int` | Luxury SUV 4, Executive Van 8, Sprinter 10 |
| `ServiceType:118` | `name unique` | One Way / Round Trip |
| `Sale:136` | `client/vehicle/service_type/location FK, passengers?, details?, stripe_code UUID unique, total Float, paid Bool, vip_code FK PROTECT null/blank` | `get_summary():182` for Stripe |
| `Transfer:198` | `date, hour, type departure/arrival (default "Departure" - casing bug!), sale FK, airline, flight_number` | |
| `Pricing:233` | `location/vehicle/service_type FK, price Float` | no unique_together, should be Decimal |

Migrations: 39 files, `0037_remove_sale_vip_code`, `0038_vehicle_passengers`, `0039_sale_vip_code` (PROTECT).

## 6. API Contract (`project/urls.py:13-38`, `travels/views.py:13-245`)

All DRF endpoints default `IsAuthenticated` (`project/settings.py:360-362`, `Token`+`Session`). No `AllowAny` — public booking requires auth token (current bug if landing lacks one).

| Endpoint | View | Auth | Notes |
|----------|------|------|-------|
| `GET /api/hotels/` | `HotelsViewSet:13` `Zone.exclude(name="Codigo Postal")` | yes | `ZoneSerializer` with nested `LocationSerializer` |
| `GET /api/postal-codes/` | `PostalCodeViewSet:18` `Location.filter(zone__name="Codigo Postal")` | yes | **bug**: uses `ZoneSerializer` for `Location` queryset |
| `GET /api/vehicles/` | `VehicleViewSet:23` | yes | |
| `GET /api/service-types/` | `ServiceTypeViewSet:28` | yes | |
| `GET /api/pricing/?location=&vehicle=&service_type=` | `PricingViewSet:33` `DjangoFilterBackend` | yes | |
| `GET /api/sales/?stripe_code=UUID` | `SaleViewSet.get:68` | yes | 401 if not found |
| `POST /api/sales/` | `SaleViewSet.post:116` | yes | 201+payment_link, 401 for bad `vip_code`, 400 otherwise, always atomic |
| `POST /api/sales/done/` | `SaleDoneView:160` | yes | nested `client.phone` mapping |

Pagination `core/pagination.py:4-7`, errors via `utils/handlers.py:4-22` -> `{status:"error", message, data}`.

Admin: `travels/admin.py:61` `SaleAdmin` `export_to_excel:106`, `custom_links` to transfers.

## 7. Conventions

- **Commits:** Conventional Commits `feat/fix/chore (<scope>):` (`git log --oneline -20`), single author `daridev`.
- **Branches:** `main` (default), `abel/dari/testing` (origin HEAD -> abel). Keep changes on feature branches, merge to `main`.
- **Lang:** code English, admin `verbose_name` Spanish, `LANGUAGE_CODE='es-mx'`.
- **Style:** No lint/format enforced. Keep diffs minimal (ponytail). Add type hints on new utils (`utils/stripe.py:6` style). File paths in messages as `path:line`.
- **Pricing:** `core/management/commands/pricing.csv` has 6 columns per location (Luxury/Executive/Sprinter × OneWay/RoundTrip), `load_pricing.py:36` skips 2 header rows, `clean_price` strips `$` `,`.

## 8. Testing

```bash
python manage.py test -v 2                        # all (sqlite)
python manage.py test travels.tests.test_views -v 2
python manage.py test travels.tests.test_admin -v 2
# selenium: TEST_HEADLESS=True (project/settings.py:22), Chrome headless=new
```

Helpers: `core/tests_base/test_models.py:1-265` (`create_zone/location/service_type/vehicle/vip_code/pricing/client/sale/transfer`), `core/tests_base/test_views.py:1-170` (`TestApiViewsMethods`, `TestSeleniumBase`), `core/tests_base/test_admin.py:1-107` (`TestAdminBase`). Fixtures `travels/fixtures/travels/*.json` loaded via `apps_loaddata`. No `pytest/coverage/factory_boy` — use std `TestCase/APITestCase/LiveServerTestCase`. Current `temp.sale.tests.todo:76` shows 93 tests, 4 errors from stale `vip_code` wiring — see active change.

## 9. OpenSpec Integration

This repo is **spec-driven** (`openspec/config.yaml:1` `schema: spec-driven`). All non-trivial work goes through a change.

### 9.1 Where things live

- `openspec/config.yaml` — project context + per-artifact rules (injected into `openspec instructions ... --json` as `context`/`rules`).
- `openspec/changes/<kebab-name>/` — `proposal.md` (what/why), `design.md` (how), `tasks.md` (steps), `specs/<capability>/spec.md` (requirements). Active example: `vip-code-sale-tracking` (proposal/design/tasks + 3 specs), `bruno-api-collection`.
- `openspec/specs/` — empty (specs live inside changes for this schema).
- Archive: `openspec/changes/archive/` (excluded from `.gitignore:22` `!openspec/changes/archive/`). Active `openspec/changes/*` is gitignored (` .gitignore:19`) — local-first until archived.

### 9.2 Workflow (use these, not ad-hoc edits)

1. **Explore** (optional): `/opsx-explore` or `skill({name:"openspec-explore"})` — clarify requirements before proposing.
2. **Propose**: `/opsx-propose <kebab-name or description>` or `skill({name:"openspec-propose"})`
   ```bash
   openspec new change "<name>"
   openspec status --change "<name>" --json   # check applyRequires/artifacts/planningHome
   openspec instructions <artifact-id> --change "<name>" --json  # template + context/rules
   ```
   Create artifacts in dependency order until `applyRequires` all `done`.
3. **Apply**: `/opsx-apply [change]` or `skill({name:"openspec-apply-change"})`
   ```bash
   openspec status --change "<name>" --json
   openspec instructions apply --change "<name>" --json  # -> contextFiles, task list, state
   # read every file in contextFiles, implement tasks one by one, toggle - [ ] -> - [x] in tasks.md
   ```
4. **Verify**: `/opsx-verify [change]` or `skill({name:"openspec-verify-change"})` — checks implementation vs specs.
5. **Archive**: `/opsx-archive [change]` or `skill({name:"openspec-archive-change"})` (`/opsx-bulk-archive` for many) — moves change to `openspec/changes/archive/` and git-tracks it.

### 9.3 Rules for agents

- **Never** edit `openspec/config.yaml` `context`/`rules` into artifact files — they are constraints only.
- **Always** use `resolvedOutputPath` from `openspec instructions` JSON, not assumed paths.
- **Always** read dependency artifacts before writing the next one.
- **Keep `tasks.md` checkboxes in sync** — flip immediately after each task.
- **Respect `actionContext.allowedEditRoots`** — if empty in workspace-planning mode, stop before editing.
- **One change at a time** unless bulk archiving. Name changes in kebab-case.
- **Reference specs in code**: e.g. `travels/serializers.py:62` validation must match `specs/vip-code-tracking/spec.md` scenarios (trim+iexact+active, 401 shape).
- After `apply` completes, suggest `archive`. After `archive`, the change becomes tracked (no longer gitignored).

### 9.4 Current context (also in `openspec/config.yaml`)

Tech stack, domain, and booking flow above are the project context injected into every `openspec instructions` call. Keep `openspec/config.yaml` in sync if stack/domain changes.

## 10. Gotchas & Do/Don't

- **DO** use `transaction.atomic` for `Client`+`Sale` creation (`travels/serializers.py:105` pattern).
- **DO** validate `vip_code` via `value__iexact` + `strip()` + `active=True`, return `401 {status:"error", message:"Invalid VIP code", errors:{vip_code:[...]}}` and create zero rows.
- **DON'T** resurrect `POST /api/validate-vip-code/` — deleted on purpose (see `vip-code-sale-tracking/design.md:39`).
- **DON'T** bypass Stripe for VIP — always call `get_payment_link` (`travels/views.py:123` commented bypass stays removed).
- **DON'T** add `pricing` logic for VIP — tracking only.
- **DON'T** forget `allowedEditRoots` check in apply.
- Fix `Transfer.type` default casing, `PostalCodeViewSet` serializer, missing `Pricing.get` 404, `SaleDoneView` NPE on `None` sale, `ADMIN` N+1, `Float` -> `Decimal`, `DEBUG` in prod, `requests` timeout before calling it done.

## 11. Useful References

- Booking flow: `v2-flowchart.mermaid:1-94`
- Settings: `project/settings.py:1-370`
- Models: `travels/models.py:1-257`
- Views: `travels/views.py:1-245`
- Serializers: `travels/serializers.py:1-144`
- Admin: `travels/admin.py:1-248`
- Stripe: `utils/stripe.py:1-46`
- Active change example: `openspec/changes/vip-code-sale-tracking/proposal.md:1-29`
