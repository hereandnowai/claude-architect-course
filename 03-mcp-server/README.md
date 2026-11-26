# Claude Certified Architect – Foundations, Episode 3 of 10: Your Own MCP Server

**HERE AND NOW AI** · *AI is Good*

Episode 3 of our **Claude Certified Architect – Foundations** exam-prep course on the
[HERE AND NOW AI YouTube channel](https://youtube.com/@hereandnow_ai).
We continue the project from [episode 2](../02-tool-design/): Maple & Co.'s support agent, for a made-up outdoor-gear
shop. Today Maple's four tools move into **their own MCP server**, so any MCP client can use them.

- **An MCP server in Python** with the official `mcp` SDK: `get_order`, `get_shipment`, `find_customer`, `issue_refund`.
- **Claude Code** connects to it through a project `.mcp.json`, with the key in an environment variable (`${MAPLE_API_KEY}`).
- **The Claude Agent SDK** connects to the very same server.
- **Errors the agent can act on:** `isError`, an error category (validation, transient, business, permission) and `isRetryable`.
- **Resources:** a catalogue of Maple's policy files that Claude can read without searching.

Exam coverage: Domain 2, Tool Design & MCP Integration (18% of the exam), task statements 2.2 and 2.4.

> Independent course: not affiliated with or endorsed by Anthropic. Claude is a trademark of Anthropic, PBC.
> We never use real exam questions (candidates sign a confidentiality agreement); all practice questions are our own.

**6 parts, 12 steps.** Tick each one as you go.

| Part | Step | |
|---|---|---|
| 1. Pick up where we left off | 1. What episodes 1 and 2 built · 2. Open the project, check it still runs | ☐ ☐ |
| 2. Maple's tools as an MCP server | 3. Add the MCP SDK · 4. Write maple_server.py · 5. Test it, no AI needed | ☐ ☐ ☐ |
| 3. Plug it into Claude Code and the Agent SDK | 6. .mcp.json, with the key outside the file · 7. Claude Code uses Maple's tools · 8. The Agent SDK, same server | ☐ ☐ ☐ |
| 4. Errors the agent can act on | 9. Four kinds of errors · 10. Watch Claude react | ☐ ☐ |
| 5. Resources | 11. A catalogue of Maple's policies · 12. Claude reads the catalogue | ☐ ☐ |
| 6. Exam lens + practice | 10 practice questions (in the video) | |

You need episode 1's setup (uv, VS Code, Ollama with `qwen3.5:4b`, Claude Code signed in with a paid Claude plan).
Nothing new to install: the MCP SDK came with the Agent SDK. Official links:
[uv](https://docs.astral.sh/uv/getting-started/installation/) · [VS Code](https://code.visualstudio.com/download) ·
[Ollama](https://ollama.com/download) · [Claude Code](https://code.claude.com/docs/en/setup).

---

## Part 1. Pick up where we left off

### Step 1. What episodes 1 and 2 built
Episode 1: the agent loop by hand (`loop_by_hand.py`) and with the Claude Agent SDK (`agent_sdk.py`). Episode 2: Maple's
four tools with clear descriptions (`maple_tools.py`), a tool test, and a policy helper with built-in tools. The
cliffhanger: Maple's tools live inside our Python files, so only our own agents can use them.

### Step 2. Open the project, check it still runs
VS Code → **File → Open Folder** → Desktop → `claude-architect-course` → **Open**. **Terminal → New Terminal**.
```sh
uv run loop_by_hand.py "When will PP-4821 arrive?"
# turn 0: tool_use · get_shipment {'tracking_number': 'PP-4821'} … Answer: … arrive on Friday.
```
Starting from the repo instead? `git clone https://github.com/hereandnowai/claude-architect-course`, open the
`03-mcp-server` folder in VS Code, run `uv sync`.

## Part 2. Maple's tools as an MCP server

### Step 3. Add the MCP SDK
```sh
uv add mcp
```
It was already in `.venv` (the Agent SDK uses it); now `pyproject.toml` names it, because our code imports it.

### Step 4. Write `maple_server.py` (new file)
`MCPServer("maple")`, one `@mcp.tool` per Maple tool, each with **the same description** from `maple_tools.py`, and
`mcp.run()` at the bottom (stdio: the client starts the file and talks to it through stdin and stdout).

### Step 5. Test it, no AI needed → `mcp_check.py` (new file)
A tiny MCP client: it starts the server, lists the tools and calls three.
```sh
uv run mcp_check.py
# Tools: ['get_order', 'get_shipment', 'find_customer', 'issue_refund']
# get_order {'order_id': 'PP-4821'}   isError: False   text: {"error": "No order with number PP-4821"}
```
The text says "error", but `isError` is False: nobody can tell the call failed. Part 4 fixes that.

## Part 3. Plug it into Claude Code and the Agent SDK

### Step 6. `.mcp.json` (new file, project scope)
```json
{
  "mcpServers": {
    "maple": {
      "command": "uv",
      "args": ["run", "maple_server.py"],
      "env": { "MAPLE_API_KEY": "${MAPLE_API_KEY}" }
    }
  }
}
```
`${MAPLE_API_KEY}` is filled in from your environment when Claude Code starts the server, so the file holds no secret and
the whole team can commit it. Set the variable in your terminal (a made-up demo value for our fake shop):
```sh
export MAPLE_API_KEY=maple-demo-key        # Windows PowerShell: $env:MAPLE_API_KEY="maple-demo-key"
claude mcp list                            # without it: a "Missing environment variables" warning
```
Run `claude` once in the folder and choose **Use this MCP server** (project servers need your approval).
Personal or experimental servers go in your user config instead: `claude mcp add --scope user …` (stored in `~/.claude.json`).

### Step 7. Claude Code uses Maple's tools
```sh
claude -p "When will PP-4821 arrive?" --allowedTools "mcp__maple__*"
# PP-4821 is due to arrive **Friday**. It's with ParcelPost and is now at the local depot.
```
MCP tool names are `mcp__<server>__<tool>`; `mcp__maple__*` allows all of Maple's tools.

### Step 8. The Agent SDK, same server → `agent_mcp.py` (new file)
`mcp_servers={"maple": {"command": "uv", "args": ["run", "maple_server.py"], "env": {...}}}` and
`allowed_tools=["mcp__maple__*"]`. The init message shows `('maple', 'connected')`.
```sh
uv run agent_mcp.py "Hi, I'm Liam, liam@example.com. What did I order?"
```

## Part 4. Errors the agent can act on

### Step 9. Four kinds of errors → edit `maple_server.py`
`ok()` for normal answers (and "nothing found" is a normal answer, not an error); `fail(category, retryable, message)`
returns `isError: true` with `{"errorCategory", "isRetryable", "message"}`:

| Category | Example in Maple's server | Retry? | What the agent should do |
|---|---|---|---|
| validation | `get_order("PP-4821")`: not an order number | no | fix the input (use get_shipment) |
| transient | the carrier's system timed out (PP-5150, first try) | **yes** | try again |
| business | refund more than the order's price | no | explain the rule to the customer |
| permission | `MAPLE_API_KEY` missing | no | stop, and get a human |

### Step 10. Watch Claude react
```sh
uv run agent_mcp.py "Where is my parcel PP-5150?"
# Our server answered (isError): {"errorCategory": "transient", "isRetryable": true, …}
# Claude: Transient error, retryable — retry.     → second call works → "on the delivery van … Monday"
unset MAPLE_API_KEY
uv run agent_mcp.py "I'm Olivia. Order A1003 arrived torn. Please refund the 89 dollars."
# Our server answered (isError): {"errorCategory": "permission", "isRetryable": false, …}
# Claude: … no money was refunded. A team member needs to fix that … I can't retry it from here.
```

## Part 5. Resources

### Step 11. A catalogue of Maple's policies → edit `maple_server.py`
`@mcp.resource("maple://policies")` returns one line per policy file; `@mcp.resource("maple://policies/{name}")` returns
one file. Tools are for actions; resources are content the app or the agent can read.

### Step 12. Claude reads the catalogue → edit `agent_mcp.py`
`tools=["ListMcpResourcesTool", "ReadMcpResourceTool"]` (the two built-in tools that list and read MCP resources).
```sh
uv run agent_mcp.py "Can I return a sale item, and for how long?"
# ListMcpResourcesTool → ReadMcpResourceTool maple://policies → ReadMcpResourceTool maple://policies/returns
# Claude: Yes, you can return a sale item within 30 days of delivery, but you'll get store credit, not a refund. …
```
In interactive Claude Code, type `@` to pick a resource, like `@maple:maple://policies/returns`.

## Part 6. Practice questions (our own, not from the exam)
The 10 questions are in the video (Part 6), with answers and explanations.

## Next: Episode 4 of 10, rules the agent can't break
Hooks that block a refund over a limit, checks before money moves, and handing a chat to a human.
