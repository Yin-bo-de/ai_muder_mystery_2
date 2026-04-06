# Code Review Severity Guide

This guide provides calibration examples for the code reviewer agent to ensure consistent severity classification across different types of issues.

## Severity Framework

### CRITICAL (P0) - MUST FIX BEFORE DEPLOYMENT

**Definition**: Issues that pose immediate security risks, data corruption, or complete feature failure.

**Impact**: Production incidents, data breaches, system downtime.

**Timeline**: Fix immediately, blocks all deployment.

#### Examples:

**Security Vulnerabilities:**

```python
# ❌ CRITICAL: Passwords stored in plaintext
user.password = request_data['password']
db.save(user)
# Impact: Database breach exposes all user passwords
# Fix: user.password = bcrypt.hashpw(request_data['password'].encode(), bcrypt.gensalt())
```

```typescript
// ❌ CRITICAL: SQL injection vulnerability
db.query(`SELECT * FROM users WHERE email = '${email}'`);
// Impact: Attacker can delete database, steal data
// Fix: db.query('SELECT * FROM users WHERE email = ?', [email]);
```

```python
# ❌ CRITICAL: Missing authentication on sensitive endpoint
@app.post("/api/admin/delete-user")
async def delete_user(user_id: str):
    await db.users.delete(user_id)  # No auth check!
# Impact: Anyone can delete any user
# Fix: Add @require_admin decorator
```

**Data Corruption:**

```typescript
// ❌ CRITICAL: Race condition causes data loss
async function updateDocument(docId, changes) {
  const doc = await getDocument(docId);
  doc.content += changes; // Two simultaneous updates = data loss
  await saveDocument(doc);
}
// Impact: Concurrent edits overwrite each other
// Fix: Use transactions with optimistic locking
```

```python
# ❌ CRITICAL: Incorrect cascade delete
class User(Base):
    posts = relationship("Post", cascade="all, delete")  # Should be delete-orphan
# Impact: Deleting user deletes all their posts permanently
# Fix: Review cascade rules, add soft delete
```

**Complete Feature Failure:**

```go
// ❌ CRITICAL: Panic in request handler crashes server
func handleRequest(w http.ResponseWriter, r *http.Request) {
    data := parseData(r.Body)  // Can panic
    // No recovery mechanism
}
// Impact: Single bad request crashes entire server
// Fix: Add defer recover() or proper error handling
```

---

### MAJOR (P1) - MUST FIX BEFORE RELEASE

**Definition**: Issues that cause significant performance degradation, major bugs, or serious technical debt.

**Impact**: Poor user experience, scalability problems, maintainability issues.

**Timeline**: Fix before release, may block deployment depending on severity.

#### Examples:

**Performance Issues:**

```python
# ❌ MAJOR: N+1 query problem
users = User.query.all()
for user in users:
    user.posts  # Separate query for each user (1000 users = 1000 queries)
# Impact: Page load time goes from 100ms to 10+ seconds
# Fix: users = User.query.options(joinedload(User.posts)).all()
```

```typescript
// ❌ MAJOR: No pagination on list endpoint
app.get('/api/posts', async (req, res) => {
  const posts = await db.posts.findMany(); // Could be millions
  res.json(posts);
});
// Impact: OOM errors, 30+ second response times
// Fix: Add .skip().limit() with pagination
```

```go
// ❌ MAJOR: Memory leak - goroutine never stops
for {
    go func() {
        // Process forever, no context cancellation
        for {
            processItems()
            time.Sleep(1 * time.Second)
        }
    }()
}
// Impact: Server runs out of memory after hours
// Fix: Use context.WithCancel and monitor goroutines
```

**Significant Bugs:**

```typescript
// ❌ MAJOR: Missing error handling for common case
async function getUserProfile(userId: string) {
  const user = await db.users.findUnique({ where: { id: userId } });
  return {
    name: user.name, // Crashes if user not found
    email: user.email,
  };
}
// Impact: 404 page crashes instead of showing error
// Fix: Check if user exists, return 404
```

```python
# ❌ MAJOR: Timezone handling inconsistency
created_at = datetime.now()  # Local timezone
# But frontend expects:
# created_at = datetime.now(timezone.utc)
# Impact: Times off by hours, reports incorrect
# Fix: Always use UTC, convert on client
```

**Technical Debt:**

```typescript
// ❌ MAJOR: Hardcoded configuration
const API_KEY = 'sk_live_abc123...';
const DB_PASSWORD = 'prod_password_2024';
// Impact: Can't deploy to different environments, secrets in repo
// Fix: Use environment variables
```

---

### MINOR (P2) - FIX WHEN CONVENIENT

**Definition**: Code quality issues, minor improvements, low-impact technical debt.

**Impact**: Reduced maintainability, minor confusion, small inefficiencies.

**Timeline**: Fix in next sprint or batch with other work.

#### Examples:

**Code Quality:**

```typescript
// ❌ MINOR: Missing type hints
function processUser(data: any): any {
  return { id: data.id, name: data.name };
}
// Impact: Harder to maintain, potential bugs
// Fix: function processUser(data: UserInput): UserOutput
```

```python
# ❌ MINOR: Unclear variable names
def calc(u, p):
    return u * p * 0.1
# Impact: Hard to understand without context
# Fix: def calculate_discount(unit_price, quantity): ...
```

