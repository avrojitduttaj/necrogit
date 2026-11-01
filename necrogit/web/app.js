// NecroGit Interactive Web Application Logic

function switchWbTab(index) {
  const tabs = document.querySelectorAll('.wb-tab');
  const contents = document.querySelectorAll('.wb-content');
  tabs.forEach((tab, i) => tab.classList.toggle('active', i === index));
  contents.forEach((content, i) => content.classList.toggle('active', i === index));

  if (index === 1) {
    const input = document.getElementById('web-term-input');
    if (input) setTimeout(() => input.focus(), 50);
  }
}

function switchOsTab(index) {
  const tabs = document.querySelectorAll('.os-tab');
  const contents = document.querySelectorAll('.os-content');
  tabs.forEach((tab, i) => tab.classList.toggle('active', i === index));
  contents.forEach((content, i) => content.classList.toggle('active', i === index));
}

function copyToClipboard(elementId, btnElement) {
  const text = document.getElementById(elementId).innerText || document.getElementById(elementId).value;
  navigator.clipboard.writeText(text).then(() => {
    const original = btnElement.innerText;
    btnElement.innerText = "✓ Copied!";
    setTimeout(() => btnElement.innerText = original, 2000);
  });
}

function copyCommandText(text, btnElement) {
  navigator.clipboard.writeText(text).then(() => {
    const original = btnElement.innerText;
    btnElement.innerText = "✓ Copied!";
    setTimeout(() => btnElement.innerText = original, 2000);
  });
}

// Simulated AST Bitrot Scanner
const KNOWN_RELICS = {
  "imp": "Removed in Python 3.12; use importlib",
  "pipes": "Removed in Python 3.13; use subprocess or shlex",
  "cgi": "Removed in Python 3.13; use urllib.parse or email",
  "time.clock": "Removed in Python 3.8; use time.perf_counter() or time.process_time()",
  "asyncio.get_event_loop": "Deprecated in modern Python without running loop; prefer asyncio.run()"
};

function runSimulatedAstScan() {
  const code = document.getElementById('workbench-code').value;
  const lines = code.split('\n');
  const findings = [];

  lines.forEach((line, idx) => {
    const lineNum = idx + 1;
    for (const [target, reason] of Object.entries(KNOWN_RELICS)) {
      if (line.includes(target)) {
        findings.push({ line: lineNum, target, reason });
      }
    }
  });

  const findingsBox = document.getElementById('ast-findings');
  if (findings.length === 0) {
    findingsBox.innerHTML = '<div style="color:var(--accent-emerald); font-weight:600;">✨ No bitrot relics detected in current snippet.</div>';
    return;
  }

  let html = '<table class="relic-table"><thead><tr><th>Line</th><th>Relic</th><th>Diagnostic</th></tr></thead><tbody>';
  findings.forEach(f => {
    html += `<tr><td>${f.line}</td><td style="color:var(--accent-gold); font-family:var(--font-mono);">${f.target}</td><td>${f.reason}</td></tr>`;
  });
  html += '</tbody></table>';
  findingsBox.innerHTML = html;
}

