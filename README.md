# 🕯️ NecroGit: The Repository Medium
*Commune with dead code and resurrect abandoned repositories with local AI.*
**Hacktoberfest 2026 — Ghost in the Machine**

---

NecroGit is an offline code archaeology medium and repository necromancer. When pointed at an abandoned legacy repository or obsolete dependency, it traces deprecated APIs, mines historical Git commit telemetry to recreate the persona and coding habits of long-gone maintainers, channels local open-weight LLMs (Gemma 2, Llama 3 via Ollama/vLLM) to auto-patch bitrot, and unravels obscure historical design choices.

It includes a self-contained web workbench, an interactive CRT terminal emulator, and static export capabilities for hosting documentation anywhere.

---

## 🎯 Partner Category Targets

### 1. 💎 Best Use of Gemma
- **Offline Open-Weight Code Reasoning:** Powered by **Google Gemma 2** (`gemma2:9b`, `gemma2:2b`, `gemma2:27b`) running locally through Ollama or vLLM.
- **Architectural Exegesis & Style Preservation:** Gemma 2's instruction-following fidelity is leveraged to digest AST bitrot findings and channel the maintainer's vintage coding style (casing, comment density, naming conventions) without cloud model homogenization.
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

## 🚀 Installation & Arbitrary Repository Usage

NecroGit is primarily an **installable local developer CLI**. You can install it once in your Python environment and execute it against **any arbitrary cloned repository** on your workstation.

### Option A: Install Directly into Your Python Environment (Recommended)

```powershell
# Install directly from GitHub:
python -m pip install "git+https://github.com/avrojitduttaj/necrogit.git"

# Or install from PyPI registry:
python -m pip install necrogit

# Verify system diagnostics:
necrogit doctor
```

### Option B: Clone and Install in Editable Mode (Development)

#### Linux / macOS
```bash
git clone https://github.com/avrojitduttaj/necrogit.git
cd necrogit
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
necrogit doctor
```

#### Windows (PowerShell)
```powershell
git clone https://github.com/avrojitduttaj/necrogit.git
cd necrogit
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
necrogit doctor
```

---

## 💻 Workflow: Resurrect Any Cloned Project

Open your terminal (e.g. VS Code integrated terminal), clone any legacy project, and run NecroGit directly inside it:

```powershell
# 1. Clone any target repository
git clone https://github.com/someuser/legacy-project.git
cd legacy-project

# 2. Inspect bitrot (analyzes target project, zero pollution)
necrogit inspect .

# 3. Channel the original maintainer's essence from git commit logs
necrogit summon .

# 4. Synthesize a resurrective patch (requires local Ollama)
necrogit patch src/legacy_worker.py --apply

# 5. Explain obscure historical architecture decisions
necrogit explain src/legacy_worker.py --symbol run_pipeline

# 6. Review persistent dossiers
necrogit memory
```

---

## 📖 CLI Commands Reference

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
Scan local files for bitrot, deprecated modules (Python 3.8–3.13 PEP 594 removals: `imp`, `pipes`, `cgi`, `time.clock`), and breaking syntax:
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

### 3. `necrogit patch <FILE_PATH> [--apply] [--model] [--base-url]`
Channel the maintainer to draft an in-style resurrective patch:
```bash
# Preview diff in terminal
necrogit patch demo/ancient_relic.py --model gemma2:9b

# Apply diff directly to a .patch file
necrogit patch demo/ancient_relic.py --model gemma2:9b --apply
```

### 4. `necrogit explain <FILE_PATH> [--symbol NAME] [--model] [--base-url]`
Channel the maintainer to explain obscure historical design choices:
```bash
necrogit explain demo/ancient_relic.py --symbol benchmark_execution --model gemma2:9b
```

### 5. `necrogit memory [REPO_PATH] [--clear]`
Inspect persistent repository dossiers and Backboard memory synchronization status:
```bash
# View all known repository dossiers
necrogit memory

# Clear recorded memory
necrogit memory --clear
```

### 6. `necrogit serve [--port 8000]`
Start local HTTP server and automatically launch the interactive CRT web terminal:
```bash
necrogit serve --port 8000
```

### 7. `necrogit export-web [DESTINATION] [--zip/--no-zip]`
Export the self-contained production website and generated `necrogit-site.zip` bundle to any directory:
```bash
necrogit export-web ./necrogit-site

# Preview exported site locally:
cd ./necrogit-site
python -m http.server 8080
```

### 8. `necrogit doctor`
Inspect installation integrity, Git availability, and local AI model connectivity:
```bash
necrogit doctor
```
```
╭────────────────────────────────╮
│ 🩺 NecroGit System Diagnostics │
╰────────────────────────────────╯
• Python Environment: 3.12.13 (OK)
• Git Telemetry: OK (Git 3.2.1, repo: necrogit)
• Web Documentation Package: OK (Found web/index.html)
• Sentry Agent Tracing: INACTIVE (SENTRY_DSN not set - running fully private)
• Backboard Persistent Memory: AIR-GAPPED (Local .necrogit/seance_memory.json)
• Probing Local LLM (http://localhost:11434/v1, target model: gemma2:9b)...
  └─ Server: ONLINE (http://localhost:11434)
  └─ Model Status: READY (gemma2:9b detected)
```

---

## 🛠️ Troubleshooting & Local Ollama Setup

### Starting Ollama
Ensure Ollama is installed and running:
```bash
# 1. Start Ollama server
ollama serve

# 2. Download Gemma 2 model weights
ollama pull gemma2:9b

# 3. Verify connection with NecroGit
necrogit doctor
```

### Resolving HTTP 404 Errors
If you see an endpoint error, verify that your Ollama server is updated to `>= 0.1.24`. NecroGit automatically queries `/v1/chat/completions` and transparently falls back to native Ollama `/api/chat`. You can also explicitly specify your endpoint:
```bash
necrogit patch demo/ancient_relic.py --base-url http://localhost:11434/v1
```

---

## 🧪 Automated Test Suite

Run all unit and integration tests:
```bash
pytest -v
```

All 21 comprehensive tests verify:
- AST archaeology detection of deprecated modules (`imp`, `pipes`, `cgi`, `time.clock`, `asyncio.get_event_loop`)
- Syntax error and syntax rot resilience
- Non-git directory fallbacks and graceful degradation
- Maintainer persona extraction from active git commit history
- SeanceEngine prompt payload construction & design exegesis
- Ollama connection failure handling, HTTP 404 differentiation, model-absent detection, native Ollama fallback, malformed responses, and timeouts
- Backboard persistent memory (local storage, dossier retrieval, and memory clearing)
- Sentry telemetry breadcrumb and context instrumentation
- CLI command executions (`summon`, `inspect`, `explain`, `memory`, `export-web`, `doctor`)
- Web asset export to directories containing spaces and deterministic ZIP bundling

---

## 🕯️ Hacktoberfest 2026

Part of the **Ghost in the Machine** theme: Resurrecting abandoned code with ethical, air-gapped, open-weight AI.
