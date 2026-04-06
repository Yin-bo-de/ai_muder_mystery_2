# Security Checklist for All Backend Specialists

This checklist applies to all backend implementations regardless of language.

## Authentication & Authorization

- [ ] All protected endpoints require authentication
- [ ] Authorization checks verify user can access specific resources
- [ ] Session tokens are cryptographically secure
- [ ] Sessions expire appropriately
- [ ] Password reset flows are secure (time-limited tokens)

## Input Validation & Injection Prevention

- [ ] **SQL Injection**: Use parameterized queries/ORM (NEVER string concatenation)
- [ ] **XSS Prevention**: Escape user input in output, set CSP headers
- [ ] **Command Injection**: Never pass user input to shell commands
- [ ] **Path Traversal**: Validate file paths, no `../` in user input
- [ ] All user input validated at API boundary
- [ ] Use validation libraries (Zod, Joi, Pydantic, Bean Validation)

## Password & Secrets Management

- [ ] Passwords hashed with bcrypt/argon2 (work factor ≥10)
- [ ] NEVER store passwords in plaintext
- [ ] Secrets in environment variables (not hardcoded)
- [ ] No API keys, tokens, or credentials in code
- [ ] Use secret management systems in production (Vault, AWS Secrets Manager)

## CSRF & Request Security

- [ ] CSRF tokens on all state-changing requests (POST, PUT, DELETE)
- [ ] SameSite cookie attribute set appropriately
- [ ] CORS configured correctly (not `Access-Control-Allow-Origin: *` in production)
- [ ] Rate limiting on sensitive endpoints (login, password reset, API endpoints)

## Data Protection

- [ ] Sensitive data encrypted at rest
- [ ] Sensitive data encrypted in transit (HTTPS/TLS)
- [ ] Don't return sensitive data in responses (passwords, internal IDs, tokens)
- [ ] Audit logs for sensitive operations
- [ ] Personal data handling follows privacy regulations (GDPR, CCPA)

## Dependency Security

- [ ] No dependencies with known CVEs
- [ ] Dependencies regularly updated
- [ ] Use lock files (package-lock.json, requirements.txt, go.sum)
- [ ] Scan for vulnerabilities (npm audit, pip-audit, etc.)

## Error Handling

- [ ] Don't expose stack traces to users
- [ ] Log errors with context (but not sensitive data)
- [ ] Return generic error messages to users
- [ ] Internal errors return 500, not detailed error info

## Language-Specific

### Python

- [ ] Use `secrets` module for tokens (not `random`)
- [ ] Validate with Pydantic schemas
- [ ] SQL: Use SQLAlchemy/Django ORM parameterized queries

### Node.js/TypeScript

- [ ] Use `crypto.randomBytes()` for tokens
- [ ] Validate with Zod/Joi
- [ ] SQL: Use Prisma/TypeORM parameterized queries
- [ ] Set security headers with helmet

### Go

- [ ] Use `crypto/rand` for tokens
- [ ] Validate with struct tags or validator package
- [ ] SQL: Use prepared statements with `database/sql`

### Rust

- [ ] Use `rand::thread_rng()` from rand crate
- [ ] Validate with validator crate
- [ ] SQL: Use sqlx with query macros (compile-time checked)

### Java

- [ ] Use `SecureRandom` for tokens
- [ ] Validate with Bean Validation
- [ ] SQL: Use JPA/Hibernate (never raw JDBC strings)
- [ ] Set Spring Security headers

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- Language-specific security guides in each specialist definition
