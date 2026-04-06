#!/usr/bin/env ts-node

/**
 * View Current Orchestration State
 *
 * This script displays the current state of all tasks, agents, and progress
 */

import { AgentContextHub } from '../lib/context-manager';

function main() {
  const hub = new AgentContextHub();

  console.log('\n=== Claude Orchestra - Current State ===\n');

  // Progress Report
  const progress = hub.getProgressReport();

  console.log('📊 Progress Report:');
  console.log(`   Total Tasks: ${progress.totalTasks}`);
  console.log(`   Completion Rate: ${progress.completionRate.toFixed(1)}%`);
  console.log('\n   Status Breakdown:');
  console.log(`   ✅ Completed: ${progress.byStatus.completed}`);
  console.log(`   🔄 In Progress: ${progress.byStatus.in_progress}`);
  console.log(`   ⏳ Pending: ${progress.byStatus.pending}`);
  console.log(`   ⚠️  Blocked: ${progress.byStatus.blocked}`);

  // Active Agents
  if (progress.activeAgents.length > 0) {
    console.log('\n🤖 Active Agents:');
    progress.activeAgents.forEach((agent: string) => {
      console.log(`   - ${agent}`);
    });
  }

  // Blocked Tasks
  if (progress.blockedTasks.length > 0) {
    console.log('\n⚠️  Blocked Tasks:');
    progress.blockedTasks.forEach((taskId: string) => {
      const task = hub.getTask(taskId);
      if (task) {
        console.log(`   - ${task.description}`);
        const status = hub.canStartTask(taskId);
        if (status.blockedBy) {
          console.log(`     Blocked by: ${status.blockedBy.join(', ')}`);
        }
      }
    });
  }

  // All Tasks
  console.log('\n📋 All Tasks:\n');

  const tasks = hub.getAllTasks();

  if (tasks.length === 0) {
    console.log('   No tasks registered yet.');
    console.log('   Use /orchestrate command in Claude Code to create tasks.\n');
    return;
  }

  tasks.forEach((task: any) => {
    const statusIcons: Record<string, string> = {
      pending: '⏳',
      in_progress: '🔄',
      completed: '✅',
      blocked: '⚠️',
    };
    const statusIcon = statusIcons[task.status] || '❓';

    console.log(`${statusIcon} [${task.status.toUpperCase()}] ${task.description}`);
    console.log(`   Assigned to: ${task.assignedTo}`);
    console.log(`   Task ID: ${task.taskId}`);

    if (task.dependencies.length > 0) {
      console.log(`   Dependencies: ${task.dependencies.join(', ')}`);
    }

    if (task.constraints.length > 0) {
      console.log(`   Constraints: ${task.constraints.join(', ')}`);
    }

    console.log(`   Context: ${task.estimatedContextTokens} tokens`);

    if (task.completedAt) {
      const duration = task.completedAt.getTime() - task.createdAt.getTime();
      console.log(`   Duration: ${Math.round(duration / 1000 / 60)} minutes`);
    }

    console.log('');
  });

  // Context Usage
  const contextUsage = hub.getContextUsage();
  console.log('💾 Context Usage:');
  console.log(`   Total: ${contextUsage.total.toLocaleString()} tokens`);
  console.log(`   Used: ${(contextUsage.total - contextUsage.available).toLocaleString()} tokens`);
  console.log(`   Available: ${contextUsage.available.toLocaleString()} tokens`);

  if (contextUsage.byAgent.size > 0) {
    console.log('\n   By Agent:');
    contextUsage.byAgent.forEach((tokens: number, agent: string) => {
      const percentage = ((tokens / contextUsage.total) * 100).toFixed(1);
      console.log(`   - ${agent}: ${tokens.toLocaleString()} (${percentage}%)`);
    });
  }

  // Conflicts
  const conflicts = hub.getConflicts();

  if (conflicts.length > 0) {
    console.log('\n⚠️  Detected Conflicts:\n');

    conflicts.forEach((conflict: any) => {
      console.log(`   [${conflict.severity}] ${conflict.category}`);
      console.log(`   ${conflict.description}`);
      console.log(`   Affected: ${conflict.affectedTasks.join(', ')}`);

      if (conflict.suggestedFix) {
        console.log(`   Fix: ${conflict.suggestedFix}`);
      }

      console.log('');
    });
  }

  console.log('=== End of Report ===\n');
}

if (require.main === module) {
  main();
}
