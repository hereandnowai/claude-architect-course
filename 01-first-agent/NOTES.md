# Notes: Claude Certified Architect course, Episode 1 of 10 (your first AI agent)

Internal notes for building the video: versions, exact paths and tree, decisions, sources. All runs: `output.txt`.

## Versions used (26 Nov 2026)
| Tool | Version |
|---|---|
| macOS / machine | 26.7.3, Apple M4 Max, 128 GB |
| uv | 0.11.12 |
| Python | CPython 3.12.12 (`uv init --python 3.12`; without `--python`, uv picked 3.13 on this Mac) |
| anthropic (PyPI) | 2.14.0 (latest on PyPI, requires Python >= 3.10) |
| claude-agent-sdk (PyPI) | 0.2.189 (latest on PyPI, requires Python >= 3.10); bundles Claude Code CLI 2.1.332 |
| Claude Code (installed) | 2.1.331, signed in with a Claude Max plan; no ANTHROPIC_API_KEY anywhere |
| Ollama / model | 0.32.13 / `qwen3.5:4b` (3.3 GB download) |
| Model used by the SDK run | `claude-opus-5-5` (plan default, from the init message) |

## Exact steps and paths (what the viewer sees)
```
~/Desktop/claude-architect-course/          ← File → Open Folder in VS Code
├── .git/                (made by uv init; hidden in VS Code's Explorer by default)
├── .venv/               (made by uv add)
├── .gitignore
├── .python-version      (3.12)
├── README.md            (empty, made by uv init)
├── main.py              (hello world from uv init; step 4 runs it once as a check)
├── pyproject.toml       (dependencies: anthropic>=2.14.0, claude-agent-sdk>=0.2.189; requires-python >=3.12)
├── uv.lock
├── maple_data.py        ← step 6 (first new file)
├── loop_by_hand.py      ← step 7 (second new file)
└── agent_sdk.py         ← step 10 (third new file)
```
Commands, in order: `uv init --python 3.12` → `uv add anthropic claude-agent-sdk` → `uv run main.py` →
(write maple_data.py, loop_by_hand.py) → `uv run loop_by_hand.py` → `uv run loop_by_hand.py "Hi, this is Liam…"` →
(write agent_sdk.py) → `uv run agent_sdk.py`.

This repo folder (`01-first-agent/`) holds the same files plus this handout (`README.md` replaces uv's empty one),
`NOTES.md`, `output.txt`, and `teaser/` (the episode 2 preview; not a viewer step in episode 1).

Line counts: maple_data.py 43, loop_by_hand.py 52 (the loop function itself, `ask`, is 27 lines), agent_sdk.py 52.

## Decisions and deviations from the plan
1. **`uv init --python 3.12`** instead of bare `uv init`: bare `uv init` picks whatever Python it finds (3.13 here), so
   the pin makes every viewer's project match ours. uv downloads Python 3.12 if it is missing (so the Python installer
   is optional; its official link stays in the description).
2. **`thinking={"type": "disabled"}` in loop_by_hand.py, labelled "Ollama only".** qwen3.5:4b thinks by default
   through Ollama's Anthropic API; with max_tokens 1024, 3 of 12 test runs never got past thinking (stop_reason
   `max_tokens`, ~25 s). With thinking off: 0.6–1.6 s per turn and every run correct. Current Claude models reject
   `{"type": "disabled"}` (e.g. Claude Opus 5.5 returns a 400; it decides on thinking itself), so the script says to
   leave the line out for Claude. Same idea as `think=false` in Spring AI episode 1.
3. **Hand loop length:** 52 lines in the file, 27 in `ask()`. Say "about fifty lines" / "the loop itself is about
   twenty-five lines", not "30 lines".
4. **`setting_sources=[]` and `tools=[]` in agent_sdk.py.** By default the SDK loads all Claude Code settings files
   (user + project, which can include hooks and CLAUDE.md) and gives Claude the built-in tools. For a first agent we
   want a clean, predictable one: no settings files, no built-in tools, only our tool. Both are documented options.
5. **The SDK names our tool `mcp__maple__get_order`** (server key `maple` + tool `get_order`); that exact name goes in
   `allowed_tools`. The output line shows this full name.
6. **Teaser numbers are from the local model** (qwen3.5:4b), not Claude. Say so ("our small local model").
   The SDK was not run with the lazy tool (to save plan usage).
7. **`tool_choice`:** Ollama's Anthropic API does not support `tool_choice` (docs), so this episode doesn't use it;
   episode 2 explains it from the docs (and on current Claude models, forced `tool_choice` "any"/"tool" returns a 400
   on Claude Opus 5.5 / Sonnet 5.5 and newer; `auto` still works).
8. **Exam guide vs product today:** the guide calls the subagent tool "Task"; Claude Code renamed it **"Agent"** in
   version 2.1.63 ("Existing `Task(...)` references … still work as aliases", code.claude.com/docs/en/sub-agents).
   `fork_session` exists in the Python SDK (`ClaudeAgentOptions(resume=…, fork_session=True)`). Both for later episodes.
9. **Plans:** "Claude Code requires a Pro, Max, Ultra, Team, Enterprise, or Console account. The free claude.ai plan does
   not include Claude Code access." (code.claude.com/docs/en/setup). The script says "a paid Claude plan, like Pro or Max".
10. **CPU-only numbers** come from a test-only model copy (`num_gpu 0`, 4,096 context) on a fast M4 Max processor;
    older laptops will be slower. Say "on our test machine's processor alone".

## Ollama notes
- `ollama ps` on this Mac showed `qwen3.5:4b` at 12 GB, 100% GPU, context 262144: Ollama picks a large context on a
  machine with a lot of memory. On a normal laptop it picks a smaller one; our CPU test used 4,096 and worked.
- The anthropic SDK needs `api_key` but Ollama ignores it ("required but ignored", docs.ollama.com/api/anthropic-compatibility).
- Not supported by Ollama's Anthropic API (docs): `tool_choice`, token counting, prompt caching, batches, citations,
  PDF blocks, `metadata`, server-sent `error` events.

## Windows
Not run on Windows (no Windows machine); standard equivalents from the official install pages:
| macOS / Linux | Windows (PowerShell) |
|---|---|
| `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| `curl -fsSL https://claude.ai/install.sh \| bash` | `irm https://claude.ai/install.ps1 \| iex` |
| Ollama installer from ollama.com/download | the same (OllamaSetup.exe) or `irm https://ollama.com/install.ps1 \| iex` |
| `uv init --python 3.12`, `uv add …`, `uv run …` | identical |

## Sources (docs pages to screenshot)
- Tool calls loop: https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls
- Stop reasons: https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
- Defining tools: https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
- Agent SDK Python: https://code.claude.com/docs/en/agent-sdk/python
- Custom tools: https://code.claude.com/docs/en/agent-sdk/custom-tools
- Sessions (fork): https://code.claude.com/docs/en/agent-sdk/sessions
- Subagents (Task → Agent): https://code.claude.com/docs/en/sub-agents
- Plans for Claude Code: https://code.claude.com/docs/en/setup
- Agent SDK with a Claude plan: https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
- API key rule for products: https://code.claude.com/docs/en/legal-and-compliance
- Ollama Anthropic compatibility: https://docs.ollama.com/api/anthropic-compatibility
- Who can take the exam: https://anthropic-partners.skilljar.com/page/faq-certifications,
  https://claude.com/blog/four-role-based-claude-certifications, https://www.anthropic.com/news/claude-partner-network,
  https://www.pearsonvue.com/us/en/anthropic.html
