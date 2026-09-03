## 1. Workspace scaffold

- [x] 1.1 Create `bruno/workspace.yml` with `opencollection: 1.0.0`, `info.name: "Marco Cabo Dashboard"` (or repo dir name), `type: workspace`, `collections: - name: "Marco Cabo API" path: "collections/marco-cabo-api"`
- [x] 1.2 Create `bruno/collections/marco-cabo-api/bruno.json` with `{"version":"1","name":"Marco Cabo API","type":"collection"}`
- [x] 1.3 Create `bruno/templates/dev.bru.example` with `vars { base_url: http://127.0.1:8000, token: <paste-token-here> }` + `@description('''...''')` for each var referencing `http://localhost:8000` fallback and shell mint `Token.objects.get_or_create`
- [x] 1.4 Add `.gitignore` entry `bruno/**/environments/*.bru` (keep `*.bru.example` tracked); verify `bruno/collections/marco-cabo-api/environments/dev.bru` is ignored and not committed
- [x] 1.5 Smoke-open workspace in Bruno Desktop 3.0+ via `Open workspace` at `bruno/` and verify environment `dev` appears in dropdown

## 2. Catalog read-only requests + cross-cutting _auth (subfolders + snake_case)

- [x] 2.1 Create `bruno/collections/marco-cabo-api/_auth/get_unauthenticated.bru` (`GET {{base_url}}/api/hotels/` with `auth: none` and omitting `Authorization` header (or empty `{{token}}`), `docs {}` with `401 {status:"error",message:"Invalid token.",data:{}}` via `utils/handlers.py:4` and note same `401` applies to every endpoint — representative target `GET /api/hotels/`)
- [x] 2.2 Create `catalog/hotels/get_list.bru` (`GET {{base_url}}/api/hotels/`, `headers { Authorization: Token {{token}} }`, `auth: none`, `docs {}` with `200 {count,next,previous,results:[{id,name,locations:[{id,name}]}]}` + `docs` note `401` is covered by `_auth/get_unauthenticated.bru` exemplar)
- [x] 2.3 Create `catalog/postal_codes/get_list.bru` (`GET {{base_url}}/api/postal-codes/`, `docs {}` noting `zone__name="Codigo Postal"` filter)
- [x] 2.4 Create `catalog/vehicles/get_list.bru` (`GET {{base_url}}/api/vehicles/`, `docs {}` with `{id,name,passengers}`)
- [x] 2.5 Create `catalog/service_types/get_list.bru` (`GET {{base_url}}/api/service-types/`, `docs {}` with `{id,name}`)
- [x] 2.6 Create `catalog/pricing/get_list.bru` (`GET {{base_url}}/api/pricing/`, `docs {}` with nested `location/vehicle/service_type/price`)
- [x] 2.7 Create `catalog/pricing/get_filtered.bru` (`GET {{base_url}}/api/pricing/?location=1&vehicle=1&service_type=1`, `docs {}` noting optional `DjangoFilterBackend` params + single filtered result example)

## 3. Sales query requests (with vip_code)

- [x] 3.1 Create `sales/sales/get_by_stripe_code.bru` (`GET {{base_url}}/api/sales/?stripe_code={{stripe_code}}`, `docs {}` with `200 {status:"success",message:"Sale data retrieved successfully",data:{id,service_type:{id,name},location:{id,name},vehicle:{id,name,passengers},total,stripe_code,vip_code:"VIP123"|null,client:{name,last_name,email}}}` per `views.py:83-89` + note `vip_code` is `value` if FK else `null` per `models.py:170`)
- [x] 3.2 Create `sales/sales/get_by_stripe_code_not_found.bru` (`GET ...?stripe_code=invalid`, `docs {}` noting intentional `401 {status:"error",message:"Sale not found",data:{}}` per `views.py:75`)
- [x] 3.3 Assign `seq` per folder incremental: `get_list` `seq:1`, `get_filtered` `seq:2`, `..._invalid`/`..._not_found` `seq:2+` (or `3` if filtered exists); `_auth` holds single file `seq:1`; `sales/sales/` orders `get_by_stripe_code` `seq:1`, `get_by_stripe_code_not_found` `seq:2`

## 4. Sales creation requests (incl. vip_code)

