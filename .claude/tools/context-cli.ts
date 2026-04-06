#!/usr/bin/env node
/**
 * Context Manager CLI Wrapper
 *
 * Provides command-line interface for AgentContextHub operations
 * Used by Claude Code during orchestration to manage persistent state
 */

import { AgentContextHub, TechnologyDetector, Task, AgentArtifact } from '../lib/context-manager';

// ===========================
// CLI Helper Functions
// ===========================

/**
 * Register a new task in the context manager
 * Usage: yarn context:register "task description" "agent-name" [dependency-ids...]
 */
export function registerTask(
  description: string,
  assignedTo: string,
  dependencies: string[] = [],
  estimatedTokens: number = 10000
): { taskId: string; task: Task } {
  const hub = new AgentContextHub();

  const task = hub.registerTask({
    description,
    assignedTo,
    dependencies,
    estimatedContextTokens: estimatedTokens,
  });

  console.log(`✅ Task registered: ${task.taskId}`);
  console.log(`   Assigned to: ${task.assignedTo}`);
  console.log(`   Status: ${task.status}`);
  if (dependencies.length > 0) {
    console.log(`   Dependencies: ${dependencies.join(', ')}`);
  }

  return { taskId: task.taskId, task };
}

/**
 * Update task status
 * Usage: yarn context:update <task-id> <status> [artifacts-json]
 */
export function updateTaskStatus(
  taskId: string,
  status: 'pending' | 'in_progress' | 'completed' | 'blocked',
  artifacts?: {
    files?: string[];
    interfaces?: Array<{ name: string; file: string }>;
    metadata?: Record<string, any>;
  }
): void {
  const hub = new AgentContextHub();

  hub.updateTaskStatus(taskId, status, artifacts);

  console.log(`✅ Task ${taskId} updated to: ${status}`);
  if (artifacts?.files) {
    console.log(`   Files: ${artifacts.files.join(', ')}`);
  }
  if (artifacts?.interfaces) {
    console.log(`   Interfaces: ${artifacts.interfaces.map((i) => i.name).join(', ')}`);
  }
}

/**
 * Get comprehensive orchestration status
 * Usage: yarn context:status
 */
export function getOrchestrationStatus(): void {
  const hub = new AgentContextHub();
  const status = hub.getOrchestrationStatus();

  console.log('\n📊 Orchestration Status');
  console.log('='.repeat(50));

  // Progress overview
  const { progress } = status;
  console.log(
    `\nProgress: ${progress.byStatus.completed}/${progress.totalTasks} tasks completed (${progress.completionRate.toFixed(1)}%)`
  );

  // Tasks by status
  console.log('\nTasks by Status:');
  console.log(`  ✅ Completed: ${progress.byStatus.completed}`);
  console.log(`  ⚙️  In Progress: ${progress.byStatus.in_progress}`);
  console.log(`  ⏳ Pending: ${progress.byStatus.pending}`);
  console.log(`  ⚠️  Blocked: ${progress.byStatus.blocked}`);

  // Active agents
  if (progress.activeAgents.length > 0) {
    console.log('\nActive Agents:');
    progress.activeAgents.forEach((agent) => {
      const tasks = status.tasks.filter(
        (t) => t.assignedTo === agent && t.status === 'in_progress'
      );
      tasks.forEach((task) => {
        console.log(`  - ${agent}: ${task.description}`);
      });
    });
  }

  // Conflicts
  if (status.conflicts.length > 0) {
    console.log('\n⚠️  Conflicts Detected:');
    status.conflicts.forEach((conflict) => {
      console.log(`  [${conflict.severity}] ${conflict.description}`);
    });
  }

  // Next actions
  const nextTasks = status.tasks.filter((t) => {
    if (t.status !== 'pending') return false;
    return t.dependencies.every((depId) => {
      const dep = status.tasks.find((task) => task.taskId === depId);
      return dep?.status === 'completed';
    });
  });

  if (nextTasks.length > 0) {
    console.log('\n🚀 Next Actionable Tasks:');
    nextTasks.forEach((task) => {
      console.log(`  - ${task.taskId}: ${task.description}`);
      console.log(`    Assigned to: ${task.assignedTo}`);
    });
  }

  console.log('');
}

/**
 * Get next tasks that are ready to start
 * Usage: yarn context:next
 */
export function getNextTasks(): Task[] {
  const hub = new AgentContextHub();
  const resumable = hub.getResumableOrchestration();

  if (!resumable.hasState) {
    console.log('ℹ️  No active orchestration found');
    return [];
  }

  console.log('\n🚀 Next Actionable Tasks:');
  console.log('='.repeat(50));

  resumable.nextTasks.forEach((task, index) => {
    console.log(`\n${index + 1}. ${task.description}`);
    console.log(`   Task ID: ${task.taskId}`);
    console.log(`   Assigned to: ${task.assignedTo}`);
    console.log(`   Estimated tokens: ${task.estimatedContextTokens}`);
  });

  if (resumable.blockedTasks.length > 0) {
    console.log('\n⏳ Blocked Tasks:');
    resumable.blockedTasks.forEach(({ task, blockedBy }) => {
      console.log(`\n   ${task.description}`);
      console.log(`   Waiting on: ${blockedBy.join(', ')}`);
    });
  }

  console.log('');
  return resumable.nextTasks;
}

/**
 * Detect project technology stack
 * Usage: yarn context:detect
 */
