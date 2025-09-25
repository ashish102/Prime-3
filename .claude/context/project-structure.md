---
created: 2025-09-25T18:56:05Z
last_updated: 2025-09-25T18:56:05Z
version: 1.0
author: Claude Code PM System
---

# Project Structure

## Root Directory Organization

```
Prime-3/
├── .claude/                    # Claude Code PM system directory
│   ├── agents/                # Specialized agents for task execution
│   ├── commands/              # Command definitions by category
│   │   ├── context/          # Context management commands
│   │   ├── pm/               # Project management commands
│   │   └── testing/          # Test execution commands
│   ├── context/              # Project-wide context files (this directory)
│   ├── epics/                # Local workspace for epic management
│   ├── prds/                 # Product Requirements Documents
│   ├── rules/                # Operational rules and standards
│   └── scripts/              # Automation scripts
├── ccpm/                      # Core PM system implementation
│   ├── agents/               # Agent definitions
│   ├── commands/             # Command implementations
│   ├── hooks/                # System hooks and configurations
│   └── scripts/              # Bash automation scripts
├── doc/                      # Documentation (Chinese)
├── install/                  # Installation scripts and guides
├── zh-docs/                  # Chinese documentation
├── AGENTS.md                 # Agent reference documentation
├── COMMANDS.md               # Command reference documentation
├── README.md                 # Primary project documentation
├── CLAUDE.md                 # Claude Code guidance (updated)
└── LICENSE                   # MIT license
```

## Key Directory Patterns

### PM System Core (`ccpm/`)
- **agents/**: Reusable agent templates for specialized tasks
- **commands/**: Markdown-based command definitions with frontmatter
- **scripts/**: Shell scripts for PM operations
- **hooks/**: Git hooks and system integrations

### Working Directories (`.claude/`)
- **epics/**: Local epic management workspace (add to .gitignore)
- **prds/**: Product Requirements Documents storage
- **context/**: Project context and documentation
- **commands/**: Instance-specific command overrides

### File Naming Conventions
- Context files: descriptive names with `.md` extension
- Command files: `category/command-name.md` structure
- Agent files: `agent-name.md` with purpose-driven names
- Epic tasks: Start as `001.md`, `002.md`, renamed to `{issue-id}.md` after GitHub sync

## Module Organization
- **Documentation**: Multi-language support (English primary, Chinese translations)
- **Installation**: Cross-platform installation scripts
- **Commands**: Categorical organization (pm, context, testing)
- **Scripts**: Shell-based automation with bash permission requirements

## Integration Points
- GitHub CLI integration through `gh` commands
- Git worktree support for parallel development
- Markdown-based configuration and documentation
- Cross-platform shell script compatibility