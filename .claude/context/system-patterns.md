---
created: 2025-09-25T18:56:05Z
last_updated: 2025-09-25T18:56:05Z
version: 1.0
author: Claude Code PM System
---

# System Patterns

## Architectural Patterns

### Command Pattern Implementation
- **Structure**: Markdown files with YAML frontmatter defining execution parameters
- **Trigger**: Slash commands (`/command-name`) invoke markdown file interpretation
- **Validation**: Preflight checks and error handling built into each command
- **Tool Restrictions**: Frontmatter specifies allowed Claude Code tools per command

### Agent-Based Context Isolation
- **Context Firewall**: Agents process heavy workloads, return concise summaries
- **Parallel Execution**: Multiple agents work simultaneously without context collision
- **Specialization**: Purpose-driven agents (code-analyzer, test-runner, parallel-worker)
- **Communication**: Agents coordinate through Git commits, not direct communication

### Local-First with Explicit Sync
- **Pattern**: All operations work on local files first, sync to GitHub on command
- **Benefits**: Speed, offline capability, atomic operations
- **Sync Points**: Explicit commands like `/pm:epic-sync` and `/pm:issue-sync`
- **State Management**: Local files are source of truth until synchronized

## Data Flow Patterns

### 5-Phase Development Discipline
1. **Brainstorm** → PRD creation (`/pm:prd-new`)
2. **Document** → Epic planning (`/pm:prd-parse`)
3. **Plan** → Task decomposition (`/pm:epic-decompose`)
4. **Execute** → Parallel implementation (`/pm:issue-start`)
5. **Track** → Progress synchronization (`/pm:issue-sync`)

### Information Hierarchy
```
PRD → Epic → Tasks → GitHub Issues → Code → Commits
```
Each level maintains traceability to previous level.

### Context Management Flow
```
Project Analysis → Context Creation → Context Loading → Work Execution
     ↓                    ↓              ↓               ↓
/context:create → /context:update → /context:prime → /pm:next
```

## Error Handling Patterns

### Fail-Fast Validation
- Preflight checks before command execution
- Clear error messages with actionable solutions
- Never leave systems in partial/corrupted state
- Graceful degradation when possible

### Permission-Based Safety
- Bash command restrictions in `settings.local.json`
- Tool-specific permissions per command
- Sandboxed execution with explicit allowlists
- Safe defaults with opt-in dangerous operations

## Parallel Execution Patterns

### Issue Decomposition
- Single issues split into multiple parallel work streams
- File-level parallelism prevents conflicts
- Coordination through Git atomic commits
- Human resolution for conflicts when they occur

### Agent Coordination
- **parallel-worker**: Coordinates multiple sub-agents
- **Spawn Pattern**: Main thread → parallel-worker → specialized agents
- **Result Consolidation**: Agents report to coordinator, coordinator summarizes to main
- **Context Preservation**: Implementation details stay in agents

## File System Patterns

### Naming Conventions
- Tasks: `001.md` → `{issue-id}.md` after GitHub sync
- Context files: Descriptive names with consistent structure
- Commands: `category/command-name.md` hierarchical organization
- Agents: `purpose-name.md` with clear functional naming

### Directory Isolation
- `.claude/epics/`: Local workspace (git-ignored)
- `ccpm/`: System implementation (version controlled)
- Context separation for different concerns
- Atomic directory operations

### Metadata Management
- YAML frontmatter for structured data
- Real datetime stamps (never placeholders)
- Version tracking in context files
- Author attribution for audit trails

## Integration Patterns

### GitHub Integration
- Issues as single source of truth
- Comments for audit trail and progress updates
- Labels for organization (`epic:feature`, `task:feature`)
- Parent-child relationships through gh-sub-issue extension

### Git Workflow Integration
- Worktree support for clean parallel development
- Atomic commits with clear messages
- Branch isolation for different work streams
- Standard Git operations with PM workflow overlay