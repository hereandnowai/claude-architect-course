# Claude Certified Architect – Foundations, Episode 2 of 10: Tools the Model Picks Correctly

**HERE AND NOW AI** · *AI is Good*

Episode 2 of our **Claude Certified Architect – Foundations** exam-prep course on the
[HERE AND NOW AI YouTube channel](https://youtube.com/@hereandnow_ai).
We continue the project from [episode 1](../01-first-agent/): Maple & Co.'s support agent, for a made-up outdoor-gear
shop. Today it grows from one tool to four, and we **measure** how often the model picks the right one.

- **Four tools with clear boundaries:** `get_order`, `get_shipment`, `find_customer`, `issue_refund`.
- **A test that asks the same questions ten times:** lazy descriptions vs good ones, a system-prompt trap, 4 tools vs 18.
- **tool_choice** (`auto`, `any`, `tool`, `none`): what each does, and an honest note on where it works.
- **Built-in tools** with the Claude Agent SDK: a policy helper that gets only Glob, Grep, Read and Edit.

Exam coverage: Domain 2, Tool Design & MCP Integration (18% of the exam), task statements 2.1, 2.3 and 2.5.

> Independent course: not affiliated with or endorsed by Anthropic. Claude is a trademark of Anthropic, PBC.
> We never use real exam questions (candidates sign a confidentiality agreement); all practice questions are our own.

**6 parts, 13 steps.** Tick each one as you go.

| Part | Step | |
|---|---|---|
| 1. Pick up where we left off | 1. What episode 1 built · 2. Open the project, check it still runs | ☐ ☐ |
| 2. Maple's four tools | 3. Grow Maple's data · 4. Four descriptions that don't overlap · 5. Connect the loop to all four | ☐ ☐ ☐ |
| 3. Test tool choice, with numbers | 6. A test that asks ten times · 7. Lazy vs good · 8. The system-prompt trap | ☐ ☐ ☐ |
| 4. How many tools, and which agent gets them | 9. Too many tools? · 10. tool_choice: four settings | ☐ ☐ |
| 5. Built-in tools with the Agent SDK | 11. Maple's four tools on Claude · 12. A policy helper · 13. Which built-in tool, when | ☐ ☐ ☐ |
| 6. Exam lens + practice | 10 practice questions (below) | |

Nothing new to install: you need episode 1's setup (uv, VS Code, Ollama with `qwen3.5:4b`, Claude Code signed in with a
paid Claude plan). Official links are in the [episode 1 handout](../01-first-agent/README.md#step-3-install-the-tools-official-links).

---

## Part 1. Pick up where we left off

### Step 1. What episode 1 built
An agent loop by hand (`loop_by_hand.py`: send → check `stop_reason` → run the tool → send back a `tool_result` → repeat
until `end_turn`) and the same agent with the Claude Agent SDK (`agent_sdk.py`). The cliffhanger: a second tool,
`get_shipment`, described only as "Gets shipment info.", and the question "When will PP-4821 arrive?". The small local
model chose `get_order` 10 times out of 10 and told the customer there was no such order.

### Step 2. Open the project, check it still runs
VS Code → **File → Open Folder** → Desktop → `claude-architect-course` → **Open**. **Terminal → New Terminal**. Make sure
Ollama is running.
```sh
uv run loop_by_hand.py
# turn 0: tool_use (4.6 s)
#   tool_use: get_order {'order_id': 'A1001'}
# turn 1: end_turn (0.7 s)
# Answer: Your order A1001, Emma, containing a Trail tent for two, is shipped and arrives Friday.
```
Starting from the repo instead? `git clone https://github.com/hereandnowai/claude-architect-course`, open the
`02-tool-design` folder in VS Code, run `uv sync`.

## Part 2. Maple's four tools

### Step 3. Grow Maple's data → edit `maple_data.py`
Four customers (Emma, Liam, Olivia, Noah) with emails; orders get a price and a tracking number; three parcels; three new
functions: `get_shipment`, `find_customer`, `issue_refund` (a fake: no money moves, never more than the order price).

### Step 4. Four descriptions that don't overlap → new file `maple_tools.py`
Every description answers five questions:
1. **What** does it do?
2. **When** should the model use it?
3. **What input**, with an example?
4. **When not** to use it, and which tool to use instead?
5. **What comes back**?

`run_tool()` dispatches all four, and an unknown tool gets an error.

### Step 5. Connect the loop to all four → edit `loop_by_hand.py`
Import `TOOLS` and `run_tool` from `maple_tools`, pass `tools=TOOLS`, and print each tool result.
```sh
uv run loop_by_hand.py "When will PP-4821 arrive?"
# turn 0: tool_use (2.0 s)
#   tool_use: get_shipment {'tracking_number': 'PP-4821'}
#   tool_result: {"tracking_number": "PP-4821", "carrier": "ParcelPost", "where": "Local depot", "arrives": "Friday"}
# turn 1: end_turn
# Answer: Your parcel PP-4821 is at the Local depot and will arrive on Friday.
```

## Part 3. Test tool choice, with numbers

### Step 6. A test that asks ten times → new file `tool_test.py` (+ `lazy_tools.py`, `extra_tools.py` from GitHub)
Eight questions, each with the right first tool. The script asks each one N times and counts the model's first choice.
```sh
uv run tool_test.py good 10        # tool sets: ep1, lazy, good, many;  add "trap", or q1 q4 … for some questions only
```

### Step 7. Lazy vs good (our results, qwen3.5:4b, 10 runs per question)
| | ep1 pair | lazy four | good four |
|---|---|---|---|
| "When will PP-4821 arrive?" | 0/10 | 7/10 | **10/10** |
| "Where is my order A1001?" | | 6/10 | 9/10 |
| All 8 questions | | 70/80 | 72/80 |
| Without the refund question | | 63/70 | **69/70** |
| Refund: "look the order up first" | | 7/10 | 3/10 |

The refund row is the surprise: a description guides the choice, but it can't force an order of steps. Rules that must
always hold belong in code (episode 4).

### Step 8. The system-prompt trap
Add one sentence to the system prompt: "Whenever the customer mentions an order, call get_order."
```sh
uv run tool_test.py lazy 10 trap   # PP-4821: 0/10 (was 7/10)
uv run tool_test.py good 10 trap   # PP-4821: 10/10 (no harm)
```

## Part 4. How many tools, and which agent gets them

### Step 9. Too many tools?
```sh
uv run tool_test.py many 10        # 18 tools: 65/80; the four Maple tools still 10/10 on their questions
```
In our small test, 18 tools didn't cause misrouting. Q7 changed ("What does Maple & Co. sell?" → `search_products`).
But the model reads more every turn: 63 tokens with no tools, 907 with our four, 2,215 with 18. Anthropic's docs say
selection accuracy degrades once you exceed 30–50 tools. The exam's principle: give each agent only the tools its role
needs.

### Step 10. tool_choice: four settings → new file `tool_choice_demo.py`
| `tool_choice` | Meaning |
|---|---|
| `{"type": "auto"}` | the model decides: a tool or plain text (the default when you pass tools) |
| `{"type": "any"}` | it must call a tool, but picks which |
| `{"type": "tool", "name": "get_order"}` | it must call this tool |
| `{"type": "none"}` | it must not call a tool (the default with no tools) |

**Honest note:** Ollama accepts `tool_choice` and ignores it (our run: `none` still called `get_order`). Claude's API
applies it, and that needs an API key from the Claude Console. Check the docs for your model: at the time of making this
episode (November 2026), Claude Opus 5.5, Claude Sonnet 5.5 and a few others return an error for `any` and `tool`.

## Part 5. Built-in tools with the Agent SDK

### Step 11. Maple's four tools on Claude → edit `agent_sdk.py`
`sdk_tool()` turns each of our definitions into an SDK tool: the same name, description and input schema.
```sh
uv run agent_sdk.py "When will PP-4821 arrive?"
# Claude asks for a tool: mcp__maple__get_shipment {'tracking_number': 'PP-4821'}
uv run agent_sdk.py "Order A1003 arrived torn. Please refund the 89 dollars."
# Claude asks for a tool: mcp__maple__get_order {'order_id': 'A1003'}
# Claude asks for a tool: mcp__maple__issue_refund {'order_id': 'A1003', 'amount': 89, 'reason': 'arrived torn'}
```

### Step 12. A policy helper → new folder `policies/` + new file `policy_helper.py`
`tools=["Glob", "Grep", "Read", "Edit"]`: these built-in tools and no others (no Bash, no Write). `cwd` is the policies
folder. On macOS and Linux, Claude Code leaves Glob and Grep out of the default tool set unless you name them.

### Step 13. Which built-in tool, when
| Request | Tools Claude used |
|---|---|
| "Which file says how long the warranty on tents is?" | **Grep** (search inside files) → **Read** |
| "Which policy files do we have? Just list them." | **Glob** (find files by name pattern) |
| "Unused items can now be returned within 45 days. Update the returns policy." | Grep → Read → **Edit** (a whole line as `old_string`, because "within 30 days of delivery" appears twice) |

Edit replaces text that must appear **exactly once**. If it can't find a unique match, read the whole file (Read) and
write it back (Write).

## Part 6. Practice questions (our own, not from the exam)
The 10 questions are in the video (Part 6), with answers and explanations.

## Next: Episode 3 of 10, your own MCP server
Maple's four tools move into their own MCP server, so Claude Code and any agent can use them, and the tools learn to
report errors in a way the agent can act on.
