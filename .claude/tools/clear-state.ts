#!/usr/bin/env ts-node

/**
 * Clear Orchestration State
 *
 * This script clears all task state, useful for starting fresh
 */

import { AgentContextHub } from '../lib/context-manager';
import * as readline from 'readline';

async function confirm(question: string): Promise<boolean> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes');
    });
  });
}

async function main() {
  const hub = new AgentContextHub();

  const progress = hub.getProgressReport();

  console.log('\n=== Clear Orchestration State ===\n');
  console.log('Current state:');
  console.log(`  Total tasks: ${progress.totalTasks}`);
  console.log(`  Completed: ${progress.byStatus.completed}`);
  console.log(`  In Progress: ${progress.byStatus.in_progress}`);
  console.log(`  Pending: ${progress.byStatus.pending}`);
  console.log('');

  if (progress.totalTasks === 0) {
    console.log('No tasks to clear. State is already empty.\n');
    return;
  }

  const shouldClear = await confirm('Are you sure you want to clear all state? (y/N): ');

  if (shouldClear) {
    hub.clearState();
    console.log('\n✅ State cleared successfully.\n');
  } else {
    console.log('\n❌ Cancelled. State unchanged.\n');
  }
}

if (require.main === module) {
  main().catch(console.error);
}
