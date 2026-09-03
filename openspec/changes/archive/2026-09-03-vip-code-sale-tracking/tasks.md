## 1. Model & Migration

- [x] 1.1 Add `Sale.vip_code = ForeignKey(VipCode, null=True, blank=True, on_delete=PROTECT, related_name="sales", verbose_name="Código VIP")` to `travels/models.py:136`
- [x] 1.2 Create migration `travels/migrations/0039_sale_vip_code.py` (AddField; depends on `0038_vehicle_passengers`); run `python manage.py migrate` and verify `VipCode` rows intact
- [x] 1.3 Verify `python manage.py makemigrations --dry-run` is clean (no duplicate `0017` conflicts)

## 2. Serializer — optional vip_code + atomic creation

- [x] 2.1 Add optional field `vip_code = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=10, write_only=True)` to `SaleSerializer` (`travels/serializers.py:62`, `source="sale.vip_code"` wiring)
- [x] 2.2 Implement validation: `strip()` + empty→`None`, else `VipCode.objects.get(value__iexact=trimmed, active=True)` else `raise ValidationError({"vip_code":["Invalid or inactive VIP code"]})`; handle `value__iexact` + trim as per `specs/vip-code-tracking`
- [x] 2.3 Wrap `SaleSerializer.create()` (`travels/serializers.py:79`) in `transaction.atomic()` covering `Client.objects.create` + `Pricing.objects.get` + `Sale.objects.create(**sale_data)` so invalid `vip_code` creates zero rows; add `from django.db import transaction`

## 3. Views — 401 branch + GET exposure + no payment bypass

- [x] 3.1 Update `SaleViewSet.post` (`travels/views.py:116-148`): after `serializer.is_valid()` check, if `"vip_code" in serializer.errors` → `Response({"status":"error","message":"Invalid VIP code","errors":serializer.errors}, status=401)`; else keep `400 Invalid sale data`; keep `get_payment_link()` unconditional (remove commented `if not sale.vip_code` line `L123`)
- [x] 3.2 Update `SaleViewSet.get` (`travels/views.py:68-114`) to include `data.vip_code = sale.vip_code.value if sale.vip_code else None` alongside `total/stripe_code/client`
- [x] 3.3 Ensure `SaleDoneView` (`travels/views.py:151`) unchanged; confirm no pricing/discount logic added

## 4. Admin surfacing

- [x] 4.1 Restore `SaleAdmin` (`travels/admin.py:61`): `list_display` add `"vip_code"` (`L67`), `list_filter` add `"vip_code"` (`L80`), `search_fields` add `"vip_code__value"` (`L92`)
- [x] 4.2 Update `TransferAdmin.search_fields` (`travels/admin.py:224`) to re-add `"sale__vip_code__value"`
- [x] 4.3 Keep `VipCodeAdmin` (`travels/admin.py:44`) unchanged; verify `PROTECT` shows `ProtectedError` with in-use codes

## 5. Purge dead separate VIP endpoint (deletion)

- [x] 5.1 Delete commented `VipCodeValidationSerializer` + `validate_vip_code` block (`travels/serializers.py:48-59`)
- [x] 5.2 Delete commented `VipCodeValidationView` block (`travels/views.py:40-60`)
- [x] 5.3 Delete commented route `path("api/validate-vip-code/", ...)` (`project/urls.py:32-36`)
- [x] 5.4 Delete commented `VipCodeValidationViewTestCase` (`travels/tests/test_views.py:342-437`); keep `core/tests_base/test_models.py:75 create_vip_code` helper
- [x] 5.5 Verify `grep -R "validate-vip-code\|VipCodeValidation" --include="*.py" .` returns 0 (expected only `create_vip_code`)

## 6. Test fixtures & Sale lifecycle tests

- [x] 6.1 Restore/extend `create_sale` helper (`core/tests_base/test_models.py:153`) to accept `vip_code: VipCode | None` + `auto_create_vip_code=False` (explicit); ensure `Sale.objects.create` maps `vip_code=vip_code`
- [x] 6.2 Add `SaleViewSetTestCase` tests (`travels/tests/test_views.py:440`): `test_post_with_valid_vip_code` (trim+iexact, 201, `sale.vip_code.value` stored, payment_link present), `test_post_invalid_vip_code_nonexistent` (401 + `validate_no_data_created`), `test_post_invalid_vip_code_inactive` (active=False → 401), `test_post_with_empty_vip_code_treated_as_none` (`""`/`null`/missing → 201 with `sale.vip_code=None`)
- [x] 6.3 Add `GET` assertion for `vip_code` (`test_get_sale_found` `L696` variant with VIP) and `TransferAdmin` search smoke if needed

## 7. Verification & Docs

- [x] 7.1 Run `python manage.py test travels.tests.test_views.SaleViewSetTestCase travels.tests.test_admin -v 2` (and `test_views` wide); confirm no orphan `Client` on `401`
- [x] 7.2 Manual `curl` against `/api/sales/` with no VIP, valid VIP (case/space), inactive, fake — verify `201` vs `401` shapes and Stripe link always present; `GET /api/sales/?stripe_code=` returns `vip_code`
- [x] 7.3 Run `openspec validate vip-code-sale-tracking --strict` and ensure specs coverage (`vip-code-tracking`, `sale-lifecycle`, `admin-sales`)
