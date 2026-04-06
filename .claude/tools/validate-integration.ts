#!/usr/bin/env tsx
/**
 * Integration Validation Tool
 *
 * Validates the integrity of the claude-orchestra system:
 * - Verifies core files exist
 * - Checks context manager can be imported
 * - Validates agent definitions are present
 */

import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { glob } from 'glob';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '../..');

interface ValidationResult {
  passed: boolean;
  message: string;
}

async function validate(): Promise<void> {
  console.log('🔍 Validating claude-orchestra integration...\n');

  const results: ValidationResult[] = [];

  // Check 1: Core library files
  const coreFiles = [
    '.claude/lib/context-manager.ts',
    '.claude/commands/orchestrate.md',
    '.claude/commands/validate-integration.md',
  ];

  for (const file of coreFiles) {
    const path = join(projectRoot, file);
    const exists = existsSync(path);
    results.push({
      passed: exists,
      message: `Core file: ${file}`,
    });
  }

  // Check 2: Agent definitions exist
  const agentFiles = await glob('.claude/agents/*.md', {
    cwd: projectRoot,
    absolute: false,
  });

  const requiredAgents = [
    'orchestrator.md',
    'frontend-specialist.md',
    'integration-validator.md',
    'code-reviewer.md',
  ];

  for (const agent of requiredAgents) {
    const exists = agentFiles.some((f) => f.endsWith(agent));
    results.push({
      passed: exists,
      message: `Agent definition: ${agent}`,
    });
  }

  // Check 3: Context manager can be imported
  try {
    const { AgentContextHub } = await import('../lib/context-manager');
    const hub = new AgentContextHub();
    results.push({
      passed: true,
      message: 'Context manager import and instantiation',
    });
  } catch (error) {
    results.push({
      passed: false,
      message: `Context manager import failed: ${error}`,
    });
  }

  // Check 4: TypeScript build artifacts exist (after build)
  const distExists = existsSync(join(projectRoot, 'dist'));
  results.push({
    passed: distExists,
    message: 'TypeScript build artifacts (dist/)',
  });

  // Print results
  console.log('Validation Results:');
  console.log('─'.repeat(60));

  let allPassed = true;
  for (const result of results) {
    const icon = result.passed ? '✅' : '❌';
    console.log(`${icon} ${result.message}`);
    if (!result.passed) {
      allPassed = false;
    }
  }

  console.log('─'.repeat(60));

  if (allPassed) {
    console.log('\n✨ All validation checks passed!\n');
    process.exit(0);
  } else {
    console.log('\n❌ Some validation checks failed. See errors above.\n');
    process.exit(1);
  }
}

// Run validation
validate().catch((error) => {
  console.error('❌ Validation failed with error:', error);
  process.exit(1);
});
