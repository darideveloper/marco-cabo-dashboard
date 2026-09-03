## Context

This repo has 8 HTTP surfaces (`project/urls.py:13-42`) — 5 `ReadOnlyModelViewSet`s under `DefaultRouter` (`hotels`, `postal-codes`, `vehicles`, `service-types`, `pricing` with `DjangoFilterBackend`) and 2 `APIView`s (`SaleViewSet` `GET /api/sales/?stripe_code=` + `POST /api/sales/` now with optional `vip_code` FK `PROTECT` per `travels/models.py:170`/`serializers.py:50-130`, `SaleDoneView` `POST /api/sales/done/`) — all behind `IsAuthenticated` (`project/settings.py:359`) with `TokenAuthentication`/`SessionAuthentication` and `utils/handlers.py:4` custom envelope. `SaleSerializer.vip_code` is `CharField(10) writeOnly` validated `trim + iexact + active=True` (`serializers.py:70`) mapping to `sale.vip_code` FK and `transaction.atomic()` creation; `SaleViewSet.get` exposes `vip_code: value|null` (`views.py:83`), `post` returns `401 {status:"error",message:"Invalid VIP code",errors:{vip_code:[...]}}` on invalid vs `400` otherwise (`views.py:118-134`). Tests (`travels/tests/test_views.py` +5 vip tests, `core/tests_base/test_models.py:156`) assert paginated `{count,next,previous,results}` and `vip_code` `401` vs `""`/`null`/missing → `None`. No Bruno workspace exists; blueprint at `/home/daridev/Desktop/obsidian/daridev/20-areas/work/django/django-bruno.md` never applied. Stakeholder intent is manual UI exploration (no `bru run` CI).

## Goals / Non-Goals

**Goals:**
- 1:1 mirroring of every API endpoint as version-controlled `.bru` files under `bruno/` that open in Bruno 3.0+ via `workspace.yml`.
- Every request embeds authoritative expected responses in a `docs {}` block (faithful to serializers, not invented) so a developer understands contracts without running the server.
- Separate `.bru` files for success and error variants (`400` validation, `401` auth/not-found — including `GET /api/sales/?stripe_code=invalid` which intentionally returns `401` per `views.py:75` and `POST /api/sales/` invalid `vip_code` → `401 {message:"Invalid VIP code"}` per `views.py:118`) plus cross-cutting `_auth` unauthenticated exemplar.
- Snake_case subfolder organization (`catalog/hotels/`, `pricing/`, `sales/sales/`, `sales/sales_done/`, `_auth/`) for discoverability.
- Expose optional `vip_code` tracking-only: `POST /api/sales/` `vip_code?: string(10) writeOnly` (`trim + iexact + active=True`; `""`/`null`/whitespace/missing → `None` → `201` else invalid → `401` with no rows via `transaction.atomic`), `GET /api/sales/?stripe_code=` returns `vip_code: value|null` (`views.py:83`), no pricing bypass.

**Non-Goals:**
- No Go API changes, no OpenAPI/`drf-spectacular` introduction, no codegen script in this change (Approach A manual).
- No `bru run` automation, pre-request `script:js` token minting, or CI wiring (follow-up per `django-bruno.md:281`).
- No `dev.sh` subdomain helper; `{{base_url}}` defaults to `http://127.0.1:8000` with documentation of `http://localhost:8000` fallback.
- No `vip_code` discount/pricing logic (tracking-only, `PROTECT` delete blocked).

## Decisions

### 1. Approach A — hand-written `.bru` over auto-generation
**Decision:** Write each `.bru` by hand; no generator script.
**Rationale:** 8 endpoints do not justify generator complexity. `SaleSerializer:50` is a non-`ModelSerializer` with `source="client.name"` nesting (`validate_vip_code:70`, `create:91`) and `SaleDoneSerializer:112` has conditional `departure_*` fields — OpenAPI generators mis-render these. Hand-written docs remain faithful and reviewable as plain-text diffs.
**Alternatives:** (B) Full codegen via `manage.py spectacular` + templating — deferred until >30 endpoints or OpenAPI is needed for other consumers. (C) Hybrid drift script — can be added later without rework.

### 2. Workspace layout — `bruno/workspace.yml` + `collections/marco-cabo-api/bruno.json`
**Decision:** Single workspace `bruno/` with one collection `marco-cabo-api` per `django-bruno.md:31`.
**Rationale:** Matches blueprint; `opencollection: 1.0.0` (spec version) vs `"version":"1"` (file format) kept distinct per `django-bruno.md:298`. Multiple collections would add navigation overhead for 8 endpoints.
**Alternatives:** Nested workspaces per domain — rejected (over-segmentation).