export async function detectTechnologyStack(): Promise<void> {
  const detector = new TechnologyDetector();
  const stack = await detector.detectStack();

  console.log('\n🔍 Technology Stack Detection');
  console.log('='.repeat(50));

  if (stack.language === 'unknown') {
    console.log('\n❌ No recognized technology stack found');
    console.log('   Supported: Python, Node.js, Go, Rust, Java');
    return;
  }

  console.log(`\n✅ Detected: ${stack.language.toUpperCase()}`);
  console.log(`   Package Manager: ${stack.packageManager}`);
  if (stack.framework) {
    console.log(`   Framework: ${stack.framework}`);
  }
  console.log(`   Project Files: ${stack.projectFiles.join(', ')}`);

  console.log('\n📋 Suggested Agents:');
  stack.suggestedAgents.forEach((agent) => {
    console.log(`   - ${agent}`);
  });

  console.log('');
}

/**
 * Check if a task can start (dependencies satisfied)
 * Usage: yarn context:can-start <task-id>
 */
export function canStartTask(taskId: string): void {
  const hub = new AgentContextHub();
  const result = hub.canStartTask(taskId);

  if (result.canStart) {
    console.log(`✅ Task ${taskId} can start (all dependencies completed)`);
  } else {
    console.log(`⏳ Task ${taskId} is blocked`);
    if (result.blockedBy) {
      console.log(`   Waiting on: ${result.blockedBy.join(', ')}`);
    }
  }
}

/**
 * Get detailed information about a specific task
 * Usage: yarn context:task <task-id>
 */
export function getTaskDetails(taskId: string): void {
  const hub = new AgentContextHub();
  const details = hub.getTaskDetails(taskId);

  if (!details.task) {
    console.log(`❌ Task ${taskId} not found`);
    return;
  }

  const task = details.task;

  console.log('\n📝 Task Details');
  console.log('='.repeat(50));
  console.log(`\nTask ID: ${task.taskId}`);
  console.log(`Description: ${task.description}`);
  console.log(`Assigned to: ${task.assignedTo}`);
  console.log(`Status: ${task.status}`);
  console.log(`Created: ${task.createdAt.toISOString()}`);
  if (task.completedAt) {
    console.log(`Completed: ${task.completedAt.toISOString()}`);
  }

  if (task.dependencies.length > 0) {
    console.log('\nDependencies:');
    details.dependsOn.forEach((dep) => {
      console.log(`  - ${dep.taskId}: ${dep.description} [${dep.status}]`);
    });
  }

  if (details.blockedBy.length > 0) {
    console.log('\n⚠️  Blocked by:');
    details.blockedBy.forEach((dep) => {
      console.log(`  - ${dep.taskId}: ${dep.description} [${dep.status}]`);
    });
  }

  if (details.completion) {
    console.log('\n✅ Completion Artifacts:');
    console.log(`   Files: ${details.completion.files.join(', ')}`);
    if (details.completion.interfaces.length > 0) {
      console.log('   Interfaces:');
      details.completion.interfaces.forEach((iface) => {
        console.log(`     - ${iface.name} (${iface.file})`);
      });
    }
  }

  console.log('');
}

/**
 * Detect conflicts in current orchestration
 * Usage: yarn context:conflicts
 */
export function detectConflicts(): void {
  const hub = new AgentContextHub();
  const conflicts = hub.detectConflicts();

  console.log('\n🔍 Conflict Detection');
  console.log('='.repeat(50));

  if (conflicts.length === 0) {
    console.log('\n✅ No conflicts detected');
    return;
  }

  console.log(`\n⚠️  ${conflicts.length} conflict(s) found:\n`);

  conflicts.forEach((conflict, index) => {
    console.log(`${index + 1}. [${conflict.severity}] ${conflict.category}`);
    console.log(`   ${conflict.description}`);
    console.log(`   Affected tasks: ${conflict.affectedTasks.join(', ')}`);
    if (conflict.suggestedFix) {
      console.log(`   💡 Suggested fix: ${conflict.suggestedFix}`);
    }
    console.log('');
  });
}

// ===========================
// CLI Entry Point
// ===========================

if (require.main === module) {
  const command = process.argv[2];
  const args = process.argv.slice(3);

  try {
    switch (command) {
      case 'register':
        if (args.length < 2) {
          console.error(
            'Usage: context-cli register <description> <agent-name> [dependency-ids...]'
          );
          process.exit(1);
        }
        registerTask(args[0], args[1], args.slice(2));
        break;

      case 'update':
        if (args.length < 2) {
          console.error('Usage: context-cli update <task-id> <status> [artifacts-json]');
          process.exit(1);
        }
        const artifacts = args[2] ? JSON.parse(args[2]) : undefined;
        updateTaskStatus(args[0], args[1] as any, artifacts);
        break;

      case 'status':
        getOrchestrationStatus();
        break;

      case 'next':
        getNextTasks();
        break;

      case 'detect':
        detectTechnologyStack();
        break;

      case 'can-start':
        if (args.length < 1) {
          console.error('Usage: context-cli can-start <task-id>');
          process.exit(1);
        }
        canStartTask(args[0]);
        break;

      case 'task':
        if (args.length < 1) {
          console.error('Usage: context-cli task <task-id>');
          process.exit(1);
        }
        getTaskDetails(args[0]);
        break;

      case 'conflicts':
        detectConflicts();
        break;

      default:
        console.log(`
Context Manager CLI
===================

Available commands:

  register <description> <agent-name> [dep-ids...]  Register a new task
  update <task-id> <status> [artifacts-json]        Update task status
  status                                            Show orchestration status
  next                                              Show next actionable tasks
  detect                                            Detect technology stack
  can-start <task-id>                               Check if task can start
  task <task-id>                                    Show task details
  conflicts                                         Detect conflicts

Examples:

  node context-cli.ts register "Build API" "backend-specialist"
  node context-cli.ts update task-123 completed '{"files":["api.ts"]}'
  node context-cli.ts status
  node context-cli.ts detect
        `);
    }
  } catch (error) {
    console.error('❌ Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}