- [x] 4.1 Create `sales/sales/post_create_minimal.bru` (`POST {{base_url}}/api/sales/`, `body: json` with `{service_type,client_name,client_email,location,vehicle}` (no `vip_code` key), `docs {}` with `201 {status:"success",message:"Sale created successfully",data:{payment_link:"https://checkout.stripe.com/..."}}` noting prefix-only + `GET` will return `vip_code:null`, + `400` for missing fields with `Este campo es requerido.`)
- [x] 4.2 Create `sales/sales/post_create_full.bru` (same + `client_last_name`, `docs {}` noting optional `allow_blank/allow_null` per `SaleSerializer:56`)
- [x] 4.3 Create `sales/sales/post_create_with_valid_vip_code.bru` (`POST {{base_url}}/api/sales/` body with `vip_code:"  vip123  "` (spaces+lowercase → trim+iexact+active, per `serializers.py:70`), `docs {}` with `201` + persisted `Sale.vip_code` FK `PROTECT` + `GET` returns `vip_code:"VIP123"`, tracking-only no discount)
- [x] 4.4 Create `sales/sales/post_create_empty_vip_code.bru` (`vip_code:""` / `null` / missing → `None`, `docs {}` with `201` + `GET` `vip_code:null` per `serializers.py:72-76`)
- [x] 4.5 Create `sales/sales/post_create_invalid_vip_code.bru` (`vip_code:"FAKE999"` nonexistent or inactive → `401 {status:"error",message:"Invalid VIP code",errors:{vip_code:["Invalid or inactive VIP code"]}}` per `views.py:118` + `serializers.py:81` + no rows via `transaction.atomic()`)
- [x] 4.6 Create `sales/sales/post_create_invalid.bru` (empty/invalid `service_type:99`, `docs {}` with `400 {status:"error",message:"Invalid sale data",errors:{...}}` + `Clave primaria "99" inválida` example distinct from vip `401`)
- [x] 4.7 Ensure `sales/sales/post_create_*.bru` use `post { url: ..., body: json, auth: none }` + `body:json { ... }` + `headers { Authorization: Token {{token}} }` + `docs {}` per `django-bruno.md:158` with incremental `seq` (minimal `1`, full `2`, valid-vip `3`, empty-vip `4`, invalid-vip `5`, invalid `6`)

## 5. Sales confirmation requests

- [x] 5.1 Create `sales/sales_done/post_confirm_one_way.bru` (`POST {{base_url}}/api/sales/done/`, `body: json` with `{sale_stripe_code,client_phone,passengers,details?,arrival_date,arrival_time,arrival_airline,arrival_flight_number}`, `docs {}` with `200 {status:"success",message:"Sale confirmed successfully",data:[]}` + arrival `Transfer` note)
- [x] 5.2 Create `sales/sales_done/post_confirm_round_trip.bru` (same + `departure_date,departure_time,departure_airline,departure_flight_number`, `docs {}` noting departure required only for `Round Trip` per `travels/views.py:207`)
- [x] 5.3 Create `sales/sales_done/post_confirm_invalid.bru` (missing `sale_stripe_code` / unknown `stripe_code` / already-paid, `docs {}` with `400 {status:"error",message:"Sale already paid"}` + `401 {status:"error",message:"Invalid sale data"}` branches)

## 6. Docs fidelity and polish

- [x] 6.1 Audit every `docs {}` for pagination envelope `{count,next,previous,results}` per `core/pagination.py:4` (not `page/total_pages`) with one-item `results`, prices as numbers (example One Way ~80.00 / Round Trip ~160.00), no invented fields, Spanish validation messages (`Este campo es requerido.`, `Clave primaria`), Sales docs include `vip_code: value|null` on `GET` and distinguish `401 Invalid VIP code` (vip) from `400` (other fields) and `401 Invalid token.` (`_auth`)
- [x] 6.2 Verify all `.bru` reference only `{{base_url}}`/`{{token}}`/`{{stripe_code}}` (no hard-coded hosts/credentials), have `meta { name, type:http, seq }` correct (incremental per folder), and `_auth/get_unauthenticated.bru` correctly omits `Authorization` header
- [x] 6.3 Run `openspec status --change bruno-api-collection` to confirm artifact completeness and manual `git status` to ensure `dev.bru` is ignored while `dev.bru.example` is tracked
- [x] 6.4 Verify `_auth/` sorts first in Bruno sidebar (underscore prefix) and opens via `Workspace dropdown → Open workspace` at `bruno/` per `django-bruno.md:292`
