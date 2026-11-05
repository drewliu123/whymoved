<div align="center">

<p>
  <img src="docs/assets/pos-logo.svg" width="140" height="140" alt="PoS logo: three interlocking state outlines progressing upward.">
</p>

# PoS · Progression of States

### Beyond Memory: Harnessing Long-Horizon Agents with Explicit Belief States

**An inference-time framework for maintaining an actionable understanding of the current world.**

[arXiv](https://arxiv.org/abs/2610.01415) · [PDF](https://arxiv.org/pdf/2610.01415) · [Project Page](https://luoyu100.github.io/projects/progression-of-states/project/) · [Quick Start](#quick-start) · [Reproduction](docs/reproduction.md) · [Examples](docs/examples.md) · [Citation](#citation)

Yu Luo<sup>1</sup>, Jiamin Jiang<sup>1</sup>, Yimin Zuo<sup>1</sup>, Xidao Wen<sup>2</sup>, Rongchen Gao<sup>1</sup>, Yongqian Sun<sup>1,*</sup>,<br>
Shenglin Zhang<sup>1</sup>, Guiyang Liu<sup>2</sup>, Cheng Zhang<sup>2</sup>, Fang Situ<sup>2</sup>, Qi Zhou<sup>2</sup>, Dan Pei<sup>3</sup>

<sup>1</sup> Nankai University &nbsp; <sup>2</sup> Alibaba Group &nbsp; <sup>3</sup> Tsinghua University<br>
<sup>*</sup> Corresponding author &nbsp; · &nbsp; arXiv preprint, October 2026

</div>

<p align="center">
  <img src="docs/assets/pos-overview.svg" width="1100" alt="PoS maintains a current belief, validates action-driven updates, and diagnoses stalled progress to compose recovery constraints.">
</p>

## Why PoS?

A long interaction history records what happened. An agent still needs to know **what holds now, what remains unresolved, and whether its actions are making progress**. PoS makes these requirements explicit through a continually maintained belief state.

- **Belief modeling.** Represent the task-relevant world as Entities, States, and Relations, together with epistemic gaps (what to learn) and achievement gaps (what to accomplish).
- **Belief-guided interaction.** Select actions using the current belief and an Active Gap; the Belief Sentinel checks candidate updates for internal consistency and support from evidence.
- **Trapping-aware recovery.** Combine gap persistence, progress stagnation, and belief recurrence to detect stalled progress. Diagnose Static, Cycle, or Drift dynamics and compose constraints for the blocked gap type.

PoS runs within a shared ReAct loop and supports **ALFWorld, LOCA-Bench, RCA-100, and ClinDiag**. This release includes full PoS, Raw Trajectory/ReAct, and two PoS ablations. See the [implementation walkthrough](docs/method.md) and [release scope](docs/reproduction.md#release-scope).

## Results at a glance

PoS achieves the highest overall metric among the evaluated methods in all **12 benchmark-backbone settings** reported in paper Table 1. Values below are percentages.

| Backbone | ALFWorld | LOCA-Bench | RCA-100 | ClinDiag |
| :--- | ---: | ---: | ---: | ---: |
| Qwen3.7-Plus | **88.81** | **56.38** | **38.83** | **45.03** |
| Kimi-K3 | **94.03** | **74.29** | **51.46** | **54.80** |
| GLM-5.3 | **97.01** | **70.86** | **49.51** | **52.15** |

ALFWorld and LOCA-Bench use task success; RCA-100 uses joint fault-type and root-cause-entity accuracy; ClinDiag uses diagnosis accuracy. LOCA-Bench's main result pools **525 cases across seven context lengths**, while its default configuration runs 75 cases at 8K.

Relative gains over the strongest evaluated baseline with the same backbone reach **22.68% on ALFWorld** and **37.89% on RCA-100**. Belief maintenance adds inference overhead: in the paper's RCA-100/Qwen3.7-Plus analysis, total tokens are 5.06× Raw Trajectory even though Task Agent tokens decrease. Read the [full result tables and compute tradeoff](docs/results.md) for comparison details.

## Quick Start

### 1. Install

Linux with Python 3.11 is the target platform. Clone the repository and install the core dependencies:

```bash
git clone https://github.com/luoyu100/PoS.git
cd PoS
conda create -n PoS python=3.11
conda activate PoS
pip install -r requirements.txt
```

Install the extras for your chosen benchmark:

| Benchmark | Additional setup |
| :--- | :--- |
| ALFWorld | `pip install -r requirements/alfworld.txt` |
| LOCA-Bench | Python extras, Node.js/npm, and MCP executables: [LOCA setup](benchmarks/LOCA-Bench/README.md) |
| RCA-100 | `pip install -r requirements/rca100.txt` |
| ClinDiag | Core dependencies and the official data archive: [data setup](docs/data.md#clindiag) |

### 2. Configure the model

The supplied configurations use Qwen3.7-Plus through the DashScope OpenAI-compatible API:

```bash
export DASHSCOPE_API_KEY="YOUR_API_KEY"
```

The runtime reads environment variables; it does **not** automatically load `.env` files. Policy, Belief, and Sentinel models have separate configuration blocks. For another backbone or provider, follow [model configuration](docs/reproduction.md#model-roles-and-provider-settings). ClinDiag's environment provider and judge remain fixed independently of the evaluated backbone.

### 3. Run one ALFWorld task

After installing the ALFWorld extras, prepare the valid-unseen data and create a separate one-case configuration:

```bash
python scripts/prepare_benchmarks.py --benchmark alfworld
python - <<'PYCONFIG'
from pathlib import Path
import yaml

config = yaml.safe_load(Path("configs/alfworld/pos.yaml").read_text())
config.update(start_case=0, end_case=1, run_until_complete=False,
              output_run_name="alfworld-pos-smoke")
Path("/tmp/pos-alfworld-smoke.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
PYCONFIG
python main.py --config /tmp/pos-alfworld-smoke.yaml
```

This runs the first task in the benchmark's deterministic ordering and makes model API calls. The output is:

```text
outputs/ALFWorld/ReAct-PoS/alfworld-pos-smoke/
├── summary.json             # Completed cases, success rate, and token usage
├── events.md                # Links to readable case traces
└── cases/case_0000/
    ├── events.jsonl          # Model calls and structured runtime events
    ├── events.md             # Readable action/belief/recovery trace
    └── result.json           # Outcome, exported context, and token usage
```

A completed run writes `result.json` even when the task is unsuccessful. See [examples and log inspection](docs/examples.md) to understand the outcome. For an API-free check of the agent loop, use the [offline validation commands](docs/development.md#offline-checks).

## Run the benchmarks

Prepare the data for your selected benchmark using [these instructions](docs/data.md), then choose its configuration:

| Benchmark | Full PoS command | Configured cases |
| :--- | :--- | :--- |
| ALFWorld | `python main.py --config configs/alfworld/pos.yaml` | 134 valid-unseen tasks |
| LOCA-Bench | `python main.py --config configs/loca/pos.yaml` | 75 tasks at 8K |
| RCA-100 | `python main.py --config configs/rca100/pos.yaml` | 103 cases |
| ClinDiag | `python main.py --config configs/clindiag/pos.yaml` | Fixed 604-case subset |

Each benchmark directory offers the same four configurations:

| Configuration | Method |
| :--- | :--- |
| `pos.yaml` | Full PoS |
| `raw.yaml` | Raw Trajectory / ReAct |
| `pos_no_consistency.yaml` | PoS without consistency validation |
| `pos_no_trapping.yaml` | PoS without trapping diagnosis and recovery |

Case ranges use `[start_case, end_case)`. `skip_existing: true` reuses all completed cases, including unsuccessful ones; `run_until_complete: true` retries crashed workers. Use a distinct output name for incompatible settings. Model calls incur provider costs.

For **paper Table 1, ablations, and context scaling**, follow the [reproduction guide](docs/reproduction.md). It covers all seven LOCA lengths, model roles, action budgets, and result aggregation. The additional ACON, PACE, HiAgent, and LongHorizon-Harness implementations evaluated in the paper are not included in this release.

## Documentation

| Guide | What it covers |
| :--- | :--- |
| [Documentation index](docs/README.md) | Reading routes for running, understanding, and reproducing PoS |
| [Method](docs/method.md) | Belief updates, consistency auditing, health, and recovery |
| [Examples](docs/examples.md) | Belief representation and inspecting your own run traces |
| [Results](docs/results.md) | Paper Table 1, metrics, and inference overhead |
| [Reproduction](docs/reproduction.md) | Evaluation scope, protocols, configurations, and aggregation |
| [Data setup](docs/data.md) | Downloads, local imports, manifests, and evaluator labels |
| [Configuration](docs/configuration.md) | YAML fields, model roles, ablations, and sharding |
| [Validation notes](docs/development.md) | Offline checks and current integration-validation status |

<details>
<summary>Repository layout</summary>

```text
PoS/
├── belief/                 # Belief Manager, Sentinel, progress, and recovery
├── baselines/              # Shared ReAct policy loop
├── contexts/               # Raw trajectory and context-provider interface
├── benchmarks/             # Unified adapter and four benchmark integrations
├── configs/                # Four method configurations per benchmark
├── prompts/                # Policy, Belief, and Sentinel prompts
├── scripts/                # Data preparation and offline validation
├── utils/                  # API retries, logging, and Markdown traces
├── docs/                   # Method, results, examples, and reproduction
├── main.py                 # Experiment entry point
└── requirements.txt        # Core dependencies
```

</details>

## Citation

If PoS is useful in your research, please cite our [paper](https://arxiv.org/abs/2610.01415):

```bibtex
@misc{luo2026memoryharnessinglonghorizonagents,
  title={Beyond Memory: Harnessing Long-Horizon Agents with Explicit Belief States},
  author={Yu Luo and Jiamin Jiang and Yimin Zuo and Xidao Wen and Rongchen Gao and Yongqian Sun and Shenglin Zhang and Guiyang Liu and Cheng Zhang and Fang Situ and Qi Zhou and Dan Pei},
  year={2026},
  eprint={2610.01415},
  archivePrefix={arXiv},
  primaryClass={cs.AI},
  url={https://arxiv.org/abs/2610.01415},
}
```

Machine-readable citation metadata is provided in [CITATION.cff](CITATION.cff).

## License and acknowledgments

PoS code and documentation are released under the [MIT License](LICENSE). Included benchmark components and data retain their own terms; see [third-party notices](THIRD_PARTY_NOTICES.md). We thank the ALFWorld, LOCA-Bench, RCA-100, and ClinDiag authors. This work was carried out during an internship at Alibaba Group.

For questions or reproducible bug reports, please [open an issue](https://github.com/luoyu100/PoS/issues).
