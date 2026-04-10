---
name: manage-integrations
description: List, audit, or update existing API integrations and connected services in the project.
---

# Manage Integrations

Help the user manage the external integrations in their project.

When invoked, do the following:

1. Scan the project for existing API integrations by looking for:
   - HTTP client usage (fetch, axios, got, etc.)
   - API base URLs and endpoint patterns
   - Environment variables referencing API keys or service URLs
   - Configuration files for third-party services
2. Present a summary of all discovered integrations
3. Based on user input, help with:
   - Updating an integration (new endpoint, changed auth)
   - Removing an integration cleanly
   - Auditing integrations for security issues (exposed keys, missing error handling)
   - Generating documentation for existing integrations

## Guidelines

- Be thorough when scanning - check all file types
- Flag any hardcoded credentials as security issues
- Suggest improvements for integrations missing error handling or retries

$ARGUMENTS
