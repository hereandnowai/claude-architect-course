# Notes: Claude Certified Architect course, Episode 2 of 10 (tools the model picks correctly)

Internal notes for building the video: versions, exact paths and tree, decisions, sources. All runs: `output.txt`.

## Versions used (26 Nov 2026): unchanged from episode 1
| Tool | Version |
|---|---|
| macOS / machine | 26.7.3, Apple M4 Max, 128 GB |
| uv / Python | 0.11.12 / CPython 3.12.12 |
| anthropic / claude-agent-sdk | 2.14.0 / 0.2.189 (bundles Claude Code CLI 2.1.332) |
| Claude Code (installed) | 2.1.331, Claude Max plan login, no ANTHROPIC_API_KEY |
| Ollama / model | 0.32.13 / `qwen3.5:4b` |
| Model used by the SDK runs | `claude-opus-5-5` (plan default, from the init message) |

No new installs and no new packages: `pyproject.toml` and `uv.lock` are episode 1's, unchanged.

## Exact steps and paths (what the viewer sees)
```
~/Desktop/claude-architect-course/          ← File → Open Folder (the same folder as episode 1)
├── .venv/ .gitignore .python-version README.md uv.lock pyproject.toml main.py   (from episode 1, unchanged)
├── maple_data.py        ← step 3 (EDITED: customers, prices, tracking numbers, parcels, 3 new functions;
│                                   the get_order tool definition moves out to maple_tools.py)
├── maple_tools.py       ← step 4 (NEW: the four tool definitions + run_tool)
├── loop_by_hand.py      ← step 5 (EDITED: imports from maple_tools, tools=TOOLS, prints each tool_result)
├── tool_test.py         ← step 6 (NEW, typed)
├── lazy_tools.py        ← step 6 (NEW, copied from GitHub: the lazy "before" definitions)
├── extra_tools.py       ← step 6 (NEW, copied from GitHub: 14 extra tools for the 18-tool test)
├── tool_choice_demo.py  ← step 10 (NEW)
├── agent_sdk.py         ← step 11 (EDITED: sdk_tool() helper, the four tools)
├── policies/            ← step 12 (NEW folder: returns.md, shipping.md, warranty.md, refunds.md)
└── policy_helper.py     ← step 12 (NEW: built-in tools Glob, Grep, Read, Edit)
```
Commands, in order: (File → Open Folder) → `uv run loop_by_hand.py` (check) → (edit maple_data.py, new maple_tools.py, edit
loop_by_hand.py) → `uv run loop_by_hand.py "When will PP-4821 arrive?"` → (tool_test.py, lazy_tools.py, extra_tools.py) →
`uv run tool_test.py ep1 10 q1` → `uv run tool_test.py lazy 10` → `uv run tool_test.py good 10` →
`uv run tool_test.py lazy 10 trap` → `uv run tool_test.py good 10 trap` → `uv run tool_test.py many 10` →
`uv run tool_choice_demo.py "Where is my order A1001?"` → (edit agent_sdk.py) → `uv run agent_sdk.py "When will PP-4821 arrive?"` →
`uv run agent_sdk.py "Order A1003 arrived torn. Please refund the 89 dollars."` → (policies/, policy_helper.py) →
`uv run policy_helper.py "Which file says how long the warranty on tents is?"` →
`uv run policy_helper.py "Which policy files do we have? Just list them."` →
`uv run policy_helper.py "Unused items can now be returned within 45 days. Update the returns policy."`

This repo folder (`02-tool-design/`) holds the project as it is at the END of episode 2 (with `policies/returns.md` still
at 30 days, so the viewer's edit run works), plus this file, `README.md` (handout), `output.txt` and
`extras/claude_lazy_check.py` (an extra check on Claude, not a viewer step).

Line counts: maple_data.py 68, maple_tools.py 82, loop_by_hand.py 48, tool_test.py 59, tool_choice_demo.py 36,
agent_sdk.py 54, policy_helper.py 43 (lazy_tools.py 26 and extra_tools.py 43 are copied, not typed).

## Decisions and deviations from the plan
1. **`hand_to_human` left for episode 4** (escalation, handoff summary). Episode 2 has four tools, as the series plan says.
2. **`get_shipment`'s input renamed `id` → `tracking_number`** as part of the fix (a clear name is part of a clear
   interface). `lazy_tools.py` keeps episode 1's exact lazy pair (including `id`) so the "before" run is the real cliffhanger.
3. **`get_order` gets one boundary line** ("It does not accept tracking numbers like PP-4821: use get_shipment") and now
   also returns the price and tracking number. Episode 1's exact version is kept in `lazy_tools.py` as `EP1_GET_ORDER_TOOL`.
4. **`issue_refund` is a fake** (appends to a list; no money moves) and refuses amounts over the order price.
   Hooks and real rules are episode 4.
