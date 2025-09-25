---
created: 2025-09-25T18:56:05Z
last_updated: 2025-09-25T18:56:05Z
version: 1.0
author: Claude Code PM System
---

# Technology Context

## Primary Technologies

### Core Platform
- **Language**: Bash shell scripting
- **Platform**: Cross-platform (Linux, macOS, Windows PowerShell)
- **Architecture**: Command-driven workflow system
- **Documentation**: Markdown-based with YAML frontmatter

### External Dependencies

#### Required Tools
- **GitHub CLI** (`gh`): Version 2.74.0+ for GitHub integration
- **gh-sub-issue extension**: For parent-child issue relationships
- **Git**: Version control system integration
- **Bash/Shell**: Command execution environment

#### Supported Package Managers
- npm/pnpm/npx (Node.js ecosystem)
- cargo (Rust)
- go (Go language)
- composer (PHP)
- bundle (Ruby)
- maven/gradle (Java)
- dotnet (.NET)
- pytest/ruff (Python)
- make (C/C++)
- flutter/swift (Mobile)

## Development Environment

### Shell Permissions Required
As defined in `ccpm/settings.local.json`:
- Git operations (`git:*`)
- GitHub CLI (`gh:*`)
- Package managers (language-specific)
- Development tools (`pytest:*`, `ruff:*`, `make:*`)
- File operations (`cat:*`, `find:*`, `grep:*`, `ls:*`, `mv:*`, `rm:*`, `sed:*`)

### Configuration Files
- `ccpm/settings.local.json`: Bash command permissions
- `ccpm/ccpm.config`: System configuration
- `.gitignore`: Excludes `.claude/epics/` from version control

### Integration Architecture
- **GitHub Issues**: Single source of truth for project state
- **Git Worktrees**: Clean isolation for parallel development
- **Markdown Files**: Configuration, documentation, and task definitions
- **YAML Frontmatter**: Structured metadata in documentation

## System Patterns

### Command Pattern
- Commands are markdown files with YAML frontmatter
- `/command-name` triggers execution
- Frontmatter specifies allowed tools and parameters
- Commands can spawn specialized agents

### Agent Pattern
- Context firewall architecture
- Heavy processing in agents, summaries returned to main thread
- Parallel agent execution without context collision
- Agent communication through Git commits

### File Management
- Local-first operations with explicit GitHub synchronization
- Atomic file operations and error handling
- Relative path standards for portability
- Real-time datetime stamping

## Deployment & Distribution
- Shell script installation (`curl` and `wget` support)
- Cross-platform installer for Windows PowerShell
- MIT License for open source distribution
- Multi-language documentation support