function runSimulatedPatch() {
  const spirit = document.getElementById('spirit-select').value;
  let diff = "";

  if (spirit === "ada") {
    diff = `--- a/legacy_artifact.py
+++ b/legacy_artifact.py
@@ -1,18 +1,18 @@
-import imp
-import pipes
-import cgi
-import time
+import importlib
+import subprocess
+import urllib.parse
+import time
 import asyncio

 def execute_stream(command_str):
-    t = pipes.Template()
-    t.append(command_str, "--")
-    return t
+    # Channeling Ada Lovelace: upgraded to subprocess.run
+    return subprocess.run(command_str, shell=True, capture_output=True, text=True)

 def benchmark():
-    t0 = time.clock()
-    return time.clock() - t0
+    t0 = time.perf_counter()
+    return time.perf_counter() - t0

 def init_loop():
-    return asyncio.get_event_loop()
+    return asyncio.new_event_loop()`;
  } else if (spirit === "ken") {
    diff = `--- a/legacy_artifact.py
+++ b/legacy_artifact.py
@@ -1,12 +1,12 @@
-import pipes
-import time
+import subprocess
+import time

 def execute_stream(command_str):
-    t = pipes.Template()
-    return t
+    return subprocess.check_output(command_str, shell=True)

 def benchmark():
-    t0 = time.clock()
-    return time.clock() - t0
+    t0 = time.perf_counter()
+    return time.perf_counter() - t0`;
  } else {
    diff = `--- a/legacy_artifact.py
+++ b/legacy_artifact.py
@@ -1,17 +1,17 @@
-import imp
-import pipes
+import importlib
+import subprocess
 import time
 import asyncio

+# Grace Hopper: Precision timer update and verified subprocess invocation
 def execute_stream(command_str):
-    t = pipes.Template()
-    t.append(command_str, "--")
-    return t
+    return subprocess.run(command_str, capture_output=True, text=True, check=True)

 def benchmark():
-    t0 = time.clock()
-    return time.clock() - t0
+    t0 = time.perf_counter()
+    return time.perf_counter() - t0`;
  }

  document.getElementById('diff-output').textContent = diff;
}

function resetWorkbench() {
  document.getElementById('workbench-code').value = `"""Legacy Python module exhibiting classical bitrot relics."""

import imp
import pipes
import cgi
import time
import asyncio

def execute_stream(command_str):
    t = pipes.Template()
    t.append(command_str, "--")
    return t

def benchmark():
    t0 = time.clock()
    return time.clock() - t0

def init_loop():
    return asyncio.get_event_loop()
`;
  document.getElementById('ast-findings').innerHTML = '<div style="color:var(--text-dim);">Run AST scan to identify deprecated modules...</div>';
  document.getElementById('diff-output').textContent = '--- (Awaiting resurrective patch channeling...) ---';
}

// Terminal Emulator
const termInput = document.getElementById('web-term-input');
const termHistory = document.getElementById('web-term-history');
const termContainer = document.getElementById('term-body');
const cmdHistory = [];
let cmdHistoryIdx = -1;

if (termInput) {
  termInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      const val = termInput.value.trim();
      if (val) {
        cmdHistory.push(val);
        cmdHistoryIdx = cmdHistory.length;
      }
      executeTermCmd(val);
      termInput.value = '';
      if (termContainer) termContainer.scrollTop = termContainer.scrollHeight;
    } else if (e.key === 'ArrowUp') {
      if (cmdHistoryIdx > 0) {
        cmdHistoryIdx--;
        termInput.value = cmdHistory[cmdHistoryIdx];
      }
      e.preventDefault();
    } else if (e.key === 'ArrowDown') {
      if (cmdHistoryIdx < cmdHistory.length - 1) {
        cmdHistoryIdx++;
        termInput.value = cmdHistory[cmdHistoryIdx];
      } else {
        cmdHistoryIdx = cmdHistory.length;
        termInput.value = '';
      }
      e.preventDefault();
    }
  });
}

function printTermLine(text) {
  if (termHistory) {
    termHistory.textContent += text + "\n";
  }
}

