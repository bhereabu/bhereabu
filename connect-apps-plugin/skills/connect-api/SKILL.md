---
name: connect-api
description: Connect an external API to the project. Generates integration code, configuration, and type definitions for a given API endpoint.
---

# Connect API

Help the user connect an external API to their project.

When invoked, do the following:

1. Ask the user for the API they want to connect (name, base URL, auth type)
2. Determine the tech stack from the current project files
3. Generate the appropriate integration code:
   - API client/wrapper with proper error handling
   - Type definitions or interfaces for request/response shapes
   - Configuration file or environment variable setup
   - A usage example demonstrating a basic request

## Guidelines

- Match the existing code style and conventions in the project
- Use `fetch` for browser-based projects, or the appropriate HTTP library if one is already installed
- Always include error handling and timeout configuration
- Never hardcode API keys or secrets - use environment variables
- Add clear comments explaining configuration options

$ARGUMENTS
