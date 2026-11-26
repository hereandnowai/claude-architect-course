# Claude Certified Architect – Foundations: Exam-Prep Course in Python (Claude Agent SDK, tool use, MCP, Claude Code)

**HERE AND NOW AI** · *AI is Good*

Free, tested, step-by-step code for the **Claude Certified Architect – Foundations** exam-prep video series on the
[HERE AND NOW AI YouTube channel](https://youtube.com/@hereandnow_ai). One project grows through the series: a
support agent for **Maple & Co.**, a made-up outdoor-gear shop.

**No API key needed.** The hand-written agent loop runs on a free local model (Ollama + `qwen3.5:4b`), and the Claude
Agent SDK examples run on a normal Claude Pro or Max plan login.

> Independent course: not affiliated with or endorsed by Anthropic. Claude is a trademark of Anthropic, PBC.
> We never use real exam questions; all practice questions are our own.

## Episodes

| # | Topic | Code |
|---|---|---|
| 1 | [The exam explained + your first AI agent in Python](https://youtu.be/hCftb5IPVas) (agent loop by hand, then with the Claude Agent SDK) | [01-first-agent](01-first-agent) |
| 2 | Tools Claude picks correctly | coming soon |
| 3 | Your own MCP server | coming soon |
| 4 | Rules the agent can't break (hooks, escalation) | coming soon |
| 5 | Claude Code for a team (CLAUDE.md, rules, commands, skills) | coming soon |
| 6 | Claude Code in CI | coming soon |
| 7 | Structured data extraction | coming soon |
| 8 | A multi-agent research team | coming soon |
| 9 | Context and sessions | coming soon |
| 10 | Exam day: practice exam and strategy | coming soon |

Each folder has its own `README.md` (the handout) and an `output.txt` with the real output we got when we ran it.

## Quick start

You need [uv](https://docs.astral.sh/uv/getting-started/installation/), [Ollama](https://ollama.com/download) and,
for the Agent SDK part, [Claude Code](https://code.claude.com/docs/en/setup) signed in with your Claude plan.

```bash
ollama pull qwen3.5:4b
git clone https://github.com/hereandnowai/claude-architect-course.git
cd claude-architect-course/01-first-agent
uv sync
uv run loop_by_hand.py      # the agent loop, by hand, on the free local model
uv run agent_sdk.py         # the same agent with the Claude Agent SDK, on your Claude plan
```

## About HERE AND NOW AI

HERE AND NOW AI teaches AI, generative AI and agentic AI, explained simply.

- Website: https://hereandnowai.com
- Email: info@hereandnowai.com
- Phone: +91 996 296 1000
- YouTube: https://youtube.com/@hereandnow_ai

## License

[MIT](LICENSE)
