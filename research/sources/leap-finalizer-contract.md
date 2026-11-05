# Finalizer backend contract

The public skill is an adapter. The probability model itself is supplied by a separate executable named by `AGENTFUTURE_FINALIZER_BIN`.

## Command-line interface

The executable must accept:

```text
--snapshot <path>                  required input JSON
--mode probability|direct|both    required finalization mode
--output <path>                    required output JSON
```

It must exit with status zero only after writing a complete result. It must not perform search, browsing, URL retrieval, or other evidence collection.

## Snapshot fields

The normalizer supplies these top-level fields:

- `task_id`
- `question`
- `freeze_time`
- `metadata`
- `question_family`
- `options`
- `evidence`
- `evidence_count`
- `evidence_bundle_hash`

The backend must treat `evidence` as immutable. It may interpret or aggregate the existing items, but it cannot append or replace them.

## Required result fields

The output JSON must include:

- `mode`
- `finalizer_status`
- `empty_evidence_bundle`
- `evidence_count`
- `evidence_bundle_hash`
- `probability_result` when mode is `probability` or `both`
- `direct_result` when mode is `direct` or `both`
- explicit error or abstention fields when a requested result is unavailable

For `both`, the two results must be derived from the same snapshot and return the same `evidence_bundle_hash`.

## Isolation semantics

Evidence-locked finalization permits model calls needed to interpret the frozen evidence. It prohibits any call whose purpose is to acquire new evidence. A backend should expose enough metadata to audit this distinction.
