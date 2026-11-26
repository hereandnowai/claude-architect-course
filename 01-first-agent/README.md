# Claude Certified Architect – Foundations, Episode 1 of 10: The Exam Explained + Your First AI Agent in Python

**HERE AND NOW AI** · *AI is Good*

Episode 1 of our **Claude Certified Architect – Foundations** exam-prep course on the
[HERE AND NOW AI YouTube channel](https://youtube.com/@hereandnow_ai).
You build the first piece of a support agent for **Maple & Co.**, a made-up outdoor-gear shop. A customer asks
"Where is my order A1001?". The agent decides to call a `get_order` tool, reads the result, and answers.

We build it twice:
1. **By hand:** we write the agent loop ourselves. The brain is a free model on your own laptop (Ollama + `qwen3.5:4b`),
   reached with Anthropic's official Python SDK through Ollama's Anthropic-compatible API. No account, no key.
2. **With the Claude Agent SDK:** the SDK runs the loop for us, and the brain is Claude, on your Claude plan.

```
 question → model → stop_reason "tool_use" → our code runs get_order → tool_result → model → stop_reason "end_turn" → answer
```

> Independent course: not affiliated with or endorsed by Anthropic. Claude is a trademark of Anthropic, PBC.
> We never use real exam questions (candidates sign a confidentiality agreement); all practice questions are our own.

**6 parts, 12 steps.** Tick each one as you go.

| Part | Step | |
|---|---|---|
| 1. The exam in five minutes | 1. What the certificate proves · 2. The map | ☐ ☐ |
| 2. Set up your laptop | 3. Install the tools · 4. Create the project | ☐ ☐ |
| 3. What an agent loop is | 5. The kitchen analogy | ☐ |
| 4. Build the loop by hand | 6. Maple's data and the first tool · 7. The loop · 8. Run it and read every turn · 9. Three mistakes the exam warns about | ☐ ☐ ☐ ☐ |
| 5. The same agent with the Claude Agent SDK | 10. Turn `get_order` into an SDK tool · 11. Run it on your Claude plan · 12. Compare the two | ☐ ☐ ☐ |
| 6. Exam lens + practice | 5 practice questions (below) | |

Commands are shown for macOS/Linux; Windows notes are in [NOTES.md](NOTES.md#windows).

---

## Part 1. The exam in five minutes

### Step 1. What the certificate proves
From the official exam guide (version 1.1, exam code CCAR-F):
- It checks that you can make good design decisions when you build real apps with Claude: Claude Code, the Claude
  Agent SDK, the Claude API and the Model Context Protocol (MCP).
- 60 multiple-choice and multiple-response questions, 120 minutes, proctored (online or at a test centre).
- Every question sits inside a scenario: 4 scenarios are picked at random from 6.
- Pass mark: a scaled score of 720 on a 100–1,000 scale. Fee: $125 USD. Valid for 12 months; renewing on time is free.
- **Who can take it (at the time of writing, November 2026):** only people at companies in the Claude Partner Network.
  Joining is free for organisations that bring Claude to market (claude.com/partners). Booking is through Pearson VUE.
  Everything you learn in this course works with a normal Claude Pro or Max plan, exam or not.

### Step 2. The map
| Domain | Weight |
|---|---|
| 1. Agentic Architecture & Orchestration | 27% |
| 2. Tool Design & MCP Integration | 18% |
| 3. Claude Code Configuration & Workflows | 20% |
| 4. Prompt Engineering & Structured Output | 20% |
| 5. Context Management & Reliability | 15% |

The 6 scenarios: customer support agent · code generation with Claude Code · multi-agent research system ·
developer productivity agent · Claude Code in CI/CD · structured data extraction.
This episode covers **task statement 1.1** (agentic loops), in Domain 1 (27% of the exam).

## Part 2. Set up your laptop

### Step 3. Install the tools (official links)
| Tool | Official link | Check |
|---|---|---|
| uv (Python project manager) | <https://docs.astral.sh/uv/getting-started/installation/> | `uv --version` |
| Python 3.12 or newer | <https://www.python.org/downloads/> (optional: uv downloads Python 3.12 for you if it is missing) | `uv run python -V` |
| Visual Studio Code | <https://code.visualstudio.com/download> | |
| Claude Code (for Part 5) | <https://code.claude.com/docs/en/setup> | `claude --version` |
| Ollama (for Part 4) | <https://ollama.com/download> | `ollama --version` |

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh          # uv (macOS/Linux)
curl -fsSL https://claude.ai/install.sh | bash             # Claude Code (macOS/Linux)
ollama pull qwen3.5:4b                                     # the free local model, 3.3 GB
claude                                                     # once: sign in with your Claude plan, then type /exit
```
- **Claude plan:** Claude Code needs a paid plan (Pro, Max, Ultra, Team or Enterprise) or a Console account; the free
  plan does not include it. When you're signed in with your plan, the Agent SDK uses your plan's usage limits.
- **Apps that other people use** must use an API key from the Claude Console, not your personal plan login
  (Anthropic's rule, see NOTES.md). In this course everything runs on your own laptop, for you.
- New to Ollama? Watch our Ollama video first: https://youtu.be/vq8opP4w30s

### Step 4. Create the project
1. On your Desktop (or anywhere), make a new folder: **`claude-architect-course`**.
2. VS Code: **File → Open Folder…** → pick it. Open a terminal: **Terminal → New Terminal**.
3. In the terminal:
```bash
uv init --python 3.12
uv add anthropic claude-agent-sdk
uv run main.py          # prints: Hello from claude-architect-course!
```
The Explorer now shows `.venv/`, `.gitignore`, `.python-version`, `main.py`, `pyproject.toml`, `README.md`, `uv.lock`.

## Part 3. What an agent loop is

### Step 5. The kitchen analogy
The model is the head chef; our code is the kitchen helper. The chef never leaves the pass.
- Chef: "Bring me order A1001" → that's a **`tool_use`** block, and `stop_reason` is `"tool_use"`.
- Helper fetches it and hands it over → that's a **`tool_result`** block (with the same `tool_use_id`).
- Chef: "Plate is ready" → the final text, and `stop_reason` is `"end_turn"`. The loop stops.

Docs: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls> and
<https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons>.

## Part 4. Build the loop by hand

### Step 6. Maple's data and the first tool → new file `maple_data.py`
Three fake orders (Emma, Liam, Olivia), a `get_order()` function, the agent's instructions, and the tool definition:
a **name**, a **description** (what it does, when to use it, the input format with an example, what it returns) and an
**input schema**. See [maple_data.py](maple_data.py).

### Step 7. The loop → new file `loop_by_hand.py`
See [loop_by_hand.py](loop_by_hand.py). The heart of it:
1. send the messages and the tools;
2. look at `stop_reason`;
3. `"tool_use"` → run each tool, append the assistant message and then one user message with the `tool_result` blocks, repeat;
4. `"end_turn"` → print the answer and stop;
5. anything else (for example `"max_tokens"`) → stop and say why.
`MAX_TURNS = 10` is only a safety net. The line `thinking={"type": "disabled"}` is **for the small local model only**
(it makes it fast and reliable on a laptop); leave it out when you use Claude.

### Step 8. Run it and read every turn
Ollama must be running (open the Ollama app, or `ollama serve`).
```bash
uv run loop_by_hand.py
# turn 0: tool_use (1.6 s)
#   tool_use: get_order {'order_id': 'A1001'}
# turn 1: end_turn (0.8 s)
# Answer: Order A1001 was shipped by Maple & Co. and is expected to arrive this Friday.
uv run loop_by_hand.py "Hi, this is Liam. What is in my order A1002 and when does it arrive?"
```
In our test: the right tool 10 times out of 10, 2 to 3 seconds a run (about 4 to 8 seconds on the processor alone).
The answers are worded a little differently each time: that's normal. Full runs: [output.txt](output.txt).

### Step 9. Three mistakes the exam warns about
1. Stopping as soon as the reply contains any text (a reply can have text **and** a tool request).
2. Reading the words ("I'm done", "Here is your answer") to decide when to stop.
3. Using a turn limit as the main way to stop. Stop on `end_turn`; a limit is only a safety net.

## Part 5. The same agent with the Claude Agent SDK

### Step 10. Turn `get_order` into an SDK tool → new file `agent_sdk.py`
See [agent_sdk.py](agent_sdk.py): the `@tool` decorator wraps our same `get_order()` function (same description);
`create_sdk_mcp_server(name="maple", …)` puts it in a small in-process tool server; `ClaudeAgentOptions` gives the
agent that server, no built-in tools (`tools=[]`), and permission to use our tool without asking:
`allowed_tools=["mcp__maple__get_order"]` (custom tools are named `mcp__<server>__<tool>`).

### Step 11. Run it on your Claude plan
```bash
uv run agent_sdk.py
# Claude asks for a tool: mcp__maple__get_order {'order_id': 'A1001'}
# Our tool answered: [{'type': 'text', 'text': '{"order_id": "A1001", "customer": "Emma", ...}'}]
# Claude: Your order A1001, the Trail tent for two, has shipped and should arrive on Friday.
# Done: success, 2 turns, 5.9 s
```
Each run uses a little of your plan's usage limits.

### Step 12. Compare the two
| | `loop_by_hand.py` | `agent_sdk.py` |
|---|---|---|
| Who runs the loop | our code (`stop_reason` checks) | the SDK |
| Brain | any model with Claude's message format (here a free local one) | Claude, on your plan |
| Good for | understanding, full control, exam questions about `stop_reason` | real agents: built-in tools, hooks, subagents, sessions (later episodes) |

## Part 6. Practice questions (our own, not from the exam)
See the video for the five Maple & Co. scenario questions with answers and explanations.

---

## Next: Episode 2 of 10, tools Claude picks correctly
We add a second tool, `get_shipment`, with a lazy description ("Gets shipment info."). In our test with the local model,
"When will PP-4821 arrive?" went to the wrong tool 10 times out of 10; with good descriptions, 10 out of 10 right.
Preview: `uv run teaser/lazy_tool.py lazy "When will PP-4821 arrive?"` (results in `teaser/teaser-runs.txt`).

Code: github.com/hereandnowai/claude-architect-course (folder `01-first-agent`), MIT licence.
