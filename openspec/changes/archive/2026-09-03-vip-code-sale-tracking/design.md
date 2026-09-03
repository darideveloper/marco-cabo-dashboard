## Context

`VipCode` (`travels/models.py:80`) survives as an orphan table (`value unique10`, `active`, timestamps) with `VipCodeAdmin` (`travels/admin.py:44`) but `Sale.vip_code` was dropped in `0037_remove_sale_vip_code.py:13` (previously `FK CASCADE`, then `null/blank` in `0022`). Validation stacks (`travels/serializers.py:48 VipCodeValidationSerializer`, `travels/views.py:40 VipCodeValidationView`, `project/urls.py:32 validate-vip-code`, `travels/tests/test_views.py:342`) are commented; `SaleViewSet` previously bypassed `utils/stripe.py:6 get_payment_link` when `sale.vip_code` present (`views.py:123`). Current `SaleSerializer.create()` (`serializers.py:79`) creates `Client` then `Sale` without `transaction.atomic`, and `SaleViewSet.post` (`views.py:116`) always generates a Stripe link.

Stakeholders: backend `Sale` lifecycle, admin tracking, optional frontend VIP field. No pricing change, no fleet logic, no frontend in this repo.

## Goals / Non-Goals

**Goals:**
- Restore `Sale.vip_code` as optional tracking FK with safe delete semantics (`PROTECT`).
- Validate optional `vip_code` inline in `POST /api/sales/` (trim + `value__iexact` + `active=True`), `401 Invalid VIP code` on failure, zero side-effects (atomic), empty/missing → `None`.
- Always generate Stripe payment link (no bypass).
- Expose `vip_code` in `GET /api/sales/?stripe_code=` and in admin filters/search.
- Delete commented dead code for the separate `/api/validate-vip-code/` endpoint.

**Non-Goals:**
- Discounts/pricing changes, VIP-specific products, new auth, new read-only catalog behavior, frontend implementation, separate validate endpoint resurrection, bulk import of codes.

## Decisions

**1. Model: `FK(VipCode, null=True, blank=True, on_delete=PROTECT, related_name="sales")` on `Sale`**
- *Rationale:* `PROTECT` preserves audit trail — deleting a code in use must be explicit (clear sales first), unlike prior `CASCADE` which deleted sales, and unlike `SET_NULL` which silently loses provenance. One migration `0039_sale_vip_code` restores prior field (`0001_initial.py:59`, `0017`, `0022`) with corrected semantics.
- *Alt considered:* `SET_NULL` — allows quick cleanup, loses tracking. `CASCADE` — rejected (historic sales loss). Decision reversible: change `on_delete` later without code churn.

**2. Serializer field: optional `CharField(max_length=10, required=False, allow_blank=True, allow_null=True, write_only=True, source="sale.vip_code")` + custom validation in `validate()` / `validate_vip_code`**
- *Rationale:* Frontend sends raw `value` string (`POST {vip_code:"VIP123"}`) not DB PK — minimal frontend change, matches old `VipCodeValidationSerializer:49`. Field maps to FK via `value__iexact` lookup. `strip()` normalizes `"  VIP "` and `iexact` gives case-insensitive UX (`vip123` == `VIP123` as requested).
- *Alt considered:* `PrimaryKeyRelatedField(queryset=VipCode)` with `vip_code_id` — requires frontend to know IDs, extra lookup.
- *Validation:* `trimmed = (value or "").strip(); if not trimmed: None` → else `VipCode.objects.get(value__iexact=trimmed, active=True)` else `ValidationError("Invalid or inactive VIP code")`. Use `value__iexact` not `value=` per `trim+case-insensitive` requirement.

**3. Atomic creation in `SaleSerializer.create()`**
- *Rationale:* Current code `travels/serializers.py:79` creates `Client` before `Sale`; without atomic, invalid VIP would orphan `Client`. Wrapping `Client.create` + `Pricing.get` + `Sale.create` in `transaction.atomic()` makes validation failures leave zero rows (checked by `validate_no_data_created` in `test_views.py:463`).
- *Alt considered:* Validate before `create()` only — still need atomic for `Pricing.DoesNotExist` after `Client` creation.

**4. View branching for `401` on invalid VIP**
- *Rationale:* Requested custom `401 {message:"Invalid VIP code"}` distinct from generic sale `400 {message:"Invalid sale data"}` and from auth `401` via `utils/handlers.py:4`. `SaleViewSet.post:141` checks `if "vip_code" in serializer.errors: return Response(..., status=401)` else `400`. Other `400`s unchanged; `GET /api/sales/` retrieval `views.py:68` adds `vip_code` to `data`.
- *Alt considered:* Always `400` with `errors.vip_code` — simpler but violates requested `401` contract.

**5. Purge dead commented endpoint instead of resurrecting**
- *Rationale:* `VipCodeValidationSerializer`, `VipCodeValidationView`, `/api/validate-vip-code/` route, and commented tests (`test_views.py:342`) are dead since `0037`. One `POST /api/sales/` call suffices for validation; separate endpoint adds a round-trip and race (`code deactivated between validate and sale`). Deleting comments reduces noise; re-adding later is trivial from git history.
- *Alt considered:* Keep commented code "for later" — rejected, violates minimal diff / ponytail.

**6. Admin re-enable `vip_code`**
- *Rationale:* Re-add `vip_code` to `SaleAdmin.list_display:67`, `list_filter:80`, `search_fields:92 (vip_code__value)`, and `TransferAdmin.search_fields:224 (sale__vip_code__value)` so tracking is visible. No new admin needed — `VipCodeAdmin:44` already correct.

## Risks / Trade-offs

- **Extra SELECT per `POST` with VIP** (`value__iexact`) → Mitigation: `value` is unique and indexed (implicit), one query, negligible vs. Stripe call.
- **PROTECT blocks admin deletes** → Mitigation: Admin shows `ProtectedError` with referencing sales; operator must null/clear sales first or deactivate code (`active=False`) instead of deleting.
- **401 for VIP vs 401 for auth/not-found** (`GET /api/sales/?stripe_code` returns `401 Sale not found` `views.py:82`, auth failures via `handlers.py:14`) → Mitigation: VIP `401` body includes `errors.vip_code` to disambiguate from auth/sale-not-found shapes; frontend checks `errors.vip_code` presence.
- **Price lookup still `Pricing.objects.get` without 404 handling** → Mitigation: existing behavior preserved; will `500` on missing pricing — intentional to surface misconfiguration (as before).
- **Frontend must send top-level `vip_code` string** → Mitigation: field optional, so old payloads remain valid; update landing repo docs.

## Migration Plan

1. Deploy code + migration `0039_sale_vip_code` (AddField nullable — no backfill, no downtime; existing rows get `NULL`).
2. No data migration needed; existing `VipCode` rows preserved.
3. Rollback: revert migration (`RemoveField`) and code; `VipCode` table untouched.
4. Post-deploy: verify `rg -n "validate-vip-code|VipCodeValidation" --include="*.py"` returns 0 (aside from `create_vip_code` helper).

## Open Questions

- None blocking. Confirmed: `message:"Invalid VIP code"`, trim+iexact, `PROTECT`, no separate endpoint.
