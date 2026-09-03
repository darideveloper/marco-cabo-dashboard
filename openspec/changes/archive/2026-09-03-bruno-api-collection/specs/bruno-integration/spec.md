## ADDED Requirements

### Requirement: Bruno workspace scaffold
The system SHALL ship a Bruno 3.0+ workspace at `bruno/` that Bruno opens as a workspace (not a bare collection).

#### Scenario: Workspace opens in Bruno UI
- **WHEN** a developer selects `bruno/` via `Workspace dropdown → Open workspace`
- **THEN** Bruno loads without `Invalid workspace: workspace.yml not found` and shows collection `Marco Cabo API`

#### Scenario: Workspace files are version-controlled
- **WHEN** the change is archived
- **THEN** `bruno/workspace.yml` exists with `opencollection: 1.0.0` and `collections: - name: "Marco Cabo API" path: "collections/marco-cabo-api"`, and `bruno/collections/marco-cabo-api/bruno.json` exists with `{"version":"1","name":"Marco Cabo API","type":"collection"}`

### Requirement: Environment template and gitignore
The system SHALL provide a committed environment template and ignore real credentials.

#### Scenario: Dev environment template
- **WHEN** a developer clones the repo
- **THEN** `bruno/templates/dev.bru.example` exists with `vars { base_url: http://127.0.1:8000, token: <paste-token-here> }` and `@description('''...''')` for each var, and no real token is committed

#### Scenario: Real env is local-only
- **WHEN** a developer copies `dev.bru.example` to `dev.bru` and pastes a real token minted via `Token.objects.get_or_create(user=...)`
- **THEN** `dev.bru` is ignored by git via `bruno/**/environments/*.bru` and requests using `{{base_url}}` / `{{token}}` resolve to the pasted values

#### Scenario: Environment display name
- **WHEN** the collection is open in Bruno
- **THEN** the environment appears as `dev` (file basename) in the top-right dropdown

### Requirement: Catalog read-only endpoints mirrored
The system SHALL mirror each read-only catalog ViewSet as `.bru` requests under `bruno/collections/marco-cabo-api/catalog/` with snake_case subfolders and `docs {}` expected-response blocks.

#### Scenario: Hotels list
- **WHEN** `catalog/hotels/get_list.bru` is sent with `Authorization: Token {{token}}`
- **THEN** it targets `GET {{base_url}}/api/hotels/` with `auth: none` and `docs {}` documents `200 {count,next,previous,results:[{id,name,locations:[{id,name}]}]}` and `401` is documented via the cross-cutting `_auth/get_unauthenticated.bru` exemplar, faithfully to `travels/views.py:13` and `ZoneSerializer`

#### Scenario: Postal codes list
- **WHEN** `catalog/postal_codes/get_list.bru` is sent
- **THEN** it targets `GET {{base_url}}/api/postal-codes/` and `docs {}` shows `results` as `Location` objects where `zone__name="Codigo Postal"` per `travels/views.py:18`

#### Scenario: Vehicles list
- **WHEN** `catalog/vehicles/get_list.bru` is sent
- **THEN** it targets `GET {{base_url}}/api/vehicles/` and `docs {}` shows `{id,name,passengers}` per `VehicleSerializer`

#### Scenario: Service types list
- **WHEN** `catalog/service_types/get_list.bru` is sent
- **THEN** it targets `GET {{base_url}}/api/service-types/` and `docs {}` shows `{id,name}` per `ServiceTypeSerializer`

#### Scenario: Pricing list and filtered
- **WHEN** `catalog/pricing/get_list.bru` is sent
- **THEN** it targets `GET {{base_url}}/api/pricing/` with nested `location:{id,name},vehicle:{id,name,passengers},service_type:{id,name},price` per `PricingSerializer`; **WHEN** `catalog/pricing/get_filtered.bru` is sent **THEN** it targets `GET {{base_url}}/api/pricing/?location=1&vehicle=1&service_type=1` and `docs {}` notes each query param is optional (`DjangoFilterBackend` `filterset_fields`) and demonstrates 1-item filtered result

### Requirement: Cross-cutting unauthenticated exemplar
The system SHALL provide a single unauthenticated exemplar under `bruno/collections/marco-cabo-api/_auth/` that demonstrates `401` for all `IsAuthenticated` endpoints.

