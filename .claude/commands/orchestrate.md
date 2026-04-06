# Orchestrate Command

Use this command to decompose complex tasks into specialized agent tasks, track progress, or resume orchestrations.

## Usage

```
/orchestrate <task description>  # Start new orchestration
/orchestrate status             # Show current orchestration progress
/orchestrate resume             # Resume from saved orchestration state
```

## What this command does:

### Start Mode (`/orchestrate <task>`)

1. **Analyzes the task** for complexity and dependencies
2. **Decomposes into subtasks** for specialist agents
3. **Creates a task plan** with proper dependencies
4. **Launches agents in waves** to manage context
5. **Tracks progress** and handles integration

### Status Mode (`/orchestrate status`)

1. **Shows progress** (completion rate, task breakdown)
2. **Lists active agents** currently working
3. **Identifies blockers** and dependencies
4. **Shows conflicts** detected by validators

### Resume Mode (`/orchestrate resume`)

1. **Loads saved state** from previous orchestration
2. **Shows next tasks** ready to execute
3. **Continues execution** from where it left off

## Instructions for Claude

When this command is invoked, detect which mode based on the argument:

### For `/orchestrate status`

1. **Use the context manager CLI** to get current state:

   ```bash
   yarn context:status
   ```

2. **Or programmatically** import and call:

   ```typescript
   import { AgentContextHub } from './.claude/lib/context-manager';
   const hub = new AgentContextHub();
   const status = hub.getOrchestrationStatus();
   ```

3. **Display the formatted output** from the CLI command, which shows:
   - Progress: X/Y tasks completed (Z%)
   - Active Agents currently working
   - Tasks by Status (Completed, In Progress, Pending, Blocked)
   - Conflicts detected
   - Next actionable tasks

### For `/orchestrate resume`

1. **Use the context manager CLI** to check for resumable state:

   ```bash
   yarn context:next
   ```

2. **Or programmatically**:

   ```typescript
   import { AgentContextHub } from './.claude/lib/context-manager';
   const hub = new AgentContextHub();
   const resumable = hub.getResumableOrchestration();
   ```

3. **If no state exists** (`!resumable.hasState`): Inform user there's nothing to resume

4. **If state exists**:
   - Show progress summary from `resumable.progress`
   - List next actionable tasks from `resumable.nextTasks` (tasks with completed dependencies)
   - Show blocked tasks and what they're waiting on
   - Ask user if they want to continue with next wave

5. **On confirmation**: Launch the next wave of tasks using the Task tool, and mark them as `in_progress` in the context manager

### For `/orchestrate <task>` (Start Mode)

1. **Act as the Orchestrator Agent** - Read and follow [.claude/agents/orchestrator.md](../.claude/agents/orchestrator.md)

2. **Detect technology stack** (if existing project):

   ```bash
   yarn context:detect
   ```

   This helps route tasks to appropriate language-specific specialists.

3. **Analyze the request** and decompose it into:
   - Atomic, parallelizable tasks
   - Clear dependencies between tasks
   - Appropriate specialist assignments

4. **Present a plan** to the user before executing:

   ```
   Task Decomposition:
   ├─ Wave 1 (Parallel)
   │  ├─ types-specialist: Define interfaces
   │  └─ database-specialist: Design schema
   ├─ Wave 2 (Parallel, depends on Wave 1)
   │  ├─ backend-specialist: Implement API
   │  └─ frontend-specialist: Build components
   └─ Wave 3 (Sequential, depends on Wave 2)
      ├─ integration-validator: Validate contracts
      └─ test-specialist: Write integration tests
   ```

5. **Register ALL tasks upfront** using CLI commands:

   After decomposing the request, register every task with the context manager using CLI:

   ```bash
   npx claude-orchestra register "Task description" specialist-name [dependency-ids...]
   ```

   **Example workflow:**

   ```bash
   # Wave 1 - No dependencies
   npx claude-orchestra register "Define TypeScript interfaces for auth models" types-specialist
   # Returns: task-001

   # Wave 2 - Depends on Wave 1
   npx claude-orchestra register "Implement JWT auth endpoints" backend-python-specialist task-001
   # Returns: task-002

   npx claude-orchestra register "Create users table migration" database-specialist task-001
   # Returns: task-003

   # Wave 3 - Depends on Wave 2
   npx claude-orchestra register "Add auth middleware" backend-python-specialist task-002 task-003
   # Returns: task-004
   ```

   **Store these task IDs** - you'll need them throughout the orchestration.

