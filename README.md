# 🕯️ NecroGit: The Repository Medium
*Commune with dead code and resurrect abandoned repositories with local AI.*
**Hacktoberfest 2026 — Ghost in the Machine**

---

NecroGit is an offline code archaeology medium and repository necromancer. When pointed at an abandoned legacy repository or obsolete dependency, it traces deprecated APIs, mines historical Git commit telemetry to recreate the persona and coding habits of long-gone maintainers, channels local open-weight LLMs (Gemma 2, Llama 3.2 via Ollama/vLLM) to auto-patch bitrot, and unravels obscure historical design choices.

---

## 🎯 Partner Category Targets

### 1. 💎 Best Use of Gemma
- **Offline Open-Weight Code Reasoning:** Powered by **Google Gemma 2** (`gemma2:9b`, `gemma2:2b`, `gemma2:27b`) running locally through Ollama or vLLM.
- **Architectural Exegesis & Style Preservation:** Gemma 2's high instruction-following fidelity is leveraged to digest AST bitrot findings and channel the maintainer's vintage coding style (casing, comment density, naming conventions) without cloud model homogenization.
- **100% Private & Air-Gapped:** Sensitive source trees, legacy industrial code, and unreleased repositories never leave your workstation. Zero API fees, zero telemetry leaks.

### 2. 🧠 Best Use of Backboard (R-CLI)
- **Persistent Agentic Memory:** Integrates state management and persistent memory via Backboard (`backboard.io` & the `R-CLI`).
- **Dossier Synchronization:** Preserves maintainer essences, code archaeology findings, and séance history across sessions in `.necrogit/seance_memory.json` (air-gapped) and seamlessly syncs to Backboard state when `BACKBOARD_API_KEY` or `backboard login` is active.
- **Run-to-Run Context:** Future developer sessions immediately remember who the maintainer was, which relics were identified, and past resurrective actions.

### 3. 📡 Best Use of Sentry Agent Tracing
- **Step-by-Step Code Archaeology Tracing:** Instrumented with `sentry-sdk>=2.0.0` to capture granular Agent Tracing spans for each stage of the resurrection pipeline.
- **Traced Spans & Breadcrumbs:**
  - `necrogit.archaeology`: AST tree traversal, syntax rot classification, and file inspections.
  - `necrogit.persona`: Git commit graph mining, author frequency analysis, and cadence divining.
  - `necrogit.llm`: Local inference spans tagged with `gen_ai.system: ollama` and `gen_ai.request.model`.
  - `necrogit.backboard`: Memory persistence and state synchronization spans.
- **Agent Context & Diagnostics:** Enriches Sentry trace scopes with maintainer persona metadata (`maintainer_persona`) and agent reasoning breadcrumbs.

---

## 🔮 Core Architecture

```
                       ┌────────────────────────────────────────┐
                       │           Abandoned Repository         │
                       └───────────────────┬────────────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       ┌────────────────────────┐                    ┌────────────────────────┐
       │   MaintainerMedium     │                    │   ArchaeologyScanner   │
       │  (Git History Mining)  │                    │   (Python AST Visitor) │
       └────────────┬───────────┘                    └────────────┬───────────┘
                    │ Maintainer Persona                          │ Bitrot Relics &
                    │ (cadence, brevity, logs)                    │ Deprecations
                    └──────────────────────┬──────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────┐
                              │      SeanceEngine      │
                              │  Google Gemma 2 9B     │
                              │   (Local / Offline)    │
                              └────────────┬───────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       ┌────────────────────────┐                    ┌────────────────────────┐
       │ Resurrective Diff File │                    │    Backboard Memory    │
       │     (.patch format)    │                    │ (Persistent Dossier &  │
       │                        │                    │  Sentry Span Tracing)  │
       └────────────────────────┘                    └────────────────────────┘
```

---

## ⚡ Why Open Innovation Matters

- **100% Offline & Private:** Code archaeology operates completely air-gapped using local weights (`gemma2:9b` via Ollama). Proprietary or sensitive legacy code never leaves your workstation.
- **Style Preservation:** Closed commercial APIs enforce homogenized writing styles. NecroGit passes custom AST findings and maintainer telemetry to open-weight models, preserving vintage naming and variable conventions.
- **Durable & Resilient:** Immune to cloud API deprecations, rate limits, subscription tiers, or remote service shutdowns.

