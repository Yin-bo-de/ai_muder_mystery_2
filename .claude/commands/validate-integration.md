# Validate Integration Command

Use this command to validate that all agent outputs work together correctly.

## Usage

```
/validate-integration
```

## What this command does:

1. **Checks type interfaces** across all agent implementations
2. **Validates API contracts** between frontend and backend
3. **Detects race conditions** in parallel code
4. **Identifies interface mismatches**
5. **Suggests fixes** for any issues found

## Instructions for Claude

When this command is invoked, you should:

1. **Act as the Integration Validator Agent** - Read and follow [.claude/agents/integration-validator.md](../.claude/agents/integration-validator.md)

2. **Scan the codebase** for:
   - TypeScript interfaces and types
   - API endpoint definitions
   - Frontend API calls
   - Database schemas
   - Error handling patterns

3. **Perform validation checks**:
   - Type interface consistency
   - API contract alignment
   - Data flow validation
   - Concurrency safety
   - Security practices

4. **Report findings** in this format:

   ```json
   {
     "status": "ISSUES_FOUND" | "PASSED",
     "issues": [
       {
         "severity": "HIGH" | "MEDIUM" | "LOW",
         "category": "TYPE_MISMATCH" | "RACE_CONDITION" | "API_CONTRACT" | ...,
         "description": "Clear description",
         "affected_files": ["file:line"],
         "fix": {
           "description": "How to fix",
           "changes": [...]
         }
       }
     ],
     "recommendations": [...]
   }
   ```

5. **Create integration tests** for critical paths if missing

6. **Assign fixes** back to appropriate specialist agents if issues found

## Validation Categories

The validator checks:

- ✅ **Type Safety**: Interface consistency, naming conventions
- ✅ **API Contracts**: Request/response formats, error handling
- ✅ **Data Flow**: Transformations, validation, sanitization
- ✅ **Concurrency**: Race conditions, locking, transactions
- ✅ **Performance**: N+1 queries, indexing, caching
- ✅ **Security**: Auth, validation, injection prevention

## Example

After implementing a user management system:

```
/validate-integration
```

Results might show:

```
ISSUES FOUND:

HIGH: Type mismatch in User interface
  - Backend returns user_id (number)
  - Frontend expects userId (string)
  - Fix: Standardize to userId: string

MEDIUM: Missing error handling
  - Frontend doesn't handle 409 Conflict
  - Backend can return 409 for duplicate email
  - Fix: Add error handler in UserForm component

Recommendations:
  - Add integration tests for duplicate email scenario
  - Create shared types package to prevent drift
```
