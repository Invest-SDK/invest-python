# Copilot instructions

Follow `/AGENTS.md` as the canonical repository instruction file.

Before generating SDK calls, inspect the current definitions in
`t_tech/invest/grpc` and the relevant proto files. Prefer
`t_tech.invest.grpc`, typed request models, `Decimal` for financial values,
timezone-aware UTC dates, and tests without real trading mutations.

Use `docs/ai/real-vs-sandbox.md` to preserve the requested execution mode and
`docs/ai/trading-safety.md` when code can create, replace, or cancel orders.
For end-to-end development or review of a trading program, follow the complete
workflow in `.agents/skills/t-invest-python-sdk-bot-builder/SKILL.md`; the prompts in
`docs/ai/prompts/` are fallbacks for assistants without skill support.

Keep `AGENTS.md` canonical for repository-wide rules. When a task-specific
trading requirement changes, update the relevant `docs/ai` page, the skill,
and its fallback prompt together.