```go
// ❌ MINOR: Missing docstring
func ProcessOrder(order Order) error {
    // Complex logic...
}
// Impact: Developers need to read code to understand
// Fix: Add comment explaining what this does
```

**Minor Duplication:**

```typescript
// ❌ MINOR: Duplicated validation logic
if (!email.includes('@')) throw new Error('Invalid email');
// ...50 lines later...
if (!email.includes('@')) throw new Error('Invalid email');
// Impact: Changes need to be made in multiple places
// Fix: Extract to validateEmail() function
```

**Minor Inefficiencies:**

```python
# ❌ MINOR: Unnecessary database call
user = User.query.get(user_id)
if user:
    # Only need the ID, but fetched full object
    return user.id
# Impact: Small performance hit
# Fix: Use exists() query or cache user IDs
```

---

### RECOMMENDATIONS - OPTIONAL

**Definition**: Future enhancements, nice-to-haves, optimizations beyond requirements.

**Impact**: Marginal improvements, future-proofing.

**Timeline**: Consider for future sprints, not urgent.

#### Examples:

**Future Enhancements:**

```python
# ✅ RECOMMENDATION: Add request/response logging
@app.middleware("http")
async def log_requests(request, call_next):
    # Could add structured logging for debugging
    response = await call_next(request)
    return response
```

```typescript
// ✅ RECOMMENDATION: Consider Redis caching
async function getPopularPosts() {
  // Works fine, but could cache for 5 minutes
  return await db.posts.findMany({ where: { views: { gt: 1000 } } });
}
```

**Nice-to-Haves:**

```go
// ✅ RECOMMENDATION: Add rate limiting
// Currently no rate limits, works fine for current load
// Consider adding if traffic increases
```

---

## Calibration Examples: Common Scenarios

### Authentication/Authorization

| Issue                                     | Severity           | Why                                 |
| ----------------------------------------- | ------------------ | ----------------------------------- |
| Missing auth check on `/admin/delete-all` | **CRITICAL**       | Anyone can destroy data             |
| Missing auth check on `/api/profile`      | **MAJOR**          | Users can view others' private data |
| Auth token not refreshed automatically    | **MINOR**          | Poor UX but workaround exists       |
| Could add OAuth login option              | **RECOMMENDATION** | Current email/password works fine   |

### Database Operations

| Issue                                 | Severity           | Why                            |
| ------------------------------------- | ------------------ | ------------------------------ |
| Race condition causes data loss       | **CRITICAL**       | Data integrity violation       |
| N+1 queries (10+ seconds page load)   | **MAJOR**          | Unusable performance           |
| Missing index on foreign key          | **MAJOR**          | Slow queries, will get worse   |
| SELECT \* instead of specific columns | **MINOR**          | Small inefficiency             |
| Could add read replica                | **RECOMMENDATION** | Current performance acceptable |

### Error Handling

| Issue                                      | Severity           | Why                          |
| ------------------------------------------ | ------------------ | ---------------------------- |
| Unhandled promise rejection crashes server | **CRITICAL**       | Downtime                     |
| No error handling for "file not found"     | **MAJOR**          | Common case causes 500 error |
| Generic error messages                     | **MINOR**          | Harder to debug              |
| Could add Sentry error tracking            | **RECOMMENDATION** | Logs work fine currently     |

### Security

| Issue                       | Severity           | Why                             |
| --------------------------- | ------------------ | ------------------------------- |
| SQL injection vulnerability | **CRITICAL**       | Database compromise             |
| XSS vulnerability           | **CRITICAL**       | Account takeover                |
| Missing CSRF protection     | **CRITICAL**       | Unauthorized actions            |
| Passwords not rate-limited  | **MAJOR**          | Brute force possible            |
| No HTTPS redirect           | **MAJOR**          | Credentials sent in clear       |
| Weak password requirements  | **MINOR**          | Users can choose weak passwords |
| Could add 2FA               | **RECOMMENDATION** | Nice security enhancement       |

---

## Decision Tree

```
Is there a security vulnerability?
├─ YES → Is it exploitable?
│  ├─ YES → CRITICAL
│  └─ NO → MAJOR (defense in depth)
└─ NO → Continue...

Does it cause data loss or corruption?
├─ YES → CRITICAL
└─ NO → Continue...

Does it cause complete feature failure?
├─ YES → CRITICAL
└─ NO → Continue...

Does it cause significant performance issues?
├─ YES → Is it already affecting users?
│  ├─ YES → MAJOR
│  └─ NO → Will it affect users at scale?
│     ├─ YES → MAJOR
│     └─ NO → MINOR
└─ NO → Continue...

Does it cause bugs in common scenarios?
├─ YES → MAJOR
└─ NO → Continue...

Is it a code quality issue?
├─ YES → MINOR
└─ NO → RECOMMENDATION
```

---

## When in Doubt

**Err on the side of higher severity for:**

- Security issues (can always downgrade after expert review)
- Data integrity issues
- Issues affecting many users
- Issues with no workaround

**Err on the side of lower severity for:**

- Cosmetic issues
- Issues with easy workarounds
- Issues affecting edge cases
- Optimizations beyond requirements

**Remember**: The goal is to prevent production incidents while not blocking progress on subjective preferences. When unsure, explain your reasoning in the issue description.
