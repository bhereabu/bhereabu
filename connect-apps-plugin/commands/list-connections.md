---
description: List all connected apps and API integrations found in the project
---

Scan the current project for all external API connections and integrations. Look for:

1. HTTP client calls (fetch, axios, XMLHttpRequest, got, node-fetch, etc.)
2. SDK imports for third-party services (Stripe, AWS, Firebase, Twilio, etc.)
3. Environment variables that reference API keys, tokens, or service URLs
4. Configuration files (.env, config files, service account JSONs)
5. Webhook endpoints or callback URLs

Present the results as a concise table with columns:
- Service/API name
- File location
- Auth method (API key, OAuth, token, none)
- Status (configured, missing config, hardcoded secret)

If no connections are found, say so and suggest using `/connect-apps-plugin:connect-api` to add one.