5. **tool_test.py scores only the first reply's first tool** (one call, the tool isn't run). That keeps 80 calls under
   two minutes. Full-loop runs (`loop_by_hand.py`) back it up in output.txt.
6. **The 18-tool test did NOT show misrouting** among the four Maple tools on our 8 questions (Q1–Q5, Q8 all 10/10).
   Its one change was Q7 ("What does Maple & Co. sell?" → `search_products` 8/10), which is reasonable once a catalogue
   tool exists. The honest story for step 9: our small test didn't break, but every turn the model reads 2.4× more tool
   text (907 → 2,215 tokens), Anthropic's docs say selection accuracy degrades past 30–50 tools, and the exam's principle is
   scoped tools per role. Don't claim our run proved degradation.
7. **The refund surprise:** with the good descriptions, the small model went straight to `issue_refund` 7/10 (lazy: 3/10)
   despite "you have already looked up the order with get_order". Claude (1 run) looked the order up first. Lesson for the
   script: a description guides the choice; it can't enforce an order of steps. Rules that must hold go in code (episode 4).
8. **The system-prompt trap:** "Whenever the customer mentions an order, call get_order." made the LAZY set send PP-4821
   to get_order 10/10 (it was 3/10 without the trap) but did nothing to the GOOD set (10/10; two sharper traps also 10/10).
   Story: one sentence in the system prompt can tip a weakly described tool set; good descriptions held in our test;
   review system prompts for keyword rules anyway (the guide's point).
9. **Example values can be copied:** in 1 of 10 A1001 runs (test and full loop each), the small model called
   `get_shipment('PP-4821')`, the example from the description. Mention it as an honest aside; the code keeps the examples
   (the docs recommend input examples; the miss rate is 1/10).
10. **tool_choice:** Ollama accepts the field without an error and ignores it (real output: `any` and `tool` still
    answered a general question in text; `none` still called `get_order`). Its docs list tool_choice as not supported.
    Claude's API applies it, but that needs an API key, which this course doesn't use. Current docs: on Claude Fable 5.2,
    Mythos 5.2, Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1, `any` and `tool` return a 400 error (`auto` and `none`
    work); on other models a forced call skips thinking and has no text before the tool call. The exam guide teaches all
    four; the script says both. `disable_parallel_tool_use` is mentioned only in NOTES (not in the guide's bullets).
11. **Built-in tools on macOS:** the tools reference says Glob and Grep are left out of the default tool set on macOS,
    Linux and WSL (Claude searches with find/grep through Bash instead), and come back when you name them in the SDK's
    `tools` option. `policy_helper.py` names them; the init message confirmed `['Edit', 'Glob', 'Grep', 'Read']`.
    `allowed_tools` only pre-approves (it doesn't restrict); `tools` is the list the model actually gets.
12. **Edit uniqueness shown for real:** `returns.md` contains "within 30 days of delivery" twice. Claude's Edit used the
    whole line as `old_string`, so it matched once. We did not get an Edit failure in our run, so the Read + Write fallback
    is explained from the guide + docs, not shown.
13. **Claude knows today's date:** its PP-4821 answer said "which is tomorrow" (runs 4 and 5). Don't read that clause out;
    fade/crop it on screen (owner to decide).
14. **Plan usage:** 7 full Agent SDK runs + 1 short init check (2 sessions). Budget was about 10.
15. **CPU only:** test-only copy (num_gpu 0, num_ctx 4096), 9/9 right first tools, 1.8–6.8 s per first reply after the
    model has loaded (16.6 s with the load).

## Windows
Not run on Windows. Same commands as episode 1 (`uv run …` is identical). The policy helper's paths use `pathlib`, so they
work on Windows too. On Windows, Glob and Grep are in Claude Code's default tool set anyway (tools reference).

## Sources (docs pages to screenshot)
- Define tools (descriptions, best practices, tool_choice, "Forcing tool use"): https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
- Tool use overview (default tool_choice auto): https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- Parallel tool use (disable_parallel_tool_use; models without any/tool): https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use
- Tool search ("degrades once you exceed 30–50 available tools"): https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool
- API errors ("Forced tool use not supported"): https://platform.claude.com/docs/en/api/errors
- Claude Code tools reference (Read, Write, Edit, Glob, Grep, Bash; Edit uniqueness; Glob/Grep on macOS): https://code.claude.com/docs/en/tools
- Agent SDK Python reference (tools, allowed_tools, disallowed_tools): https://code.claude.com/docs/en/agent-sdk/python
- Agent SDK permissions ("allowed_tools … does not restrict"): https://code.claude.com/docs/en/agent-sdk/permissions
- Agent SDK subagents (per-agent tool lists): https://code.claude.com/docs/en/agent-sdk/subagents
- Ollama Anthropic compatibility (tool_choice not supported): https://docs.ollama.com/api/anthropic-compatibility