#### Scenario: Unauthenticated request returns 401
- **WHEN** `_auth/get_unauthenticated.bru` is sent as `GET {{base_url}}/api/hotels/` with `auth: none` and omitting the `Authorization` header (or leaving `{{token}}` empty)
- **THEN** the server returns `401 {status:"error",message:"Invalid token.",data:{}}` via `utils/handlers.py:4` and `docs {}` notes this same `401` applies to every endpoint (`/api/hotels/`, `/api/postal-codes/`, `/api/vehicles/`, `/api/service-types/`, `/api/pricing/`, `/api/sales/`, `/api/sales/done/`) using `GET /api/hotels/` as the representative target

### Requirement: Sales query endpoint mirrored
The system SHALL mirror `GET /api/sales/?stripe_code=` as `.bru` requests under `sales/sales/` with success and not-found variants.

#### Scenario: Get sale by stripe_code success
- **WHEN** `sales/sales/get_by_stripe_code.bru` is sent as `GET {{base_url}}/api/sales/?stripe_code={{stripe_code}}` with token
- **THEN** `docs {}` documents `200 {status:"success",message:"Sale data retrieved successfully",data:{id,service_type:{id,name},location:{id,name},vehicle:{id,name,passengers},total,stripe_code,vip_code:"VIP123"|null,client:{name,last_name,email}}}` per `travels/views.py:83-89` (vip_code is `value` if Sale has FK else `null`, `travels/models.py:170`) and notes `stripe_code` is a UUID query param

#### Scenario: Get sale by stripe_code success with vip_code
- **WHEN** `sales/sales/get_by_stripe_code.bru` is sent for a sale created with `vip_code`
- **THEN** `data.vip_code` equals that `VipCode.value` (e.g., `"VIP123"` trimmed+uppercased as stored) and `docs {}` shows `vip_code` as string; **WHEN** sale was created with `vip_code:""`/`null`/missing **THEN** `data.vip_code` is `null`

#### Scenario: Get sale not found returns 401
- **WHEN** `sales/sales/get_by_stripe_code_not_found.bru` is sent with `?stripe_code=invalid`
- **THEN** the server returns `401 {status:"error",message:"Sale not found",data:{}}` per `travels/views.py:75` and `docs {}` notes this intentional `401` reuse (not `404`) and that the query param is required

### Requirement: Sales creation endpoints mirrored
The system SHALL mirror `POST /api/sales/` as `.bru` requests under `sales/sales/` with minimal, full, vip, and invalid variants.

#### Scenario: Create sale minimal
- **WHEN** `sales/sales/post_create_minimal.bru` is sent as `POST {{base_url}}/api/sales/` with `body: json` containing `{service_type:1,client_name:"John",client_email:"john@example.com",location:1,vehicle:1}` (no `vip_code` key)
- **THEN** the server returns `201 {status:"success",message:"Sale created successfully",data:{payment_link:"https://checkout.stripe.com/..."}}` and `docs {}` notes `payment_link` is dynamic and only the prefix is assertable, with total derived from `Pricing` per `travels/serializers.py:97` and `GET` will return `vip_code:null`

#### Scenario: Create sale full
- **WHEN** `sales/sales/post_create_full.bru` is sent with the same fields plus `client_last_name:"Doe"`
- **THEN** it demonstrates optional `client_last_name` handling (`required:false, allow_blank, allow_null` per `SaleSerializer:56`) and returns `201` as above

#### Scenario: Create sale with valid vip_code
- **WHEN** `sales/sales/post_create_with_valid_vip_code.bru` is sent with `vip_code: "  vip123  "` (spaces + lowercase to demonstrate `trim + iexact`)
- **THEN** `validate_vip_code` (`serializers.py:70`, `value__iexact` + `active=True`) returns `VipCode` obj, `Sale` is created with `vip_code` FK (`models.py:170` `PROTECT`) via `transaction.atomic()`, server returns `201` and subsequent `GET /api/sales/?stripe_code=` returns `vip_code:"VIP123"`; `docs {}` notes `vip_code` is tracking-only (no discount/bypass) and `writeOnly CharField(10)`

#### Scenario: Create sale with empty vip_code treated as none
- **WHEN** `sales/sales/post_create_empty_vip_code.bru` is sent with `vip_code:""` or `null` or missing key
- **THEN** `validate_vip_code` returns `None`, `Sale` is created with `vip_code=None` via `transaction.atomic()`, server returns `201` and `GET` returns `vip_code:null`; `docs {}` notes `""`/`null`/whitespace/missing all map to `None`

