---
created: 2025-09-25T18:56:05Z
last_updated: 2025-09-25T18:56:05Z
version: 1.0
author: Claude Code PM System
---

# Project Style Guide

## Coding Standards

### Command File Structure
All command files follow this pattern:
```markdown
---
allowed-tools: Read, Write, Bash, Task
---

# Command Title

Brief description of command purpose.

## Required Rules
Reference any rules from `.claude/rules/` that must be followed.

## Preflight Checklist
Validation steps before execution.

## Instructions
Step-by-step implementation details.
```

### Documentation Conventions
- **YAML Frontmatter**: Always include created, last_updated, version, and author fields
- **Real Timestamps**: Use actual datetime values, never placeholders like "YYYY-MM-DD"
- **Markdown Structure**: Consistent heading hierarchy and formatting
- **Relative Paths**: Always use project-relative paths, never absolute paths with usernames

### File Naming Standards
- **Commands**: `category/command-name.md` (kebab-case)
- **Agents**: `agent-purpose.md` (descriptive purpose-based naming)
- **Context**: `context-type.md` (descriptive, consistent with content)
- **Tasks**: `001.md` → `{issue-id}.md` (sequential then GitHub ID-based)

## Shell Script Standards

### Error Handling
- Fail-fast principle with clear error messages
- Provide actionable solutions in error output
- Never leave systems in partial or corrupted state
- Use proper exit codes for different failure types

### Command Safety
- All bash commands must be listed in `ccpm/settings.local.json` permissions
- Use sandbox mode by default unless explicitly overridden
- Validate inputs before executing destructive operations
- Provide confirmation prompts for irreversible actions

### Output Format
- Use consistent status indicators (✅, ❌, ⚠️, 📋, 📊, 🔍)
- Structure output for readability with clear sections
- Provide both summary and detailed information when relevant
- Use progress indicators for long-running operations

## Content Style Guide

### Writing Tone
- **Direct and Professional**: Clear, concise communication
- **Action-Oriented**: Focus on what to do, not just what exists
- **User-Focused**: Written from the perspective of helping users succeed
- **Technically Precise**: Use accurate terminology without unnecessary jargon

### Documentation Structure
1. **Purpose Statement**: What the document/command accomplishes
2. **Prerequisites**: What needs to be in place first
3. **Step-by-Step Instructions**: Clear, ordered implementation details
4. **Error Handling**: What to do when things go wrong
5. **Success Criteria**: How to know it worked correctly

### Code Comment Style
- **Minimal Comments**: Code should be self-documenting
- **Purpose Comments**: Explain why, not what
- **Frontmatter Documentation**: Use YAML for metadata, not inline comments
- **Command Descriptions**: Brief, active voice descriptions of command purpose

## GitHub Integration Standards

### Issue Management
- **Labels**: Use consistent labeling scheme (`epic:feature`, `task:feature`)
- **Titles**: Clear, descriptive titles that summarize the work
- **Descriptions**: Reference parent issues and provide context
- **Updates**: Regular progress updates in comments, not just at completion

### Commit Messages
- **Format**: Conventional commit style preferred
- **Scope**: Reference issue numbers when applicable
- **Content**: Focus on what changed and why
- **Atomic Commits**: Small, focused commits that can be easily reviewed

## Path and Reference Standards

### Privacy and Portability
- **Relative Paths**: Always use project-relative paths in documentation
- **No Username Exposure**: Never include absolute paths with usernames in public content
- **Cross-Platform**: Use forward slashes and avoid platform-specific assumptions
- **Project Root References**: Use consistent root directory indicators

### File References
- **Consistent Format**: Use `file_path:line_number` for code references
- **Relative to Project**: All paths relative to project root
- **Clear Context**: Provide enough context to locate references easily
- **Version Awareness**: Consider that files may change over time

## Quality Assurance Standards

### Validation Requirements
- All context files must be at least 10 lines of substantive content
- YAML frontmatter must be valid and complete
- Markdown formatting must be consistent and proper
- No placeholder content or "TBD" markers in production

### Testing and Verification
- Commands must include preflight validation
- Error conditions must be tested and handled
- Success paths must be validated
- Documentation must be verified for accuracy

### Maintenance Standards
- Regular updates to keep content current
- Version tracking for significant changes
- Author attribution for accountability
- Last updated timestamps for currency tracking