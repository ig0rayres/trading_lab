> Part of `panel-triggers`. Return to [SKILL.md](../SKILL.md).

# Trigger writes

## 1. Read

Load the single `control_flags` row, the `market_controls` row for `B3_EQUITY`, `CRYPTO`, or `FOREX`, or the `strategy_states` row for a key that already exists. Starting anchors, when the row is first created, are the cents in `docs/DATABASE.md` section 6. `demo_operation_on` and every `operation_on` start false.

## 2. Reject

Return 404 when `strategy_key` is not already in `strategy_states`. Return 422 when `market` is outside the three literals, when a cent field is below 1, or when the body tries to set a live-trading flag. Ignore any field that is not in the OpenAPI patch schema. `orb` and `mean_reversion` stay out of `paper_limited` and `paper_validated`.

## 3. Write

Update the target row. Insert one `trigger_changes` row with `target_table`, `target_id`, `field_name`, `old_value`, `new_value`, and `changed_at`. Do not update that audit row later. The response body uses the same field names as `docs/db-schema.dbml`.

## 4. After the write

Gate B reads the new row on the next decision. A write does not submit the queued signal that was waiting.