#### Scenario: Create sale with invalid vip_code returns 401
- **WHEN** `sales/sales/post_create_invalid_vip_code.bru` is sent with `vip_code:"FAKE999"` (nonexistent) or inactive code
- **THEN** `validate_vip_code` raises `ValidationError("Invalid or inactive VIP code")`, `SaleViewSet.post` (`views.py:118`) returns `401 {status:"error",message:"Invalid VIP code",errors:{vip_code:["Invalid or inactive VIP code"]}}` and no `Client`/`Sale` rows are persisted (`transaction.atomic()` + `validate_no_data_created` per `tests/test_views.py`)

#### Scenario: Create sale invalid returns 400
- **WHEN** `sales/sales/post_create_invalid.bru` is sent with empty body or invalid `service_type:99`
- **THEN** the server returns `400 {status:"error",message:"Invalid sale data",errors:{service_type:["Clave primaria \"99\" inválida - objeto no existe."], ...}}` per `travels/views.py:127-134` and `tests/test_views.py:491` and `docs {}` shows required-field and invalid-PK examples distinct from the `401` vip_code branch

### Requirement: Sales confirmation endpoints mirrored
The system SHALL mirror `POST /api/sales/done/` as `.bru` requests under `sales/sales_done/` with one-way, round-trip, and invalid variants.

#### Scenario: Confirm sale one-way
- **WHEN** `sales/sales_done/post_confirm_one_way.bru` is sent as `POST {{base_url}}/api/sales/done/` with `body: json` containing `{sale_stripe_code,client_phone,passengers,details?,arrival_date,arrival_time,arrival_airline,arrival_flight_number}`
- **THEN** the server returns `200 {status:"success",message:"Sale confirmed successfully",data:[]}` and creates one `Transfer` of `type:"arrival"` per `travels/views.py:199`; `docs {}` notes `details` is optional and `departure_*` fields are absent for One Way

#### Scenario: Confirm sale round-trip
- **WHEN** `sales/sales_done/post_confirm_round_trip.bru` is sent with the same plus `departure_date,departure_time,departure_airline,departure_flight_number` and the sale's `service_type.name=="Round Trip"`
- **THEN** the server creates both `arrival` and `departure` `Transfer`s per `travels/views.py:207` and returns `200` as above; `docs {}` notes departure fields are required only for Round Trip

#### Scenario: Confirm sale invalid returns 400 or 401
- **WHEN** `sales/sales_done/post_confirm_invalid.bru` is sent with missing `sale_stripe_code` or already-paid sale or invalid `stripe_code`
- **THEN** the server returns `400 {status:"error",message:"Invalid sale data",data:{}}` or `401 {status:"error",message:"Invalid sale data",data:{}}` or `400 {status:"error",message:"Sale already paid",data:[]}` per `travels/views.py:165-184` and `docs {}` documents each branch with `WHEN` a used/unknown `stripe_code` is sent

### Requirement: Mandatory docs block per request
Every `.bru` file SHALL carry a `docs {}` block that documents expected responses without requiring a live run.

#### Scenario: Docs completeness
- **WHEN** any `.bru` is inspected without sending
- **THEN** its `docs {}` contains Markdown with endpoint purpose + `Authorization: Token` requirement (or notes omitted header for `_auth` exemplar), status codes (`200` ViewSets, `201` `POST /api/sales/` + `401 Invalid VIP code` for vip branch + `400` for other validation + `401` for auth/not-found per `views.py:118-134`/`utils/handlers.py:4`), abbreviated JSON examples derived from serializers (paginated `{count,next,previous,results}` for catalog, `{status,message,data|errors}` for sales incl. `vip_code: value|null` on `GET` and `vip_code` writeOnly string(10) on `POST`), no invented fields, prices as numbers, and a note that serializer changes must update the matching `docs` in the same change

#### Scenario: Pagination fidelity
- **WHEN** a catalog `docs {}` is read
- **THEN** it shows the actual `CustomPageNumberPagination` envelope (`count`, `next`, `previous`, `results`) per `core/pagination.py:4` not speculative `page/page_size/total_pages`, with one abbreviated list item

#### Scenario: Seq ordering per folder
- **WHEN** `_auth/`, `catalog/pricing/`, or `sales/sales/` is inspected
- **THEN** `meta { seq }` is incremental per folder: `get_list` `seq:1`, `get_filtered` `seq:2`, `..._invalid`/`..._not_found` `seq:2+` (or `3` if filtered exists), and `sales/sales/` orders `post_create_minimal` `seq:1`, `post_create_full` `seq:2`, `post_create_with_valid_vip_code` `seq:3`, `post_create_empty_vip_code` `seq:4`, `post_create_invalid_vip_code` `seq:5`, `post_create_invalid` `seq:6`, ensuring Bruno tabs open in logical order
