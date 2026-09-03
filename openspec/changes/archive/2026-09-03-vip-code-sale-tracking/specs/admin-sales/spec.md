## ADDED Requirements

### Requirement: Sale admin surfaces VIP code
`travels/admin.py:61 SaleAdmin` list `list_display`, `list_filter`, and `search_fields` SHALL include `vip_code` (`vip_code`, `vip_code__value`) so VIP-tracked sales are filterable and searchable. `TransferAdmin` search SHALL include `sale__vip_code__value`.

#### Scenario: Filter by VIP
- **WHEN** an admin filters `Sale` by `vip_code`
- **THEN** only sales with that `VipCode` SHALL be shown

#### Scenario: Search by VIP value
- **WHEN** an admin searches `Sale` or `Transfer` by a `VipCode.value` substring
- **THEN** matching sales/transfers SHALL appear

#### Scenario: Sale creation via admin
- **WHEN** a sale is created or edited in admin
- **THEN** `vip_code` SHALL be selectable as an optional FK (null allowed), with `PROTECT` preventing deletion of in-use codes
