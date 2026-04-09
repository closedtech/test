# Multi-Agent Architecture

## Overview
Централизованная мультиагентная система где Neo (центральный агент) координирует специализированных агентов.

## Agent Roles

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Neo (Central)** | Координатор | Планирование, делегирование, агрегация |
| **Researcher** | Исследователь | Поиск, анализ, синтез информации |
| **Coder** | Программист | Реализация, оптимизация, тесты |
| **Reviewer** | Критик | Ревью, проверка качества, баги |

## Communication Flow

```
User ──▶ Neo ──▶ Researcher
              │
              ▼
           Coder ──▶ Reviewer
              ▲
              │
              └────────── (loop until good)
```

## Task Queue
Tasks are stored in `tasks/queue.md`
Results in `tasks/results.md`

## Spawn Commands

```python
# Spawn researcher
sessions_spawn(
    task="Research: [topic]",
    label="researcher",
    mode="run",
    runtime="subagent"
)

# Spawn coder
sessions_spawn(
    task="Implement: [specification]",
    label="coder", 
    mode="run",
    runtime="subagent"
)

# Spawn reviewer
sessions_spawn(
    task="Review: [code]",
    label="reviewer",
    mode="run",
    runtime="subagent"
)
```

## Memory Architecture
- `MEMORY.md` — глобальный контекст (Neo only)
- `agents/researcher/memory.md` — контекст исследователя
- `agents/coder/memory.md` — контекст программиста
- `agents/reviewer/memory.md` — контекст критика

## Quality Gates
1. Researcher must complete before Coder starts
2. Coder output must pass Reviewer
3. Neo approves final delivery to User
