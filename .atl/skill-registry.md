# Skill Registry — AI-day-project

Generated: 2026-10-09

## User Skills (project-level, .claude/skills/)

| Skill | Trigger | Path |
|-------|---------|------|
| rag-implementation | Building RAG / document Q&A with vector DBs. CONCEPTS ONLY: its code uses LangChain — do NOT follow code | .claude/skills/rag-implementation/SKILL.md |
| openrouter-models | Querying OpenRouter models, pricing, capabilities, providers (TS scripts) | .claude/skills/openrouter-models/SKILL.md |
| flock-brand-design | Any UI/styling/logos/Streamlit theming for Flock | .claude/skills/flock-brand-design/SKILL.md |

## User Skills (user-level, ~/.claude/skills/)

| Skill | Trigger |
|-------|---------|
| go-testing | Go tests / Bubbletea (not relevant here) |
| skill-creator | Creating new AI skills |
| branch-pr, issue-creation, judgment-day | PR / issue / adversarial review workflows |

## Compact Rules

### flock-brand-design
- All UI (Streamlit theme, CSS, logos) MUST use the official Flock palette, gradients and logo files from the skill. Read the skill before any UI code.

### rag-implementation
- Use for concepts only (chunking, embeddings, retrieval, prompting). Implement the loop by hand with chromadb + openai SDK; NO LangChain/LangGraph.

### openrouter-models
- Use only to pick/inspect a `:free` model; app calls OpenRouter via `openai` SDK, base_url https://openrouter.ai/api/v1.

## Project Conventions
- No project-level CLAUDE.md/AGENTS.md. Global user rules: never build after changes; use bat/rg/fd/sd/eza; conventional commits; no AI attribution in commits.