### 3. Environment handling — `dev.bru.example` committed, `dev.bru` gitignored
**Decision:** `bruno/templates/dev.bru.example` with `base_url: http://127.0.1:8000` and `token: <paste-token-here>` placeholders + `@description('''...''')` per `django-bruno.md:92`; `.gitignore` adds `bruno/**/environments/*.bru`; `README` documents copy-to-`dev.bru` + shell mint via `Token.objects.get_or_create`.
**Rationale:** Prevents credential leakage; mirrors blueprint security note (`django-bruno.md:105`). `http://127.0.1:8000` matches `.env.dev:6`; comment notes `http://localhost:8000` fallback.
**Alternatives:** Shared `bruno/environments/` at workspace root — not supported; blueprint scope is collection-level.

### 4. Subfolders + snake_case vs flat Catalog + cross-cutting _auth
**Decision:** `catalog/hotels/`, `catalog/postal_codes/`, `catalog/vehicles/`, `catalog/service_types/`, `catalog/pricing/` and `sales/sales/`, `sales/sales_done/` with files like `get_list.bru`, `get_filtered.bru`, `post_create_minimal.bru`, plus top-level `_auth/get_unauthenticated.bru` (underscore prefix sorts first in Bruno sidebar, cross-cutting `401` exemplar, representative target `GET {{base_url}}/api/hotels/`).
**Rationale:** User-confirmed snake_case; flat `Catalog/` with 6 files would conflate pricing variants. `_auth/` isolates the unauthenticated `401` which is identical via `utils/handlers.py:4` for all endpoints — one exemplar avoids 5 clones while remaining discoverable at collection root (vs `catalog/hotels/get_list_unauthenticated.bru` which misled as hotels-specific).
**Alternatives:** One folder per model at collection root — more top-level folders. `catalog/hotels/get_list_unauthenticated.bru` — rejected as misleading. `auth/` without underscore — valid but sorts between `catalog`/`sales`, less visible.

### 5. Token header + invalid-call files (incl. vip_code)
**Decision:** Every `.bru` sets `auth: none` and `headers { Authorization: Token {{token}} }`; add explicit negative `.bru` files: `_auth/get_unauthenticated.bru` targeting `GET {{base_url}}/api/hotels/` with omitted `Authorization` header (or empty `{{token}}`) demonstrating `401 {status:"error",message:"Invalid token."}` (via `utils/handlers.py:4`); `sales/sales/get_by_stripe_code_not_found.bru` (`"Sale not found"` 401); `sales/sales/post_create_invalid.bru` (`400` for missing/invalid FKs); `sales/sales/post_create_invalid_vip_code.bru` (`401 {message:"Invalid VIP code",errors:{vip_code:["Invalid or inactive VIP code"]}}` with empty `{{token}}` check not needed — distinct from auth-missing 401, via `serializers.py:81` + `views.py:118`); `sales/sales/post_create_empty_vip_code.bru` documents `""`/`null`/missing → `None` → `201` + `GET` `null`; `sales/sales_done/post_confirm_invalid.bru`.
**Rationale:** Accurate to `IsAuthenticated` + `vip_code` `401` (different `message`/`errors` shape). Single `_auth` exemplar covers auth-missing; dedicated Sales vip files make tracking-only validation explorable without editing happy-path `post_create_*`. Separating `400` vs vip `401` prevents conflating the two branches in `views.py:118`.
**Alternatives:** Only `docs {}` for errors — rejected per user request. Per-endpoint `get_list_unauthenticated.bru` (5 clones) — rejected as duplication.

### 6. `docs {}` fidelity rules
**Decision:** Paginated examples use exact live envelope `{count,next,previous,results}` as asserted in `travels/tests/test_views.py` via `core/pagination.py:4` with 1-item `results` (no `page/page_size/total_pages`); Sales creation examples distinguish `201 {status:"success",message:"Sale created successfully",data:{payment_link:"https://checkout.stripe.com/... (dynamic)"}}` noting prefix-only, `400 {…Invalid sale data…}` for missing/invalid FKs (Spanish `Este campo es requerido.` + `Clave primaria "99" inválida`), and `401 {status:"error",message:"Invalid VIP code",errors:{vip_code:["Invalid or inactive VIP code"]}}` for `vip_code` (vs `401 {message:"Invalid token."}` in `_auth`); `GET /api/sales/` `200` includes `vip_code: "VIP123" | null` per `views.py:83`. No invented fields; prices as numbers (example totals `80.00` One Way / `160.00` Round Trip per current csv).
**Rationale:** Prevents doc drift; prices as numbers, media URLs absolute, examples minimal per blueprint `django-bruno.md:232`.
**Alternatives:** Full fixture dumps — too verbose.

