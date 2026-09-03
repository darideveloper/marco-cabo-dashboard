## ADDED Requirements

### Requirement: VipCode reference data
The system SHALL retain the `VipCode` model (`travels/models.py:80`) with `value` (unique, max 10, `verbose_name="Código"`), `active` (default True), `created_at`, `updated_at`; managed via `VipCodeAdmin` (`travels/admin.py:44`).

#### Scenario: Admin manages VIP codes
- **WHEN** an admin opens `VipCode` in admin
- **THEN** list displays `value`, `active`, `updated_at` and allows search on `value`

#### Scenario: Inactive code exists
- **WHEN** a `VipCode` has `active=False`
- **THEN** it SHALL NOT be considered valid for sales (see Requirement: Sale creation validates optional VIP code)

### Requirement: Sale carries optional VIP code
The system SHALL store an optional tracking-only VIP code on `Sale` as `Sale.vip_code` (`travels/models.py:136`) with `FK(VipCode, null=True, blank=True, on_delete=PROTECT, related_name="sales")`. The field SHALL be exposed as top-level `vip_code: string | null` on sale APIs.

#### Scenario: Sale without VIP
- **WHEN** `POST /api/sales/` is called without `vip_code`, or with `vip_code` as `""`, `null`, or missing
- **THEN** `sale.vip_code` SHALL be `NULL` and sale creation proceeds normally

#### Scenario: Sale with valid VIP persisted and returned
- **WHEN** `POST /api/sales/` is called with a valid VIP code
- **THEN** `sale.vip_code` SHALL be the matching `VipCode` FK and `GET /api/sales/?stripe_code=` SHALL return `data.vip_code` equal to the `VipCode.value`

#### Scenario: Delete protection
- **WHEN** an admin deletes a `VipCode` referenced by any `Sale`
- **THEN** the deletion SHALL be blocked with a `ProtectedError` (requires clearing `Sale.vip_code` first)

### Requirement: Sale creation validates optional VIP code
The system SHALL validate the optional `vip_code` inline in `POST /api/sales/` (`travels/views.py:116`, `travels/serializers.py:62 SaleSerializer`): trim whitespace, case-insensitive match (`value__iexact=trimmed`), and require `active=True`. Invalid cases SHALL return `401 {status:"error", message:"Invalid VIP code", errors:{vip_code:["Invalid or inactive VIP code"]}}` and SHALL NOT persist `Client` or `Sale` (atomic).

#### Scenario: Valid code accepted
- **WHEN** `POST /api/sales/` includes `vip_code: "  vip123 "` and a `VipCode(value="VIP123", active=True)` exists
- **THEN** validation SHALL pass (case-insensitive, trimmed) and sale is created with `201 {status:"success", data:{payment_link}}` and payment link is still generated (no bypass)

#### Scenario: Non-existent code rejected with 401
- **WHEN** `POST /api/sales/` includes `vip_code: "FAKE999"`
- **THEN** system SHALL return `401` with `errors.vip_code` containing `"Invalid or inactive VIP code"` and SHALL create zero `Client`/`Sale` rows

#### Scenario: Inactive code rejected with 401
- **WHEN** `POST /api/sales/` includes a `vip_code` whose `VipCode.active=False`
- **THEN** system SHALL return `401` with `errors.vip_code` and SHALL create zero rows

#### Scenario: Empty treated as absent
- **WHEN** `POST /api/sales/` includes `vip_code: ""` or `null`
- **THEN** system SHALL treat it as absent, SHALL NOT return `401`, and SHALL create the sale with `vip_code=None`

### Requirement: No payment bypass for VIP
A VIP code SHALL NOT alter pricing or skip Stripe. `SaleViewSet.post` (`travels/views.py:124 get_payment_link`) SHALL be called unconditionally regardless of `vip_code`.

#### Scenario: Valid VIP still pays
- **WHEN** a sale is created with a valid `vip_code`
- **THEN** `Sale.total` SHALL equal `Pricing` for the `location/vehicle/service_type` and a Stripe `payment_link` SHALL be returned

### Requirement: Separate VIP validation endpoint stays removed
The standalone `POST /api/validate-vip-code/` (`travels/views.py:40 VipCodeValidationView`, `travels/serializers.py:48 VipCodeValidationSerializer`, `project/urls.py:32`) SHALL NOT exist; commented dead code SHALL be deleted.

#### Scenario: Validate endpoint absent
- **WHEN** a client calls `POST /api/validate-vip-code/`
- **THEN** system SHALL return `404` (no route)

