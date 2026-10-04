# Anthropic Advisor Tool — Python Demos

The **advisor tool** lets a faster executor model (e.g. Claude Sonnet 4.6)
consult a higher-intelligence advisor model (e.g. Claude Opus 4.6) mid-generation
for strategic guidance. The advisor sees the full conversation, produces a plan
or course correction, and the executor continues informed by that advice — all
inside a single API request.

> **Beta.** Include the header `advisor-tool-2026-03-01` in your requests.

## Model compatibility

| Executor                         | Advisor              |
|----------------------------------|----------------------|
| Claude Haiku 4.5                 | Claude Opus 4.6      |
| Claude Sonnet 4.6                | Claude Opus 4.6      |
| Claude Opus 4.6                  | Claude Opus 4.6      |

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY='sk-ant-...'
```

## Examples

| #  | File                    | What it demonstrates                                            |
|----|-------------------------|-----------------------------------------------------------------|
| 01 | `01_basic_usage.py`     | Minimal single-turn advisor call                                |
| 02 | `02_multi_turn.py`      | Multi-turn conversation preserving advisor result blocks        |
| 03 | `03_caching.py`         | Advisor-side prompt caching with TTL                            |
| 04 | `04_combined_tools.py`  | Advisor alongside web search and a custom tool                  |
| 05 | `05_cost_tracking.py`   | Parsing `usage.iterations[]` for per-model cost breakdown       |
| 06 | `06_max_uses.py`        | Capping advisor calls per request with `max_uses`               |

Run any example:

```bash
python 01_basic_usage.py
```

## Key patterns

**Tool definition:**

```python
{
    "type": "advisor_20260301",
    "name": "advisor",
    "model": "claude-opus-4-6",
}
```

**Multi-turn — preserve full response content:**

```python
messages.append({"role": "assistant", "content": response.content})
```

Stripping `advisor_tool_result` blocks from the history will break the
conversation (400 error).

**Caching — add to the tool definition:**

```python
"caching": {"type": "ephemeral", "ttl": "5m"}
```

Cache writes cost more than reads save for ≤2 advisor calls. Enable caching for
longer agent loops (3+ calls).

## Links

- [Advisor tool documentation](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/advisor-tool)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
