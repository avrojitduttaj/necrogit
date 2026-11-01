# 🕯️ NecroGit: The Repository Medium
*A Hacktoberfest 2026 "Ghost in the Machine" Open-Source AI Project*

NecroGit resurrects abandoned repositories and resolves bitrot by mining Git commit history, building a stylistic persona of the original maintainer, and utilizing offline open-weight models to draft faithful modernized patches.

---

## ⚡ Why Open Innovation Matters
- **100% Offline & Private:** Code archaeology operates completely air-gapped using local weights (`gemma2:9b` via Ollama). Sensitive code never leaves your workstation.
- **Style Preservation:** Closed commercial APIs enforce homogenized writing styles. NecroGit passes custom AST findings and maintainer telemetry to open-weight models, preserving vintage naming and variable conventions.
- **Durable:** Immune to API deprecations, subscription tiers, or remote service shutdowns.

## 🚀 Quickstart
```bash
# 1. Install dependencies
pip install -e .

# 2. Ensure your local open-weight model is running
ollama run gemma2:9b

# 3. Commune with a repository
necrogit summon .

# 4. Detect bitrot
necrogit inspect .

# 5. Channel the maintainer for a patch
necrogit patch path/to/legacy_file.py