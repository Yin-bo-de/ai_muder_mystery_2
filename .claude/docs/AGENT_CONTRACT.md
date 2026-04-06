# Agent Contract

**All specialist agents must follow this contract when working within the orchestration system.**

## Core Principles

### 1. Single Responsibility

- **Focus ONLY on your assigned task**
- Don't expand scope beyond what orchestrator requested
- Don't implement features from other specialists' domains
- If you need another domain's work, request it via handoff protocol

### 2. Complete Implementation

- **Implement complete, production-ready code**
- Don't leave TODOs or placeholders
- Handle all error cases
- Include necessary imports and dependencies
- Code should work immediately when integrated

### 3. Interface Clarity

- **Export clear interface contracts**
- Document function signatures and types
- Specify input/output formats explicitly
- Make dependencies on other components clear
- Use consistent naming conventions

### 4. Context Awareness

- **Work within your context budget** (typically 8-15k tokens)
- Only read files relevant to your task
- Don't request full project history
- Focus on interfaces, not implementation details of other agents

### 5. Quality Standards

- **Follow language-specific best practices**
- Adhere to project conventions (if they exist)
- Write idiomatic code for your language/framework
- See [SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md) for security requirements

### 6. Documentation

- **Document edge cases and assumptions**
- Explain non-obvious decisions
- Note limitations or trade-offs made
- Document complex business logic

### 7. MCP Tools Usage

- **Use available MCP servers when helpful**
- **context7**: Available for enhanced context management
  - Use `mcp__context7__*` tools for storing/retrieving cross-session context
  - Useful for maintaining state across orchestration sessions
  - Store important decisions, architectural patterns, or conventions
- Check for other MCP tools in `.mcp.json` that may assist your task
- Prefer MCP tools over manual file operations when they provide better abstractions

### 8. Handoff Protocol

- **Use structured handoff format** when passing to next agent
- Include: completed artifacts, interfaces, edge cases, next steps
- Make integration points explicit
- Specify test requirements

## What NOT to Do

### Don't:

- ❌ Implement features outside your domain
- ❌ Make assumptions about other agents' work
- ❌ Leave incomplete code or TODOs
- ❌ Ignore error handling
- ❌ Use overly generic types (`any`, `object`, `interface{}`)
- ❌ Hardcode configuration values
- ❌ Write code that only works in specific environments

### Do:

- ✅ Ask for clarification if task is ambiguous
- ✅ Flag blockers or dependencies explicitly
- ✅ Return detailed handoff information
- ✅ Use environment variables for configuration
- ✅ Write portable, testable code

## Handoff Template

When completing your task, return:

```json
{
  "completed_task": "task-id",
  "artifacts": {
    "files": ["list of files created/modified"],
    "interfaces": [{ "name": "InterfaceName", "file": "path/to/file" }],
    "endpoints": ["API endpoints if applicable"],
    "dependencies": ["new packages added"]
  },
  "edge_cases": ["Edge case 1 and how it's handled", "Edge case 2 and how it's handled"],
  "assumptions": [
    "Assumption 1 made during implementation",
    "Assumption 2 that should be validated"
  ],
  "test_requirements": ["Test scenario 1", "Test scenario 2"],
  "next_steps": ["What needs to happen next", "Who should do it"]
}
```

## Integration Points

When your work depends on or affects other agents:

1. **Identify dependencies early**: Don't discover halfway through
2. **Use shared types**: Import from common type definitions
3. **Document contracts**: What you expect from others, what you provide
4. **Validate assumptions**: Check that dependencies exist and work as expected

## Completion Criteria

Before marking your task complete:

- [ ] All specified functionality implemented
- [ ] Security checklist satisfied (see [SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md))
- [ ] Error handling comprehensive
- [ ] Code follows project conventions
- [ ] Interfaces exported and documented
- [ ] Dependencies specified (with versions)
- [ ] Handoff information complete

## Remember

You are part of a coordinated system. Your work must integrate seamlessly with other specialists' work. Quality and completeness are more important than speed.

**When in doubt, ask the orchestrator for clarification rather than making assumptions.**
