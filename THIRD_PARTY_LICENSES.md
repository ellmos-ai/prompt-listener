# Third-Party Licenses & Runtime Invariants

**Repository:** `ellmos-ai/prompt-listener`
**Stand:** 2026-09-18
**Version:** 1.0.3
**SPDX-License-Identifier:** MIT

---

## 1. Overview & Licensing Policy

`prompt-listener` is released under the **MIT License**. It is engineered as a **purpose-sharp functional unit ("Cell Model")** and a **versioned fork-master template** for prompt and session interaction analysis.

### Core Philosophy: Zero Core Runtime Dependencies
The core toolchain (`prompt_analyzer.py` Stages 0–1, `stage0_agent_event.py`, and `schema/agent_event_v2.py`) relies **exclusively on the Python Standard Library** (stdlib-only). It requires **zero third-party packages** to extract raw session prompts, filter topics, map to `AgentEvent v2` provenance ledgers, and export markdown/JSONL protocols.

---

## 2. Dependency Inventory & License Audit

### 2.1 Core Runtime Dependencies (Stages 0–1 & AgentEvent v2)
| Package | Version | License (SPDX) | Type / Purpose | Copyleft? |
|---|---|---|---|---|
| **Python Standard Library** | $\ge$ 3.10 | PSF-2.0 | Core runtime (json, re, dataclasses, argparse, sys, os) | No |

*Zero external runtime packages are required for standard local extraction and provenance tracking.*

### 2.2 Optional Integration Dependencies (Stages 2–4 Classification)
| Package | Version | License (SPDX) | Type / Purpose | Copyleft? |
|---|---|---|---|---|
| `anthropic` | $\ge$ 0.18.0 (Optional) | MIT | Optional neighbor client for LLM-based categorization | No |

*Classification stages (Stages 2–4) detect optional LLM runners at runtime (e.g. `anthropic` or local `llmauto` runner). If absent, `prompt_analyzer.py` runs safely in `--dry-run` mode without failure.*

### 2.3 Development, Testing & Quality Assurance
| Package | Version | License (SPDX) | Type / Purpose | Copyleft? |
|---|---|---|---|---|
| `pytest` | $\ge$ 8.0.0 | MIT | Test framework & contract assertion | No |
| `ruff` | $\ge$ 0.4.0 | MIT / Apache-2.0 | Static analysis, linting, formatting | No |

---

## 3. Zero-Copyleft & Compatibility Guarantee

1. **Permissive Licensing Only:** Every component and dependency is covered by permissive licenses (MIT, Apache-2.0, PSF-2.0).
2. **Zero Copyleft Contamination:** There are no GPL, AGPL, LGPL, or SSPL dependencies in this codebase.
3. **Unrestricted Commercial & Academic Use:** Both the master template and any declared forks may be utilized in proprietary, enterprise, or open-source research environments without viral licensing obligations.
4. **Declared Divergence Isolation:** When a consuming project requires capabilities that expand the attack or privacy surface (such as live network daemons), it must fork rather than pollute the master. Forked projects maintain their own isolated license and dependency boundaries as declared in `FORKS.md`.

---

## 4. Governance & Runtime Invariants

`prompt-listener` complies with 10 strict technical and architectural invariants:

| Invariant ID | Title | Description | Compliance Status |
|---|---|---|---|
| `INV-LOCAL-01` | **Local-First & Zero Egress** | Stages 0–1 run 100% offline with zero network requests and zero credential requirements. | **VERIFIED** |
| `INV-POSTHOC-02` | **Post-Hoc Analysis Only** | Operates strictly on user-provided static session logs (`.jsonl`). Contains no live hooks, no keystroke loggers, and no daemons. | **VERIFIED** |
| `INV-DEPEND-03` | **Zero Core Dependencies** | Core extraction and `AgentEvent v2` mapping require only the Python standard library. | **VERIFIED** |
| `INV-SCHEMA-04` | **Structured Provenance Ledger** | Full `AgentEvent v2` implementation with 18 sub-ledgers tracking authority, trust boundaries, tool context, and review states. | **VERIFIED** |
| `INV-PIPELINE-05` | **5-Stage Pipeline Separation** | Clear operational boundaries between Raw Extraction (0), Filtering (1), Classification (2), Aggregation (3), and Statistics (4). | **VERIFIED** |
| `INV-TEMPLATE-06` | **Cell & Fork-Master Model** | Operates as a stable master template; divergent requirements fork deliberately with registration in `FORKS.md`. | **VERIFIED** |
| `INV-PRIVACY-07` | **Sensitive Capability Isolation** | Limits are features: features that widen the surveillance or abuse surface are forbidden in master and isolated into forks. | **VERIFIED** |
| `INV-METRICS-08` | **Domain-Specific Archaeology** | Native detection of turning points (`is_turning_point`), prompt type codes (`SP`, `NT`, `NM`, `NS`, `KO`, `BE`, `RA`, `MP`), and word counts. | **VERIFIED** |
| `INV-FORMAT-09` | **Dual Output Architecture** | Generates human-readable Markdown protocols alongside machine-parseable JSONL event streams. | **VERIFIED** |
| `INV-SLA-10` | **Security Policy & 48h SLA** | Formally defined security reporting channel via GitHub Advisories and email with 48h initial response SLA (`SECURITY.md`). | **VERIFIED** |

---

## 5. Execution Privileges (RunAsInvoker)

`prompt-listener` requires **no administrative, root, or elevated privileges**. It runs strictly in user space (`RunAsInvoker`), reading user-specified files and writing output reports to user-permitted paths.
