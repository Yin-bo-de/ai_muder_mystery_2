/**
 * Agent Context Management System (Layer 2)
 *
 * This system maintains state across all agents without mixing implementation details.
 * It provides:
 * - Task registration and tracking
 * - Inter-agent dependency management
 * - Structured handoff protocols
 * - Context window allocation
 * - Conflict detection
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import { join } from 'path';
import { glob } from 'glob';
import { parse as parseToml } from 'smol-toml';

// ===========================
// Type Definitions
// ===========================

export interface TechnologyStack {
  language: 'python' | 'nodejs' | 'go' | 'rust' | 'java' | 'unknown';
  packageManager: string;
  framework?: string;
  projectFiles: string[];
  suggestedAgents: string[];
}

export interface AgentRegistry {
  language: string;
  packageFiles: string[];
  packageManager: string;
  agents: string[];
  frameworkDetection?: (dependencies: string[]) => string | undefined;
}

export interface Task {
  taskId: string;
  description: string;
  assignedTo: string;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  dependencies: string[];
  interfaces: Record<string, string>;
  constraints: string[];
  estimatedContextTokens: number;
  createdAt: Date;
  completedAt?: Date;
  artifacts?: AgentArtifact;
}

export type InterfaceDefinition = any;
export type CompletionHandoff = AgentArtifact;

export interface AgentArtifact {
  agentId: string;
  taskId: string;
  files: string[];
  interfaces: Array<{ name: string; file: string }>;
  completedAt: Date;
  metadata: Record<string, any>;
}

export interface HandoffProtocol {
  fromAgent: string;
  toAgent: string;
  taskId: string;
  artifacts: {
    interfaces: Record<string, string>;
    implementationNotes: Record<string, string>;
    dependencies: string[];
    testRequirements: string[];
  };
  contextBudget: number;
}

export interface ConflictIssue {
  id: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  category: string;
  description: string;
  affectedTasks: string[];
  suggestedFix?: string;
  detectedAt: Date;
}

// ===========================
// Technology Detection Registry
// ===========================

const TECHNOLOGY_REGISTRY: Record<string, AgentRegistry> = {
  python: {
    language: 'python',
    packageFiles: ['pyproject.toml', 'requirements.txt', 'setup.py'],
    packageManager: 'uv', // Modern default
    agents: ['backend-python-specialist', 'ml-specialist'],
    frameworkDetection: (dependencies: string[]) => {
      if (dependencies.some((d) => d.includes('fastapi'))) return 'fastapi';
      if (dependencies.some((d) => d.includes('django'))) return 'django';
      if (dependencies.some((d) => d.includes('flask'))) return 'flask';
      if (
        dependencies.some(
          (d) => d.includes('torch') || d.includes('tensorflow') || d.includes('sklearn')
        )
      ) {
        return 'ml';
      }
      return undefined;
    },
  },
  nodejs: {
    language: 'nodejs',
    packageFiles: ['package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock'],
    packageManager: 'npm', // Or pnpm/yarn based on lock file
    agents: ['backend-nodejs-specialist', 'frontend-specialist'],
    frameworkDetection: (dependencies: string[]) => {
      if (dependencies.some((d) => d.includes('express'))) return 'express';
      if (dependencies.some((d) => d.includes('fastify'))) return 'fastify';
      if (dependencies.some((d) => d.includes('nestjs'))) return 'nestjs';
      if (dependencies.some((d) => d.includes('react'))) return 'react';
      if (dependencies.some((d) => d.includes('vue'))) return 'vue';
      if (dependencies.some((d) => d.includes('next'))) return 'nextjs';
      return undefined;
    },
  },
  go: {
    language: 'go',
    packageFiles: ['go.mod', 'go.sum'],
    packageManager: 'go modules',
    agents: ['backend-go-specialist'],
    frameworkDetection: (dependencies: string[]) => {
      if (dependencies.some((d) => d.includes('gin-gonic/gin'))) return 'gin';
      if (dependencies.some((d) => d.includes('labstack/echo'))) return 'echo';
      if (dependencies.some((d) => d.includes('gorilla/mux'))) return 'gorilla';
      return undefined;
    },
  },
  rust: {
    language: 'rust',
    packageFiles: ['Cargo.toml', 'Cargo.lock'],
    packageManager: 'cargo',
    agents: ['backend-rust-specialist'],
    frameworkDetection: (dependencies: string[]) => {
      if (dependencies.some((d) => d.includes('axum'))) return 'axum';
      if (dependencies.some((d) => d.includes('actix-web'))) return 'actix-web';
      if (dependencies.some((d) => d.includes('rocket'))) return 'rocket';
      return undefined;
    },
  },
  java: {
    language: 'java',
    packageFiles: ['pom.xml', 'build.gradle', 'build.gradle.kts'],
    packageManager: 'maven/gradle',
    agents: ['backend-java-specialist'],
    frameworkDetection: (dependencies: string[]) => {
      if (dependencies.some((d) => d.includes('spring-boot'))) return 'spring-boot';
      if (dependencies.some((d) => d.includes('quarkus'))) return 'quarkus';
      if (dependencies.some((d) => d.includes('micronaut'))) return 'micronaut';
      return undefined;
    },
  },
};

// ===========================
// Technology Detection Functions
// ===========================

export class TechnologyDetector {
  private projectRoot: string;

  constructor(projectRoot: string = '.') {
    this.projectRoot = projectRoot;
  }

  /**
   * Detect the technology stack of the project
   */
  async detectStack(): Promise<TechnologyStack> {
    // Check for each known stack
    for (const [key, registry] of Object.entries(TECHNOLOGY_REGISTRY)) {
      const detectedFiles = this.findProjectFiles(registry.packageFiles);

      if (detectedFiles.length > 0) {
        const dependencies = await this.extractDependencies(detectedFiles[0], key);
        const framework = registry.frameworkDetection?.(dependencies);

        // Determine which agents to use based on framework
        let suggestedAgents = [...registry.agents];

        // Special handling for Python: choose between backend and ML
        if (key === 'python' && framework) {
          if (framework === 'ml') {
            suggestedAgents = ['ml-specialist'];
          } else if (['fastapi', 'django', 'flask'].includes(framework)) {
            suggestedAgents = ['backend-python-specialist'];
          }
        }

        // Special handling for Node.js: choose between backend and frontend
        if (key === 'nodejs' && framework) {
          if (['express', 'fastify', 'nestjs'].includes(framework)) {
            suggestedAgents = ['backend-nodejs-specialist'];
          } else if (['react', 'vue', 'nextjs'].includes(framework)) {
            suggestedAgents = ['frontend-specialist'];
          }
        }

        return {
          language: key as any,
          packageManager: registry.packageManager,
          framework,
          projectFiles: detectedFiles,
          suggestedAgents,
        };
      }
    }

    return {
      language: 'unknown',
      packageManager: 'unknown',
      projectFiles: [],
      suggestedAgents: [],
    };
  }

  /**
   * Find project files that match the given patterns
   */
  private findProjectFiles(patterns: string[]): string[] {
    const found: string[] = [];

    for (const pattern of patterns) {
      const filePath = join(this.projectRoot, pattern);
      if (existsSync(filePath)) {
        found.push(filePath);
      }
    }

    return found;
  }

  /**
   * Extract dependencies from project files using proper parsers
   */
  private async extractDependencies(filePath: string, language: string): Promise<string[]> {
    try {
      const content = readFileSync(filePath, 'utf-8');

      if (language === 'python') {
        if (filePath.endsWith('pyproject.toml')) {
          // Use proper TOML parser
          const parsed = parseToml(content) as any;
          const deps: string[] = [];

          // Standard dependencies
          if (parsed.project?.dependencies && Array.isArray(parsed.project.dependencies)) {
            deps.push(
              ...parsed.project.dependencies.map((d: string) => d.split(/[<>=!]/)[0].trim())
            );
          }

          // Optional dependencies
          if (parsed.project?.['optional-dependencies']) {
            for (const group of Object.values(parsed.project['optional-dependencies'])) {
              if (Array.isArray(group)) {
                deps.push(...group.map((d: string) => d.split(/[<>=!]/)[0].trim()));
              }
            }
          }

          return [...new Set(deps)]; // Deduplicate
        } else if (filePath.endsWith('requirements.txt')) {
          return content
            .split('\n')
            .map((line) => line.trim())
            .filter((line) => line && !line.startsWith('#'))
            .map((line) => line.split(/[<>=!]/)[0].trim());
        }
      } else if (language === 'nodejs') {
        const packageJson = JSON.parse(content);
        return [
          ...Object.keys(packageJson.dependencies || {}),
          ...Object.keys(packageJson.devDependencies || {}),
        ];
      } else if (language === 'go') {
        // Parse go.mod - extract module paths from require blocks
        const lines = content.split('\n');
        const deps: string[] = [];
        let inRequire = false;

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('require (')) {
            inRequire = true;
            continue;
          }
          if (inRequire && trimmed === ')') {
            inRequire = false;
            continue;
          }
          if (inRequire || trimmed.startsWith('require ')) {
            const match = trimmed.match(/^(?:require\s+)?([^\s]+)/);
            if (match && match[1] && !match[1].startsWith('//')) {
              deps.push(match[1]);
            }
          }
        }
        return deps;
      } else if (language === 'rust') {
        // Use proper TOML parser for Cargo.toml
        const parsed = parseToml(content);
        const deps: string[] = [];

        if (parsed.dependencies) {
          deps.push(...Object.keys(parsed.dependencies));
        }
        if (parsed['dev-dependencies']) {
          deps.push(...Object.keys(parsed['dev-dependencies']));
        }
        if (parsed['build-dependencies']) {
          deps.push(...Object.keys(parsed['build-dependencies']));
        }

        return deps;
      } else if (language === 'java') {
        // XML (Maven pom.xml) or Gradle dependency extraction
        const depMatches =
          content.match(/<artifactId>(.*?)<\/artifactId>/g) ||
          content.match(/implementation\s+["'](.+?)["']/g) ||
          [];
        return depMatches.map((m) =>
          m
            .replace(/<\/?artifactId>/g, '')
            .replace(/implementation\s+["']/g, '')
            .replace(/["']/g, '')
        );
      }

      return [];
    } catch (error) {
      console.error(`Error extracting dependencies from ${filePath}:`, error);
      return [];
    }
  }

  /**
   * Get agent recommendations based on detected stack and task description
   */
  getAgentRecommendations(stack: TechnologyStack, taskDescription: string): string[] {
    const recommendations = [...stack.suggestedAgents];

    // Add additional agents based on task description
    const lowerTask = taskDescription.toLowerCase();

    if (lowerTask.includes('test') || lowerTask.includes('testing')) {
      recommendations.push('test-specialist');
    }

    if (
      lowerTask.includes('database') ||
      lowerTask.includes('schema') ||
      lowerTask.includes('migration')
    ) {
      recommendations.push('database-specialist');
    }

    if (lowerTask.includes('validate') || lowerTask.includes('integration')) {
      recommendations.push('integration-validator');
    }

    return [...new Set(recommendations)]; // Remove duplicates
  }
}

// ===========================
// Context Hub
// ===========================

export class AgentContextHub {
  private statePath: string;
  private projectState: {
    architecture: Record<string, any>;
    tasks: Map<string, Task>;
    dependencies: Map<string, string[]>;
    completions: Map<string, AgentArtifact>;
    interfaces: Map<string, any>;
    conflicts: ConflictIssue[];
    contextAllocations: Map<string, number>;
  };

  constructor(statePath: string = './.claude/state') {
    this.statePath = statePath;

    // Ensure state directory exists
    if (!existsSync(statePath)) {
      mkdirSync(statePath, { recursive: true });
    }

    // Load or initialize state
    this.projectState = this.loadState();
  }

  // ===========================
  // Task Management
  // ===========================

  registerTask(spec: {
    description: string;
    assignedTo: string;
    dependencies?: string[];
    interfaces?: Record<string, string>;
    constraints?: string[];
    estimatedContextTokens?: number;
  }): Task {
    const taskId = this.generateTaskId();

    const task: Task = {
      taskId,
      description: spec.description,
      assignedTo: spec.assignedTo,
      status: 'pending',
      dependencies: spec.dependencies || [],
      interfaces: spec.interfaces || {},
      constraints: spec.constraints || [],
      estimatedContextTokens: spec.estimatedContextTokens || 8000,
      createdAt: new Date(),
    };

    this.projectState.tasks.set(taskId, task);

    // Register dependencies
    if (task.dependencies.length > 0) {
      this.projectState.dependencies.set(taskId, task.dependencies);
    }

    // Allocate context window
    this.projectState.contextAllocations.set(task.assignedTo, task.estimatedContextTokens);

    this.saveState();

    return task;
  }

  updateTaskStatus(
    taskId: string,
    status: Task['status'],
    artifacts?: Partial<AgentArtifact>
  ): void {
    const task = this.projectState.tasks.get(taskId);

    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }

    task.status = status;

    if (status === 'completed') {
      task.completedAt = new Date();

      // Store completion artifacts
      if (artifacts) {
        const artifact: AgentArtifact = {
          agentId: task.assignedTo,
          taskId,
          files: artifacts.files || [],
          interfaces: artifacts.interfaces || [],
          completedAt: new Date(),
          metadata: artifacts.metadata || {},
        };

        this.projectState.completions.set(taskId, artifact);

        // Also store artifacts on the task object
        task.artifacts = artifact;

        // Extract and store interfaces
        artifact.interfaces.forEach((iface) => {
          this.projectState.interfaces.set(iface.name, {
            file: iface.file,
            taskId,
            agentId: task.assignedTo,
          });
        });
      }
    }

    this.saveState();
  }

  getTask(taskId: string): Task | undefined {
    return this.projectState.tasks.get(taskId);
  }

  getAllTasks(): Task[] {
    return Array.from(this.projectState.tasks.values());
  }

  getTasksByStatus(status: Task['status']): Task[] {
    return Array.from(this.projectState.tasks.values()).filter((task) => task.status === status);
  }

  getTasksByAgent(agentId: string): Task[] {
    return Array.from(this.projectState.tasks.values()).filter(
      (task) => task.assignedTo === agentId
    );
  }

  // ===========================
  // Dependency Management
  // ===========================

  canStartTask(taskId: string): { canStart: boolean; blockedBy?: string[] } {
    const task = this.projectState.tasks.get(taskId);

    if (!task) {
      return { canStart: false };
    }

    if (task.dependencies.length === 0) {
      return { canStart: true };
    }

    const blockedBy: string[] = [];

    for (const depId of task.dependencies) {
      const depTask = this.projectState.tasks.get(depId);

      if (!depTask || depTask.status !== 'completed') {
        blockedBy.push(depId);
      }
    }

    return {
      canStart: blockedBy.length === 0,
      blockedBy: blockedBy.length > 0 ? blockedBy : undefined,
    };
  }

  getDependencyGraph(): Map<string, string[]> {
    return this.projectState.dependencies;
  }

  // ===========================
  // Handoff Protocol
  // ===========================

  prepareHandoff(fromTaskId: string, toAgent: string): HandoffProtocol {
    const fromTask = this.projectState.tasks.get(fromTaskId);

    if (!fromTask) {
      throw new Error(`Task ${fromTaskId} not found`);
    }

    const artifact = this.projectState.completions.get(fromTaskId);

    if (!artifact) {
      throw new Error(`No completion artifacts for task ${fromTaskId}`);
    }

    // Calculate available context budget
    const totalContext = 200000; // Claude's context window
    const orchestratorContext = 10000;
    const reservedContext = 20000;
    const usedContext = Array.from(this.projectState.contextAllocations.values()).reduce(
      (sum, val) => sum + val,
      0
    );

    const availableContext = totalContext - orchestratorContext - reservedContext - usedContext;

    // Build handoff protocol
    const handoff: HandoffProtocol = {
      fromAgent: fromTask.assignedTo,
      toAgent,
      taskId: fromTaskId,
      artifacts: {
        interfaces: this.extractRelevantInterfaces(toAgent),
        implementationNotes: artifact.metadata.notes || {},
        dependencies: artifact.metadata.dependencies || [],
        testRequirements: artifact.metadata.testRequirements || [],
      },
      contextBudget: Math.min(availableContext, 30000),
    };

    return handoff;
  }

  private extractRelevantInterfaces(agentId: string): Record<string, string> {
    const relevant: Record<string, string> = {};

    // Get interfaces that this agent needs to know about
    this.projectState.interfaces.forEach((value, key) => {
      // Include all shared interfaces
      relevant[key] = value.file;
    });

    return relevant;
  }

  // ===========================
  // Context Management
  // ===========================

  allocateContextWindow(agentId: string, tokens: number): void {
    this.projectState.contextAllocations.set(agentId, tokens);
    this.saveState();
  }

  getContextUsage(): {
    total: number;
    byAgent: Map<string, number>;
    available: number;
  } {
    const totalContext = 200000;
    const used = Array.from(this.projectState.contextAllocations.values()).reduce(
      (sum, val) => sum + val,
      0
    );

    return {
      total: totalContext,
      byAgent: new Map(this.projectState.contextAllocations),
      available: totalContext - used,
    };
  }

  // ===========================
  // Conflict Detection
  // ===========================

  detectConflicts(): ConflictIssue[] {
    const conflicts: ConflictIssue[] = [];

    // Check for interface conflicts
    const interfaceConflicts = this.detectInterfaceConflicts();
    conflicts.push(...interfaceConflicts);

    // Check for dependency conflicts
    const dependencyConflicts = this.detectDependencyConflicts();
    conflicts.push(...dependencyConflicts);

    // Store conflicts
    this.projectState.conflicts = conflicts;
    this.saveState();

    return conflicts;
  }

  private detectInterfaceConflicts(): ConflictIssue[] {
    // TODO: Implement interface conflict detection
    // This would parse TypeScript files and compare interface definitions
    return [];
  }

  private detectDependencyConflicts(): ConflictIssue[] {
    const conflicts: ConflictIssue[] = [];

    // Check for circular dependencies
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const hasCycle = (taskId: string): boolean => {
      visited.add(taskId);
      recursionStack.add(taskId);

      const dependencies = this.projectState.dependencies.get(taskId) || [];

      for (const depId of dependencies) {
        if (!visited.has(depId)) {
          if (hasCycle(depId)) {
            return true;
          }
        } else if (recursionStack.has(depId)) {
          conflicts.push({
            id: `circular-dep-${Date.now()}`,
            severity: 'HIGH',
            category: 'CIRCULAR_DEPENDENCY',
            description: `Circular dependency detected: ${taskId} -> ${depId}`,
            affectedTasks: [taskId, depId],
            detectedAt: new Date(),
          });
          return true;
        }
      }

      recursionStack.delete(taskId);
      return false;
    };

    this.projectState.tasks.forEach((_, taskId) => {
      if (!visited.has(taskId)) {
        hasCycle(taskId);
      }
    });

    return conflicts;
  }

  getConflicts(): ConflictIssue[] {
    return this.projectState.conflicts;
  }

  // ===========================
  // Reporting
  // ===========================

  getProgressReport(): {
    totalTasks: number;
    byStatus: Record<Task['status'], number>;
    completionRate: number;
    blockedTasks: string[];
    activeAgents: string[];
  } {
    const tasks = Array.from(this.projectState.tasks.values());

    const byStatus = {
      pending: 0,
      in_progress: 0,
      completed: 0,
      blocked: 0,
    };

    const blockedTasks: string[] = [];
    const activeAgents = new Set<string>();

    tasks.forEach((task) => {
      byStatus[task.status]++;

      if (task.status === 'blocked') {
        blockedTasks.push(task.taskId);
      }

      if (task.status === 'in_progress') {
        activeAgents.add(task.assignedTo);
      }
    });

    const completionRate = tasks.length > 0 ? (byStatus.completed / tasks.length) * 100 : 0;

    return {
      totalTasks: tasks.length,
      byStatus,
      completionRate,
      blockedTasks,
      activeAgents: Array.from(activeAgents),
    };
  }

  /**
   * Get comprehensive orchestration status for tracking progress
   */
  getOrchestrationStatus(): {
    progress: {
      totalTasks: number;
      byStatus: Record<Task['status'], number>;
      completionRate: number;
      blockedTasks: string[];
      activeAgents: string[];
    };
    tasks: Array<{
      taskId: string;
      description: string;
      status: Task['status'];
      assignedTo: string;
      dependencies: string[];
      artifacts?: Task['artifacts'];
    }>;
    conflicts: ConflictIssue[];
    interfaces: Array<{ name: string; definition: InterfaceDefinition }>;
  } {
    const tasks = Array.from(this.projectState.tasks.values());
    const interfaces = Array.from(this.projectState.interfaces.entries()).map(
      ([name, definition]) => ({ name, definition })
    );

    return {
      progress: this.getProgressReport(),
      tasks: tasks.map((task) => ({
        taskId: task.taskId,
        description: task.description,
        status: task.status,
        assignedTo: task.assignedTo,
        dependencies: task.dependencies,
        artifacts: task.artifacts,
      })),
      conflicts: this.projectState.conflicts,
      interfaces,
    };
  }

  /**
   * Get detailed information for a specific task
   */
  getTaskDetails(taskId: string): {
    task: Task | undefined;
    dependsOn: Task[];
    blockedBy: Task[];
    completion?: CompletionHandoff;
  } {
    const task = this.getTask(taskId);
    if (!task) {
      return {
        task: undefined,
        dependsOn: [],
        blockedBy: [],
      };
    }

    const dependsOn = task.dependencies
      .map((depId) => this.getTask(depId))
      .filter((t): t is Task => t !== undefined);

    const blockedBy = dependsOn.filter((t) => t.status !== 'completed');

    return {
      task,
      dependsOn,
      blockedBy,
      completion: this.projectState.completions.get(taskId),
    };
  }

  /**
   * Get information needed to resume an orchestration session
   */
  getResumableOrchestration(): {
    hasState: boolean;
    progress: {
      totalTasks: number;
      byStatus: Record<Task['status'], number>;
      completionRate: number;
      blockedTasks: string[];
      activeAgents: string[];
    } | null;
    nextTasks: Task[];
    blockedTasks: Array<{ task: Task; blockedBy: string[] }>;
  } {
    const tasks = Array.from(this.projectState.tasks.values());
    if (tasks.length === 0) {
      return {
        hasState: false,
        progress: null,
        nextTasks: [],
        blockedTasks: [],
      };
    }

    const progress = this.getProgressReport();

    // Find next tasks that can be started (pending with no incomplete dependencies)
    const nextTasks = tasks.filter((task) => {
      if (task.status !== 'pending') return false;
      return task.dependencies.every((depId) => {
        const dep = this.getTask(depId);
        return dep?.status === 'completed';
      });
    });

    // Find blocked tasks with their blocking dependencies
    const blockedTasks = tasks
      .filter((task) => task.status === 'blocked' || task.status === 'pending')
      .map((task) => {
        const blockedBy = task.dependencies.filter((depId) => {
          const dep = this.getTask(depId);
          return dep?.status !== 'completed';
        });
        return { task, blockedBy };
      })
      .filter((item) => item.blockedBy.length > 0);

    return {
      hasState: true,
      progress,
      nextTasks,
      blockedTasks,
    };
  }

  // ===========================
  // State Persistence
  // ===========================

  private loadState(): typeof this.projectState {
    const stateFile = join(this.statePath, 'context-state.json');

    if (existsSync(stateFile)) {
      try {
        const data = JSON.parse(readFileSync(stateFile, 'utf-8'));

        return {
          architecture: data.architecture || {},
          tasks: new Map(Object.entries(data.tasks || {})),
          dependencies: new Map(Object.entries(data.dependencies || {})),
          completions: new Map(Object.entries(data.completions || {})),
          interfaces: new Map(Object.entries(data.interfaces || {})),
          conflicts: data.conflicts || [],
          contextAllocations: new Map(Object.entries(data.contextAllocations || {})),
        };
      } catch (error) {
        console.error('Failed to load state, initializing fresh:', error);
      }
    }

    return {
      architecture: {},
      tasks: new Map(),
      dependencies: new Map(),
      completions: new Map(),
      interfaces: new Map(),
      conflicts: [],
      contextAllocations: new Map(),
    };
  }

  private saveState(): void {
    const stateFile = join(this.statePath, 'context-state.json');

    const data = {
      architecture: this.projectState.architecture,
      tasks: Object.fromEntries(this.projectState.tasks),
      dependencies: Object.fromEntries(this.projectState.dependencies),
      completions: Object.fromEntries(this.projectState.completions),
      interfaces: Object.fromEntries(this.projectState.interfaces),
      conflicts: this.projectState.conflicts,
      contextAllocations: Object.fromEntries(this.projectState.contextAllocations),
    };

    writeFileSync(stateFile, JSON.stringify(data, null, 2));
  }

  clearState(): void {
    this.projectState = {
      architecture: {},
      tasks: new Map(),
      dependencies: new Map(),
      completions: new Map(),
      interfaces: new Map(),
      conflicts: [],
      contextAllocations: new Map(),
    };

    this.saveState();
  }

  // ===========================
  // Utilities
  // ===========================

  private generateTaskId(): string {
    return `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// ===========================
// Wave Orchestrator
// ===========================

export class WaveOrchestrator {
  private contextHub: AgentContextHub;
  private maxContextPerWave: number = 100000;

  constructor(contextHub: AgentContextHub) {
    this.contextHub = contextHub;
  }

  deployWaves(tasks: Task[]): Task[][] {
    const waves: Task[][] = [];
    let currentWave: Task[] = [];
    let contextBudget = 0;

    // Sort tasks by dependencies (topological sort)
    const sortedTasks = this.topologicalSort(tasks);

    for (const task of sortedTasks) {
      const estimatedContext = task.estimatedContextTokens;

      if (contextBudget + estimatedContext > this.maxContextPerWave) {
        // Start new wave
        waves.push(currentWave);
        currentWave = [task];
        contextBudget = estimatedContext;
      } else {
        currentWave.push(task);
        contextBudget += estimatedContext;
      }
    }

    if (currentWave.length > 0) {
      waves.push(currentWave);
    }

    return waves;
  }

  private topologicalSort(tasks: Task[]): Task[] {
    const sorted: Task[] = [];
    const visited = new Set<string>();
    const tempMark = new Set<string>();

    const visit = (taskId: string) => {
      if (tempMark.has(taskId)) {
        throw new Error(`Circular dependency detected involving ${taskId}`);
      }

      if (!visited.has(taskId)) {
        tempMark.add(taskId);

        const task = this.contextHub.getTask(taskId);
        if (task) {
          task.dependencies.forEach((depId) => visit(depId));
          visited.add(taskId);
          sorted.push(task);
        }

        tempMark.delete(taskId);
      }
    };

    tasks.forEach((task) => {
      if (!visited.has(task.taskId)) {
        visit(task.taskId);
      }
    });

    return sorted;
  }
}

// ===========================
// Example Usage
// ===========================

// NOTE: Example code commented out - use the CLI instead (npx claude-orchestra <command>)
if (false && require.main === module) {
  // Initialize context hub
  const hub = new AgentContextHub();

  // Register tasks
  const task1 = hub.registerTask({
    description: 'Define TypeScript interfaces',
    assignedTo: 'types-specialist',
    estimatedContextTokens: 5000,
  });

  const task2 = hub.registerTask({
    description: 'Implement backend API',
    assignedTo: 'backend-specialist',
    dependencies: [task1.taskId],
    estimatedContextTokens: 15000,
  });

  const task3 = hub.registerTask({
    description: 'Implement frontend components',
    assignedTo: 'frontend-specialist',
    dependencies: [task1.taskId],
    estimatedContextTokens: 15000,
  });

  const task4 = hub.registerTask({
    description: 'Write integration tests',
    assignedTo: 'test-specialist',
    dependencies: [task2.taskId, task3.taskId],
    estimatedContextTokens: 10000,
  });

  // Check if tasks can start
  console.log('Task 1 can start:', hub.canStartTask(task1.taskId));
  console.log('Task 2 can start:', hub.canStartTask(task2.taskId));

  // Complete task 1
  hub.updateTaskStatus(task1.taskId, 'completed', {
    files: ['src/types/user.ts'],
    interfaces: [{ name: 'User', file: 'src/types/user.ts' }],
    metadata: {
      notes: { critical: 'All IDs are strings (UUIDs)' },
    },
  });

  // Check again
  console.log('Task 2 can start:', hub.canStartTask(task2.taskId));

  // Get progress report
  console.log('Progress:', hub.getProgressReport());

  // Deploy in waves
  const waveOrch = new WaveOrchestrator(hub);
  const waves = waveOrch.deployWaves(hub.getAllTasks());

  console.log(`Deploying in ${waves.length} waves:`);
  waves.forEach((wave, i) => {
    console.log(
      `Wave ${i + 1}:`,
      wave.map((t) => t.description)
    );
  });
}
