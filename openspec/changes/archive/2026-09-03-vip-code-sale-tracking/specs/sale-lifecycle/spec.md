## ADDED Requirements

### Requirement: Sale creation carries optional vip_code
`POST /api/sales/` (`travels/views.py:116`, `travels/serializers.py:62 SaleSerializer`) SHALL accept an optional top-level `vip_code` string field (`required=False, allow_blank=True, allow_null=True, max_length=10, write_only=True`, `source="sale.vip_code"`). When present and non-empty, it SHALL be normalized via `strip()` and validated as a valid `VipCode`; when missing/empty/`null`, it SHALL map to `None`.

#### Scenario: Request schema without VIP unchanged
- **WHEN** `POST /api/sales/` is sent with `{service_type, client_name, client_last_name?, client_email, location, vehicle}` and no `vip_code`
- **THEN** validation of existing required fields SHALL behave as before (`400 {message:"Invalid sale data", errors:{field: [...]}}` on missing/invalid FKs — Spanish messages as in `travels/tests/test_views.py:483`) and sale creation SHALL proceed

#### Scenario: Request schema with VIP string
- **WHEN** `POST /api/sales/` is sent with `vip_code: "VIP123"` (or trimmed/any case)
- **THEN** the field SHALL be accepted as valid input when the code exists and active, and rejected with `401` when invalid

### Requirement: Sale creation is atomic with no orphan Client
`SaleSerializer.create()` (`travels/serializers.py:79`) SHALL wrap `Client.objects.create` + `Pricing` lookup + `Sale.objects.create` in `transaction.atomic`, and `SaleViewSet.post` `travels/views.py:116` validation SHALL run before creation so an invalid `vip_code` creates zero `Client`/`Sale`/`Transfer` rows.

#### Scenario: Invalid VIP leaves no trace
- **WHEN** `POST /api/sales/` with `vip_code:"FAKE"` fails validation
- **THEN** `Client.objects.count()` and `Sale.objects.count()` SHALL remain `0` (verified as in `travels/tests/test_views.py:463 validate_no_data_created`)

#### Scenario: Pricing still resolved under atomic
- **WHEN** a valid sale is created
- **THEN** `Sale.total` SHALL equal `Pricing.price` for `location/vehicle/service_type` as before (`travels/tests/test_views.py:614` `90.00` one-way, `L653` `170.00` round-trip)

### Requirement: Invalid VIP returns custom 401
When `vip_code` validation fails, `SaleViewSet.post` `travels/views.py:141` SHALL branch: if `serializer.errors` contains `vip_code` → return `401 {status:"error", message:"Invalid VIP code", errors:{vip_code:["Invalid or inactive VIP code"]}}` instead of the generic `400 Invalid sale data`. All other sale validation remains `400 {message:"Invalid sale data", errors:{…}}`. Unauthenticated requests still use `utils/handlers.py:4` → `401 {status:"error", message:"detail"}`.

#### Scenario: VIP 401 shape
- **WHEN** `POST /api/sales/` with `vip_code:"FAKE"` is rejected
- **THEN** response SHALL be `401` with `message:"Invalid VIP code"` and `errors.vip_code` present

#### Scenario: Non-VIP errors stay 400
- **WHEN** `POST /api/sales/` with missing `service_type`
- **THEN** response SHALL be `400 {message:"Invalid sale data", errors:{service_type:[...]}}`

### Requirement: Sale retrieval exposes vip_code
`GET /api/sales/?stripe_code=` (`travels/views.py:68`) SHALL include `data.vip_code: string | null` (the `VipCode.value` or `null`) alongside existing fields (`id, service_type, location, vehicle, total, stripe_code, client`). Lookup remains by `stripe_code` (`models.py:162`).

#### Scenario: Retrieve sale with VIP
- **WHEN** `GET /api/sales/?stripe_code=<uuid>` for a sale with `vip_code="VIP123"`
- **THEN** `data.vip_code` SHALL equal `"VIP123"`

#### Scenario: Retrieve sale without VIP
- **WHEN** retrieving a sale created without `vip_code`
- **THEN** `data.vip_code` SHALL be `null`

#### Scenario: Not found stays 401
- **WHEN** `GET /api/sales/?stripe_code=invalid`
- **THEN** system SHALL return `401 {status:"error", message:"Sale not found", data:{}}` as in `views.py:76`
