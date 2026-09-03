## Why

VIP codes exist as an orphaned model (`travels/models.py:80 VipCode`) since `0037_remove_sale_vip_code.py:13` removed `Sale.vip_code`. All validation paths (`travels/serializers.py:48 VipCodeValidationSerializer`, `travels/views.py:40 VipCodeValidationView`, `project/urls.py:32 /api/validate-vip-code/`, `travels/tests/test_views.py:342 VipCodeValidationViewTestCase`) are commented but the `VipCode` table and `VipCodeAdmin` (`travels/admin.py:44`) remain. The business needs tracking-only VIP codes on sales: optional at booking, validated inline, no payment bypass, and no separate validation endpoint.

## What Changes

- **Restore `Sale.vip_code` FK** as nullable `FK(VipCode, null=True, blank=True, on_delete=PROTECT, related_name="sales", verbose_name="Código VIP")` — replaces the removed `0037` field with safer delete semantics (`PROTECT` not prior `CASCADE`). Migration `0039_sale_vip_code`.
- **Inline validation in `POST /api/sales/`** (`travels/views.py:116 SaleViewSet` + `travels/serializers.py:62 SaleSerializer`): add optional `vip_code: string` field; trim + `value__iexact` + `active=True` lookup; invalid (non-existent or inactive) → `401 {status:"error", message:"Invalid VIP code", errors:{vip_code:["Invalid or inactive VIP code"]}}` and no `Client`/`Sale` persisted; empty `""` / `null` / missing → `None` (sale proceeds as today). Wrap `SaleSerializer.create()` (`travels/serializers.py:79`) in `transaction.atomic` to avoid orphan `Client`.
- **Expose `vip_code` in `GET /api/sales/?stripe_code=`** (`travels/views.py:68`): include `vip_code: value | null` in response `data`.
- **Re-enable admin surfacing** (`travels/admin.py:67,80,92 SaleAdmin`, `L224 TransferAdmin`): `vip_code` in `list_display`, `list_filter`, `search_fields` (`vip_code__value`, `sale__vip_code__value`).
- **BREAKING (error contract)**: `POST /api/sales/` now returns `401` for invalid VIP codes; all other sale validation remains `400`. Unauthenticated requests still `401` via `utils/handlers.py:4 custom_exception_handler`.
- **Removal**: Delete commented dead code for separate endpoint — `VipCodeValidationSerializer`, `VipCodeValidationView`, `/api/validate-vip-code/` route, and its commented tests — instead of leaving them commented.

## Capabilities

### New Capabilities
- `vip-code-tracking`: Tracking-only VIP codes on sales — optional `vip_code` string at `POST /api/sales/`, validated (`trim + case-insensitive + active=True`), persisted as `Sale.vip_code FK`, returned in `GET /api/sales/`, surfaced in admin. No pricing/discount change.

### Modified Capabilities
- `sale-lifecycle`: `POST /api/sales/` creation and `GET /api/sales/` retrieval contract extended to carry `vip_code`; creation is now atomic and has a new `401` error branch for VIP.
- `admin-sales`: Sale/Transfer admin list/filter/search extended to VIP.

## Impact

- **Code**: `travels/models.py:136`, `travels/serializers.py:62`, `travels/views.py:68,116`, `travels/admin.py:44,61,207`, `project/urls.py:32`, migration `0039`, tests `core/tests_base/test_models.py:153`, `travels/tests/test_views.py`.
- **APIs**: `POST /api/sales/` (new optional field + new `401`), `GET /api/sales/?stripe_code=` (new field), `POST /api/sales/done/` unchanged, read-only catalog endpoints (`/api/hotels/`, `/api/postal-codes/`, `/api/vehicles/`, `/api/service-types/`, `/api/pricing/`) unchanged. `POST /api/validate-vip-code/` stays removed.
- **DB**: One `AddField` with `PROTECT`; existing `VipCode` rows preserved; `PROTECT` blocks deletion of in-use codes (admin shows `ProtectedError`).
- **Dependencies**: None new. `django.db.transaction`, `django.db.models.PROTECT`.
- **Risks**: Extra `SELECT` per `POST` with VIP; `PROTECT` requires handling in admin deletes.
