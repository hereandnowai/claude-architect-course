# Notes: Claude Certified Architect course, Episode 3 of 10 (your own MCP server)

Internal notes for building the video: versions, exact paths and tree, decisions, sources. All runs: `output.txt`.

## Versions used (27 Nov 2026)
| Tool | Version |
|---|---|
| macOS / machine | 26.7.3, Apple M4 Max, 128 GB |
| uv / Python | 0.11.12 / CPython 3.12.12 |
| anthropic / claude-agent-sdk / mcp | 2.14.0 / 0.2.189 / **2.3.0** (official MCP Python SDK, `MCPServer`, `Client`) |
| Claude Code (installed) | 2.1.331, Claude Max plan login, no ANTHROPIC_API_KEY |
| Ollama / model | 0.32.13 / `qwen3.5:4b` (step 2 only) |
| Model used by Claude Code and the SDK | `claude-opus-5-5` (plan default, from the init message) |

`uv add mcp` downloads nothing: mcp 2.3.0 is already a dependency of claude-agent-sdk. It only adds `"mcp>=2.3.0"` to
`pyproject.toml` (we import it directly now, so we name it).

## Exact steps and paths (what the viewer sees)
```
~/Desktop/claude-architect-course/          ← File → Open Folder (the same folder as episodes 1 and 2)
├── .venv/ .gitignore .python-version README.md main.py          (unchanged)
├── pyproject.toml   ← step 3 (EDITED by uv add: "mcp>=2.3.0"; uv.lock updated too)
├── maple_server.py  ← step 4 (NEW: MCPServer + four @mcp.tool, same descriptions as maple_tools.py, mcp.run())
│                      step 9 (EDITED: ok() / fail(category, retryable, message) → CallToolResult with is_error)
│                      step 11 (EDITED: two @mcp.resource: maple://policies and maple://policies/{name})
├── mcp_check.py     ← step 5 (NEW: tiny MCP client, no model) · step 9 (EDITED: env + four error checks)
│                      step 11 (EDITED: list + read the catalogue)
├── .mcp.json        ← step 6 (NEW: project-scoped, env MAPLE_API_KEY = ${MAPLE_API_KEY})
├── agent_mcp.py     ← step 8 (NEW: Agent SDK + the external stdio server) · step 12 (EDITED: the two resource tools)
├── maple_data.py maple_tools.py loop_by_hand.py agent_sdk.py tool_test.py lazy_tools.py extra_tools.py
│   tool_choice_demo.py policy_helper.py                          (from episode 2, unchanged)
└── policies/        (episode 2; returns.md says 45 days for unused items after episode 2's edit run)
```
Commands, in order: (File → Open Folder) → `uv run loop_by_hand.py "When will PP-4821 arrive?"` → `uv add mcp` →
(maple_server.py) → (mcp_check.py) `uv run mcp_check.py` → (.mcp.json) `claude mcp list` (warning) →
`export MAPLE_API_KEY=maple-demo-key` → `claude` (approve "Use this MCP server", /exit) → `claude mcp list` (Connected) →
`claude -p "When will PP-4821 arrive?" --allowedTools "mcp__maple__*"` → (agent_mcp.py)
`uv run agent_mcp.py "Hi, I'm Liam, liam@example.com. What did I order?"` → (edit maple_server.py, mcp_check.py)
`uv run mcp_check.py` → `unset MAPLE_API_KEY; uv run mcp_check.py` → `export …; uv run agent_mcp.py "Where is my parcel PP-5150?"` →
`uv run agent_mcp.py "I'm Olivia. Order A1003 arrived torn. Please refund 120 dollars."` → `unset MAPLE_API_KEY;
uv run agent_mcp.py "I'm Olivia. Order A1003 arrived torn. Please refund the 89 dollars."` → (resources) `uv run mcp_check.py` →
(edit agent_mcp.py) `uv run agent_mcp.py "Can I return a sale item, and for how long?"`

This repo folder holds the project as it is at the END of episode 3. Line counts: maple_server.py 86 (step 4 version 35),
mcp_check.py 37, agent_mcp.py 45, .mcp.json 11.

