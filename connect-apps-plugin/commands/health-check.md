---
description: Run a health check on all connected app integrations to verify configuration and security
---

Perform a health check on all connected apps and integrations in the project:

1. **Configuration check**: Verify all required environment variables are documented and have fallbacks
2. **Security audit**: Flag any hardcoded API keys, tokens, or secrets in source code
3. **Error handling**: Check that API calls have proper error handling, timeouts, and retries
4. **Dependency check**: Verify that HTTP client libraries and SDKs are up-to-date in package.json
5. **Documentation**: Check if integrations are documented (README, inline comments, or API docs)

Output a report with:
- Overall health score (good / needs attention / critical)
- List of issues found, grouped by severity
- Suggested fixes for each issue