### 7. vip_code tracking-only validation (now in scope)
**Decision:** `SaleSerializer.vip_code` is `CharField(required=False, allow_blank, allow_null, maxLength=10, writeOnly)`; `validate_vip_code` returns `None` for `""`/whitespace/`null`/missing, else `trim + iexact` lookup `VipCode(value__iexact=…, active=True)` → `VipCode` obj or `ValidationError("Invalid or inactive VIP code")`; `validate()` maps `VipCode|None` to `sale.vip_code`; `create()` wraps `Client`+`Sale` in `transaction.atomic()` (prevents orphan rows on 401); `SaleViewSet.post` branches `vip_code ∈ errors → 401 Invalid VIP code` else `400`; `Sale.vip_code` is `FK PROTECT null/blank` (`0039`), surfaced in `SaleAdmin`/`TransferAdmin` search.
**Rationale:** Mirrors HEAD `serializers.py:66-109`, `views.py:83-126`, `models.py:170`; tracking-only (no discount/bypass, `get_payment_link` always called); `PROTECT` preserves audit trail; atomic satisfies proposal’s `validate_no_data_created` guarantee.
**Alternatives:** Separate `/api/validate-vip-code/` — deleted; `CASCADE` — rejected; non-atomic create — rejected (orphan Client).

## Risks / Trade-offs

- **`payment_link` dynamic** (`utils/stripe.py:42` → external `STRIPE_API_HOST`) → Mitigation: `docs {}` shows prefix `https://checkout.stripe.com/` + note "value is dynamic per sale; 201 only asserts prefix" rather than a fixed URL.
- **`401` reused for "Sale not found"** (`views.py:75`) conflates auth vs not-found → Mitigation: `docs {}` and `get_by_stripe_code_not_found.bru` explicitly document this intentional reuse with error message `"Sale not found"` (distinct from vip `401` “Invalid VIP code”).
- **`vip_code` `401` vs auth `401` conflation** (`views.py:118` vs `utils/handlers.py:4`) → Mitigation: `_auth/get_unauthenticated.bru` shows `401 {message:"Invalid token."}` (no `errors`), `post_create_invalid_vip_code.bru` shows `401 {message:"Invalid VIP code",errors:{vip_code:[…]}}`; `docs {}` disambiguates `trim+iexact+active` rule.
- **Serializer ↔ docs drift** (incl. `vip_code` maxLength/validation) → Mitigation: Rule "serializer change must update matching `docs {}` in same PR" + reviewer checklist; future hybrid drift script can lint.
- **Token mint friction** (no login endpoint per `django-bruno.md:264`) → Mitigation: `dev.bru.example` description links to shell snippet; `_auth/get_unauthenticated.bru` demonstrates 401 by omitting `Authorization` header (or empty `{{token}}`).
- **Pagination mismatch if `CustomPageNumberPagination` is replaced** → Mitigation: Docs copy test-asserted shape `{count,next,previous,results}`; if pagination gains `page/page_size/total_pages`, update all catalog `docs {}`.
- **`base_url` drift if `.env.dev:6` changes** → Mitigation: `_auth` and `dev.bru.example` `@description` notes `base_url` must match `HOST` in `.env.dev` (`http://127.0.1:8000`, fallback `http://localhost:8000`); update example if `HOST` changes.
- **File proliferation (18-19 `.bru` incl. `_auth` + 3 vip variants)** → Mitigation: Subfolders keep navigation shallow; no deeper than 2 levels ( `_auth/` + `catalog/*` + `sales/sales` + `sales/sales_done` ).
- **`PROTECT` delete blocked** (`Sale.vip_code` FK) → Mitigation: Admin delete of in-use `VipCode` shows `ProtectedError`; docs note tracking-only semantics.

## Migration Plan

1. Create `bruno/workspace.yml`, `bruno/collections/marco-cabo-api/bruno.json` (no data migration; DB already has `0039_sale_vip_code` FK).
2. Add `bruno/templates/dev.bru.example` + `.gitignore` entry + copy instruction; `dev.bru` stays local.
3. Add `_auth/get_unauthenticated.bru` + catalog `get_list`/`get_filtered` + `sales/get_by_stripe_code(.not_found)` (docs with `vip_code:value|null`) + `sales/post_create_*` (6 variants: minimal/full/valid-vip/invalid-vip/empty-vip/invalid-generic) + `sales_done/post_confirm_*` + invalid Sales variants (single PR).
4. Open workspace in Bruno: verify `Open workspace` at `bruno/` (not collection subfolder) resolves `workspace.yml` per `django-bruno.md:292` and `_auth` sorts first.
5. No rollback beyond `git revert`; no new DB changes in this collection change (relies on `0039`).
6. Future: if vip validation tightens (e.g., discount logic), update `post_create_invalid_vip_code.bru` docs and pricing examples; no extra migration now.

## Open Questions

- None blocking — vip scope now aligned to HEAD `trim+iexact+active`, `PROTECT`, `transaction.atomic`. Optional follow-ups: `prod.bru.example` template (defer) and whether to alias `vip_code` → `invitation_code` in `docs {}` user-facing wording (keep `vip_code` for code fidelity).