## Decisions and findings
1. **MCP SDK v2 API:** `from mcp.server import MCPServer` (v2's name for FastMCP), `@mcp.tool(description=…)`,
   `@mcp.resource(uri)`, `mcp.run()` (stdio default). Client: `from mcp import Client, StdioServerParameters`.
   `StdioServerParameters.env` is merged over a small default environment (PATH, HOME…), so MAPLE_API_KEY must be passed
   explicitly; the same is true for the SDK's `env` and `.mcp.json`'s `env`.
2. **One description, three places:** the server's tools reuse `maple_tools.py`'s descriptions (`GET_ORDER_TOOL["description"]`),
   so the hand loop, the in-process SDK server (episode 2) and the MCP server all show the model the same text.
3. **The first server returns `-> str`:** MCP SDK v2 then also sends the text as structured content, and Claude Code
   shows it as `{"result": "…"}` (real output, step 8). Step 9 returns `CallToolResult` directly, so the text is plain.
4. **The "uniform error" problem shown for real:** in step 5, `get_order("PP-4821")` returns `{"error": …}` text with
   `isError: False`. That's episode 2's style, and it's exactly what the guide's 2.2 warns about.
5. **Error categories:** the guide's skill line says errorCategory (transient/validation/permission) and its knowledge
   line adds business errors; we use all four. "Nothing found" (`{"found": false}`) stays a normal result (guide: valid
   empty results vs access failures). Unknown order in `issue_refund` = validation (there's nothing to refund).
6. **The transient error is staged and said so:** our pretend carrier fails the FIRST `get_shipment("PP-5150")` call in
   each server process, then works. Claude (1 run): read `isRetryable: true`, wrote "Transient error, retryable — retry.",
   called again, answered. Script says "a pretend timeout".
7. **The business error didn't fire with Claude:** asked for $120 on an $89 order, Claude looked the order up and offered
   $89 without calling issue_refund (1 run). Honest story: Claude checked first; the server rule is the safety net for
   any client that doesn't (mcp_check.py shows the business error). Episode 4 adds rules that can't be skipped (hooks).
8. **Permission:** with MAPLE_API_KEY unset, Claude called issue_refund, got `permission / isRetryable false`, and told
   Olivia no money moved, a team member must fix the setup, "I can't retry it from here." (1 run).
9. **Missing env var in .mcp.json:** `claude mcp list` warns "Missing environment variables: MAPLE_API_KEY" and Claude
   Code passes the unexpanded `${MAPLE_API_KEY}` text (docs). The server treats a value starting with `${` as missing.
10. **Approval:** project servers from `.mcp.json` need approval in interactive Claude Code ("New MCP server found in this
    project: maple … Use this MCP server"); `claude -p` and the Agent SDK load them without asking (docs). We approved
    once interactively (no prompt sent to the model). The folder-trust dialog also says "Trusting this folder loads
    .mcp.json here or above (MCP servers)" (only shown on a folder's first trust; viewers trusted it in episode 1).
11. **Tool search:** in `claude -p`, Claude first called ToolSearch (`select:mcp__maple__…`) because MCP tool definitions
    are deferred by default (docs: "Tool search is enabled by default"). In the Agent SDK with `tools=[…]` (no ToolSearch)
    it's off, so the maple tools are loaded directly.
12. **Resources in the SDK:** with `tools=["ListMcpResourcesTool", "ReadMcpResourceTool"]` Claude listed the resources,
    read `maple://policies`, then `maple://policies/returns`, and answered (4 turns, 7.1 s). Templates
    (`maple://policies/{name}`) don't appear in `resources/list`; the catalogue tells Claude the URIs.
13. **Timeless:** Claude Code's answers mention today's date ("Today is Friday, November 27…", "Monday, November 30").
    The video shows only the first paragraph of run 1 and marks the cut (…); the Noah run isn't shown.
14. **Privacy:** `claude mcp list` also lists your own other connectors (cloud services, plugins). The video shows only
    the maple lines, with a note that other servers would be listed too.
15. **Plan usage:** 7 runs on the plan (2 claude -p, 5 Agent SDK), all short.

## Windows
Not run on Windows. `uv run …` is the same; set the variable with `$env:MAPLE_API_KEY="maple-demo-key"` (PowerShell).

## Sources (docs pages to screenshot)
- Claude Code MCP (scopes, .mcp.json, env expansion, approval, resources with @): https://code.claude.com/docs/en/mcp
- Agent SDK MCP (stdio config, mcp__server__tool names, allowedTools wildcards, init status, env credentials): https://code.claude.com/docs/en/agent-sdk/mcp
- MCP spec, tools (error handling: protocol errors vs isError tool execution errors): https://modelcontextprotocol.io/specification/latest/server/tools
- MCP spec, resources (URIs, resources/list, resources/read, templates): https://modelcontextprotocol.io/specification/latest/server/resources
- MCP Python SDK docs: https://py.sdk.modelcontextprotocol.io/
- Use the Claude Agent SDK with your Claude plan: https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