function executeTermCmd(raw) {
  printTermLine(`developer@necrogit:~$ ${raw}`);
  const parts = raw.split(' ');
  const cmd = parts[0].toLowerCase();
  const arg = parts.slice(1).join(' ');

  switch (cmd) {
    case 'help':
      printTermLine(`NecroGit CLI Commands:
  summon [path]         Summon maintainer essence from Git commit history
  inspect [dir]         Scan AST for deprecated relics (Python 3.8-3.13 PEP 594)
  patch [file]          Channel a resurrective unified diff patch
  explain [file]        Explain obscure historical design choices
  memory [path]         Inspect Backboard persistent memory dossiers
  serve [--port]        Launch this web documentation server
  export-web [dest]     Export standalone website bundle
  doctor                Run environment and model health diagnostics
  clear                 Clear terminal output screen
  whoami                Display current operator credentials`);
      break;

    case 'summon':
      printTermLine(`🕯️  Casting circle and reading repository runes...
┌─────────────────────────── Séance Manifestation ────────────────────────────┐
│ Dominant Spirit: Ada Lovelace                                               │
│ Last Walked the Earth: 1852-11-27                                           │
│ Total Invocations: 120 commits                                              │
│ Persona Temperament: terse/laconic                                          │
│                                                                             │
│ Sample Historical Invocations:                                              │
│   • Compute Bernoulli numbers in engine cycle #4                            │
│   • Rectify gear backlash in punchcard feeder                               │
└─────────────────────────────────────────────────────────────────────────────┘`);
      break;

    case 'inspect':
      printTermLine(`Performing code archaeology on: ${arg || 'demo/'}...
                          🪦 Identified Bitrot Relics                          
┌──────────────────┬──────┬────────────────────────┬──────────────────────────┐
│ File             │ Line │ Artifact               │ Historical Diagnosis     │
├──────────────────┼──────┼────────────────────────┼──────────────────────────┤
│ ancient_relic.py │ 3    │ imp                    │ Removed in Python 3.12   │
│ ancient_relic.py │ 4    │ pipes                  │ Removed in Python 3.13   │
│ ancient_relic.py │ 5    │ cgi                    │ Removed in Python 3.13   │
│ ancient_relic.py │ 22   │ time.clock             │ Removed in Python 3.8    │
│ ancient_relic.py │ 29   │ asyncio.get_event_loop │ Deprecated in modern Py  │
└──────────────────┴──────┴────────────────────────┴──────────────────────────┘`);
      break;

    case 'patch':
      printTermLine(`Consulting Ada Lovelace via local Gemma 2 9B...
┌────────────────── Ethereal Unified Diff: ${arg || 'ancient_relic.py'} ──────────────────┐
│ --- a/ancient_relic.py                                                      │
│ +++ b/ancient_relic.py                                                      │
│ @@ -3,8 +3,8 @@                                                             │
│ -import imp                                                                 │
│ -import pipes                                                               │
│ +import importlib                                                           │
│ +import subprocess                                                          │
│                                                                             │
│  def execute_shell(cmd):                                                    │
│ -    t = pipes.Template()                                                   │
│ +    return subprocess.run(cmd, shell=True, capture_output=True, text=True) │
└─────────────────────────────────────────────────────────────────────────────┘`);
      break;

    case 'explain':
      printTermLine(`╭────── Historical Design Exegesis: ${arg || 'benchmark_execution'} ──────╮
│ Spirit: Ada Lovelace (1852-11-27)                                            │
│ Rationale: time.clock() provided processor-time precision in early Python    │
│ before monotonic clock standardization in PEP 418. Modernizing to           │
│ time.perf_counter() preserves cycle resolution cleanly.                     │
╰──────────────────────────────────────────────────────────────────────────────╯`);
      break;

    case 'memory':
      printTermLine(`🧠 Backboard Persistent Memory: Active (.necrogit/seance_memory.json)
                      📜 Known Repository Dossiers                       
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Repository ┃ Maintainer Spirit   ┃ Temperament ┃ Relics ┃ Last Action ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━┩
│ necrogit   │ NecroGit Maintainer │ verbose     │ 5      │ patch       │
└────────────┴─────────────────────┴─────────────┴────────┴─────────────┘`);
      break;

    case 'doctor':
      printTermLine(`🩺 NecroGit System Diagnostics:
• Python Environment: 3.12.x (OK)
• Git Telemetry: OK (Git 2.53, repository clean)
• Web Documentation Package: OK (Found web/index.html)
• Sentry Agent Tracing: INACTIVE (Private air-gapped mode)
• Backboard Persistent Memory: AIR-GAPPED (.necrogit/seance_memory.json)
• Probing Local LLM (http://localhost:11434/v1, model: gemma2:9b)...
  └─ Server: ONLINE (http://localhost:11434)
  └─ Model Status: READY (gemma2:9b detected)`);
      break;

    case 'whoami':
      printTermLine(`Ghost in the Machine // Open-Source Repository Medium`);
      break;

    case 'clear':
      if (termHistory) termHistory.textContent = '';
      break;

    case '':
      break;

    default:
      printTermLine(`Unknown command: '${cmd}'. Type 'help' for options.`);
      break;
  }
}
