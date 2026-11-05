# Manuscript results

[Documentation index](README.md) · [Reproduction guide](reproduction.md)

These tables transcribe Table 1 of the October 2026 manuscript, **Beyond Memory: Harnessing Long-Horizon Agents with Explicit Belief States**. They are reported experimental results, not outputs bundled with this repository. The [Project Page](https://luoyu100.github.io/projects/progression-of-states/project/#results) presents the same comparisons interactively.

## Metrics and evaluation sets

| Benchmark | Reported overall metric | Evaluated cases |
| :--- | :--- | ---: |
| ALFWorld | Task success on valid-unseen | 134 |
| LOCA-Bench | Task success, pooled over seven environment-description lengths | 525 |
| RCA-100 | Joint correctness of fault type and root-cause entity | 103 |
| ClinDiag | Diagnosis accuracy on the fixed balanced subset | 604 |

All table entries below are percentages. Best performance in each benchmark/backbone comparison is bold. A missing or incorrect terminal submission remains in the denominator. The LOCA lengths are 8K, 16K, 32K, 64K, 96K, 128K, and 256K, with 75 cases per length. See the [evaluation protocol](reproduction.md#evaluation-protocol) for budgets and subsets.

## Table 1: Qwen3.7-Plus

| Method | ALFWorld | LOCA-Bench | RCA-100 | ClinDiag |
| :--- | ---: | ---: | ---: | ---: |
| Raw Trajectory | 62.69 | 43.62 | 24.27 | 38.91 |
| ACON | 66.42 | 49.90 | 27.18 | 39.74 |
| PACE | 67.91 | 17.33 | 28.16 | 41.89 |
| HiAgent | 66.42 | 24.57 | 28.16 | 40.07 |
| LongHorizon-Harness | 72.39 | 52.57 | 26.21 | 40.56 |
| **PoS** | **88.81** | **56.38** | **38.83** | **45.03** |
| Without consistency validation | 73.88 | 44.57 | 31.07 | 44.54 |
| Without trapping diagnosis and recovery | 73.13 | 48.19 | 33.98 | 42.38 |

## Table 1: Kimi-K3

| Method | ALFWorld | LOCA-Bench | RCA-100 | ClinDiag |
| :--- | ---: | ---: | ---: | ---: |
| Raw Trajectory | 81.34 | 69.71 | 36.89 | 49.17 |
| ACON | 81.34 | 70.86 | 40.78 | 38.58 |
| PACE | 84.33 | 41.52 | 35.92 | 50.17 |
| HiAgent | 88.81 | 49.52 | 41.75 | 48.51 |
| LongHorizon-Harness | 91.79 | 67.62 | 38.83 | 51.82 |
| **PoS** | **94.03** | **74.29** | **51.46** | **54.80** |
| Without consistency validation | 91.79 | 67.43 | 48.54 | 54.47 |
| Without trapping diagnosis and recovery | 88.81 | 69.52 | 46.60 | 50.83 |

## Table 1: GLM-5.3

| Method | ALFWorld | LOCA-Bench | RCA-100 | ClinDiag |
| :--- | ---: | ---: | ---: | ---: |
| Raw Trajectory | 93.28 | 62.86 | 32.04 | 46.85 |
| ACON | 94.78 | 65.90 | 33.98 | 46.19 |
| PACE | 94.78 | 38.29 | 37.86 | 43.38 |
| HiAgent | 94.78 | 45.90 | 40.78 | 44.87 |
| LongHorizon-Harness | 95.52 | 64.38 | 31.07 | 45.53 |
| **PoS** | **97.01** | **70.86** | **49.51** | **52.15** |
| Without consistency validation | 94.78 | 62.67 | 47.57 | 51.49 |
| Without trapping diagnosis and recovery | 92.54 | 65.71 | 42.72 | 48.51 |

The additional ACON, PACE, HiAgent, and LongHorizon-Harness implementations are not included here. Released configurations cover Raw Trajectory, full PoS, and the two PoS ablations. Refer to manuscript Appendix D.2-D.3 for the other baseline adaptations.

## Interpreting improvements

Compare against the strongest evaluated baseline with the **same backbone**. A percentage-point gain is `PoS - baseline`; a relative gain is `(PoS - baseline) / baseline × 100`.

For Qwen3.7-Plus on ALFWorld, 88.81 versus 72.39 is **16.42 percentage points**, or **22.68% relative**. For Qwen3.7-Plus on RCA-100, 38.83 versus 28.16 is **10.67 percentage points**, or **37.89% relative**. Relative percentages are not percentage-point differences.

## Inference overhead

Manuscript Table 2 reports the following RCA-100/Qwen3.7-Plus comparison. Tokens are mean input plus output tokens per episode across 103 cases; `K` denotes thousands.

| Measurement | Raw Trajectory | PoS |
| :--- | ---: | ---: |
| Joint accuracy (%) | 24.27 | 38.83 |
| Task Agent tokens (K) | 355.70 | 281.20 |
| Total method tokens (K) | 355.70 | 1,800.13 |

PoS uses about **20.9% fewer Task Agent tokens** but **5.06× total method tokens** in this comparison. Belief construction and Sentinel calls contribute to the total. These are token counts, not dollar costs or universal efficiency guarantees; actual API cost depends on the selected provider and model.

The runtime records method token usage in `summary.json`. ClinDiag separately records environment-provider and judge token usage under `benchmark_info.token_usage`; see [aggregation](reproduction.md#read-and-aggregate-results) before comparing totals.

## Comparing a new run

Use the same subset, action budget, model roles, decoding parameters, and aggregation protocol. The manuscript used live API models without fixed snapshots, so a later run may differ even with the same requested model name. Preserve the exact YAML, repository commit, run date, and provider model identifiers alongside your outputs. Current validation coverage is documented in [Validation notes](development.md).
