# 🕯️ NecroGit: The Repository Medium
*Commune with dead code and resurrect abandoned repositories with local AI.*
**Hacktoberfest 2026 — Ghost in the Machine**

---

NecroGit is an offline code archaeology medium and repository necromancer. It communes with abandoned software by mining historical Git commit telemetry to recreate the persona and coding habits of long-gone maintainers, detects bitrot and deprecated Python APIs through AST analysis, and channels local open-weight LLMs (Gemma 2, Llama 3 via Ollama) to draft authentic, style-preserving resurrective patches.

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
                              │ (Local Open-Weight LLM)│
                              │  Gemma 2 / Llama 3     │
                              └────────────┬───────────┘
                                           │
                                           ▼
                              ┌────────────────────────┐
                              │ Resurrective Diff File │
                              │     (.patch format)    │
                              └────────────────────────┘
```

1. **AST Code Archaeology (`necrogit.core.archaeology`):**
   Parses Python files into Abstract Syntax Trees to identify obsolete standard library modules (e.g., Python 3.12/3.13 removals such as `imp`, `pipes`, `cgi`, `cgitb`, `crypt`, `telnetlib`, `xdrlib`), deprecated APIs (`time.clock`, `asyncio.get_event_loop`), and structural syntax decay.

2. **Git Persona Mining (`necrogit.core.persona`):**
   Traverses repository commit history to divine the primary author's name, commit volume, stylistic temperament (`laconic`, `balanced`, `verbose`), active era, and authentic historical commit messages.

3. **Offline Séance Engine (`necrogit.core.engine`):**
   Injects the maintainer's stylistic essence and AST findings into a targeted prompt sent to an air-gapped local model via OpenAI-compatible endpoints (`http://localhost:11434/v1`). Models produce unified diffs preserving legacy casing and comment conventions.

4. **Sentry Agent Tracing (`necrogit.telemetry`):**
   Transparent span monitoring for every stage of the séance (archaeology scanning, history mining, LLM channeling) using `sentry-sdk>=2.0.0`.

---

## ⚡ Why Open Innovation Matters

- **100% Offline & Air-Gapped:** Sensitive or proprietary legacy code never leaves your workstation. No closed APIs, no remote data leaks.
- **Style Preservation:** Commercial LLMs force generic modern styles. NecroGit channels the original maintainer's cadence and conventions.
- **Durable & Resilient:** Immune to cloud API deprecations, rate limits, price surges, or subscription lockouts.

---

## 🚀 Installation & Setup

### Prerequisites
- Python >= 3.10
- Git
- Local LLM runner (e.g., [Ollama](https://ollama.com) with `gemma2:9b` or `llama3.1:8b`)

```bash
# Clone the repository
git clone https://github.com/your-username/necrogit.git
cd necrogit

# Install in editable mode
pip install -e .
```

---

## 📖 CLI Usage

### 1. Summon the Maintainer's Spirit
Analyze Git history to manifest the maintainer's spirit:
```bash
necrogit summon .
```
```
🕯️  Casting circle and reading repository runes...
┌─────────────────────────── Séance Manifestation ────────────────────────────┐
│ Dominant Spirit: Ada Lovelace                                               │
│ Last Walked the Earth: 1852-11-27                                           │
│ Total Invocations: 120 commits                                              │
│ Persona Temperament: terse/laconic                                          │
│                                                                             │
│ Sample Historical Invocations:                                              │
│   • Compute Bernoulli numbers in engine cycle #4                            │
│   • Rectify gear backlash in punchcard feeder                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Inspect Repository for Bitrot Relics
Scan your codebase with AST archaeology:
```bash
necrogit inspect demo/
```
```
Performing code archaeology on: demo...
                          🪦 Identified Bitrot Relics                          
┌──────────────────┬──────┬────────────────────────┬──────────────────────────┐
│ File             │ Line │ Artifact               │ Historical Diagnosis     │
├──────────────────┼──────┼────────────────────────┼──────────────────────────┤
│ ancient_relic.py │ 3    │ imp                    │ Removed in Python 3.12;  │
│                  │      │                        │ use importlib            │
│ ancient_relic.py │ 4    │ pipes                  │ Removed in Python 3.13;  │
│                  │      │                        │ use subprocess or shlex  │
│ ancient_relic.py │ 5    │ cgi                    │ Removed in Python 3.13;  │
│                  │      │                        │ use urllib.parse or      │
│                  │      │                        │ email                    │
│ ancient_relic.py │ 22   │ time.clock             │ Removed in Python 3.8;   │
│                  │      │                        │ use time.perf_counter()  │
│ ancient_relic.py │ 29   │ asyncio.get_event_loop │ Deprecated in modern     │
│                  │      │                        │ Python without running   │
│                  │      │                        │ loop; prefer             │
│                  │      │                        │ asyncio.run()            │
└──────────────────┴──────┴────────────────────────┴──────────────────────────┘
```

### 3. Channel a Resurrective Patch
Channel the maintainer to draft an in-character unified diff:
```bash
# Draft diff to terminal
necrogit patch demo/ancient_relic.py --model gemma2:9b

# Save patch file directly
necrogit patch demo/ancient_relic.py --model gemma2:9b --apply
```

---

## 🧪 Testing

Run the automated test suite with `pytest`:
```bash
pytest -v
```

All 8 comprehensive tests cover:
- AST archaeology detection of deprecated modules and attributes (`imp`, `pipes`, `cgi`, `time.clock`, `asyncio.get_event_loop`)
- Syntax error and syntax rot resilience
- Non-git directory fallbacks and graceful degradation
- Maintainer persona extraction from active git commit history
- SeanceEngine prompt payload and system message styling
- Offline model connection error recovery
- CLI `summon` and `inspect` end-to-end command runner flows

---

## 🕯️ Hacktoberfest 2026

Part of the **Ghost in the Machine** theme:
Bringing dead open-source repositories back to life with ethical, private, and local open-weight AI.