6. **Track in TodoWrite for UI visibility**:

   Also add tasks to TodoWrite so user sees progress in the UI:

   ```typescript
   TodoWrite([
     {
       content: 'Define TypeScript interfaces for auth models',
       status: 'pending',
       activeForm: 'Defining TypeScript interfaces for auth models',
     },
     {
       content: 'Implement JWT auth endpoints',
       status: 'pending',
       activeForm: 'Implementing JWT auth endpoints',
     },
     {
       content: 'Create users table migration',
       status: 'pending',
       activeForm: 'Creating users table migration',
     },
     { content: 'Add auth middleware', status: 'pending', activeForm: 'Adding auth middleware' },
   ]);
   ```

7. **Before launching each task:**

   a. **Check if task can start** (dependencies satisfied):

   ```bash
   npx claude-orchestra can-start <task-id>
   ```

   Only proceed if output shows "✅ Task can start"

   b. **Mark task as in-progress** in BOTH systems:

   ```bash
   npx claude-orchestra update-task <task-id> in_progress
   ```

   ```typescript
   TodoWrite([{ content: "Define TypeScript interfaces...", status: "in_progress", ... }])
   ```

   c. **Read the agent definition file**:

   ```
   Read file: .claude/agents/{specialist-name}.md
   ```

   Example: For backend task → read `.claude/agents/backend-python-specialist.md`

   d. **Launch the specialist** with Task tool, including task ID in prompt:

   ```
   Task(
     subagent_type="general-purpose",
     prompt="""
     {FULL CONTENTS OF .claude/agents/{specialist-name}.md}

     ========================================
     YOUR SPECIFIC TASK
     ========================================
     Task ID: {task-id from register command}

     {detailed task description with acceptance criteria}

     ========================================
     CONTEXT
     ========================================
     {minimal, focused context - only interfaces and contracts this task needs}

     ========================================
     HANDOFF REQUIREMENTS
     ========================================
     When complete, return structured handoff as specified in .claude/docs/AGENT_CONTRACT.md

     Your Task ID: {task-id}
     """
   )
   ```

   e. **Launch tasks in parallel** when they're in the same wave

8. **When specialist completes**, process handoff in BOTH systems:

   a. **Update context manager** with artifacts using CLI:

   ```bash
   npx claude-orchestra update-task <task-id> completed '{
     "files": ["path/to/modified/files"],
     "interfaces": [{"name": "InterfaceName", "file": "path/to/file"}],
     "metadata": {
       "dependencies": ["package-names"],
       "testRequirements": ["Test scenarios"]
     }
   }'
   ```

   b. **Update TodoWrite**:

   ```typescript
   TodoWrite([{ content: "Define TypeScript interfaces...", status: "completed", ... }])
   ```

9. **Monitor progress periodically**:

   ```bash
   npx claude-orchestra status
   ```

   Shows completion rate, active agents, blocked tasks.

10. **Check for conflicts** after each wave:

```bash
yarn context:conflicts
```

8. **Validate integration** by launching the integration-validator agent

## Examples

### Start a new orchestration

```
/orchestrate Implement real-time WebSocket notification system with Redis pub/sub
```

This would decompose into:

- Wave 1: Define message types, design Redis schema
- Wave 2: Implement WebSocket server, Redis integration, client manager
- Wave 3: Validate integration, write tests

### Check orchestration status

```
/orchestrate status
```

Shows current progress, active agents, blocked tasks, and conflicts.

### Resume interrupted orchestration

```
/orchestrate resume
```

Loads saved state and continues with next actionable tasks.

## Important

### For Start Mode

- **Never write code yourself** as orchestrator
- **Detect technology stack first** using `yarn context:detect`
- **Always present the plan first**
- **Use BOTH TodoWrite (UI) and Context Manager (persistence)** to track tasks
- **Launch agents in parallel when possible** (same-wave tasks)
- **Process handoffs properly** - update context manager with artifacts
- **Check for conflicts** after each wave using `yarn context:conflicts`
- **Validate integration at the end**

### For Status Mode

- **Use context manager CLI** (`yarn context:status`)
- **Format output clearly** with progress indicators
- **Highlight blockers** that need attention
- **Show next actionable tasks**

### For Resume Mode

- **Use context manager CLI** (`yarn context:next`)
- **Check for resumable state first**
- **Show what's been completed** so user has context
- **Show blocked tasks** and their dependencies
- **Get confirmation** before launching next wave
- **Update task status to in_progress** when resuming

### Why Dual Tracking?

**TodoWrite** = Real-time UI feedback (user sees progress NOW)
**Context Manager** = Persistent orchestration database (enables resume, cross-session state)

They serve different purposes:

- TodoWrite is ephemeral (lost when conversation ends)
- Context Manager persists to `.claude/state/context-state.json`
- Context Manager enables resume, artifact tracking, dependency management
- TodoWrite provides immediate visibility in Claude Code UI