---

## 🚀 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/necrogit.git
cd necrogit

# Install in editable mode
pip install -e .

# (Optional) Set up Sentry Agent Tracing and Backboard Memory
export SENTRY_DSN="https://your-dsn@sentry.io/project"
export BACKBOARD_API_KEY="your-backboard-key"
```

Ensure your local open-weight model is running:
```bash
ollama run gemma2:9b
```

---

## 📖 CLI Commands

### 1. `necrogit summon [REPO_PATH]`
Summon and interview the maintainer's spirit from Git history:
```bash
necrogit summon .
```
```
🕯️  Casting circle and reading repository runes...
╭──────────────────────────── Séance Manifestation ────────────────────────────╮
│ Dominant Spirit: Ada Lovelace                                                │
│ Last Walked the Earth: 1852-11-27                                            │
│ Total Invocations: 120 commits                                               │
│ Persona Temperament: terse/laconic                                           │
│                                                                              │
│ Sample Historical Invocations:                                               │
│   • Compute Bernoulli numbers in engine cycle #4                             │
│   • Rectify gear backlash in punchcard feeder                                │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 2. `necrogit inspect [TARGET_DIR]`
Scan local files for bitrot, deprecated modules (Python 3.8–3.13 PEP 594 removals), and breaking syntax:
```bash
necrogit inspect demo/
```
```
Performing code archaeology on: demo...
                          🪦 Identified Bitrot Relics                          
┌──────────────────┬──────┬────────────────────────┬──────────────────────────┐
│ File             │ Line │ Artifact               │ Historical Diagnosis     │
├──────────────────┼──────┼────────────────────────┼──────────────────────────┤
│ ancient_relic.py │ 3    │ imp                    │ Removed in Python 3.12   │
│ ancient_relic.py │ 4    │ pipes                  │ Removed in Python 3.13   │
│ ancient_relic.py │ 5    │ cgi                    │ Removed in Python 3.13   │
│ ancient_relic.py │ 22   │ time.clock             │ Removed in Python 3.8    │
│ ancient_relic.py │ 29   │ asyncio.get_event_loop │ Deprecated in modern Py  │
└──────────────────┴──────┴────────────────────────┴──────────────────────────┘
```

### 3. `necrogit explain <FILE_PATH> [--symbol NAME]`
Channel the maintainer to explain obscure historical design choices:
```bash
necrogit explain demo/ancient_relic.py --symbol benchmark_execution --model gemma2:9b
```

### 4. `necrogit patch <FILE_PATH> [--apply]`
Channel the maintainer to draft an in-style resurrective patch:
```bash
necrogit patch demo/ancient_relic.py --model gemma2:9b --apply
```

### 5. `necrogit memory`
Inspect persistent repository dossiers and Backboard memory synchronization status:
```bash
necrogit memory
```
```
🧠 Backboard Persistent Memory: Air-Gapped / Local Mode (.necrogit/seance_memory.json)
                      📜 Known Repository Dossiers                       
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Repository ┃ Maintainer Spirit   ┃ Temperament ┃ Relics ┃ Last Action ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━┩
│ necrogit   │ NecroGit Maintainer │ verbose     │ 5      │ patch       │
└────────────┴─────────────────────┴─────────────┴────────┴─────────────┘
```

---

## 🧪 Automated Test Suite

Run all unit and integration tests:
```bash
pytest -v
```

All 11 tests pass with 100% code integrity:
- `test_archaeology_detects_deprecated_imports`
- `test_persona_non_git_directory`
- `test_engine_prompt_payload_construction`
- `test_engine_explain_design_construction`
- `test_archaeology_detects_syntax_rot`
- `test_archaeology_inspect_directory`
- `test_persona_git_repo`
- `test_engine_connect_error`
- `test_backboard_memory_local_persistence`
- `test_telemetry_breadcrumbs_and_context`
- `test_cli_summon_inspect_explain_and_memory`

---

## 🕯️ Hacktoberfest 2026

Part of the **Ghost in the Machine** theme: Resurrecting abandoned code with ethical, air-gapped, open-weight AI.
