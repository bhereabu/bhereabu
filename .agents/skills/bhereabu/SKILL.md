```markdown
# bhereabu Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `bhereabu` Python repository. While the project does not use a specific framework, it follows consistent naming, import, and export styles. You'll learn how to structure files, write imports/exports, and understand the commit and testing patterns found in this codebase.

## Coding Conventions

### File Naming
- **CamelCase** is used for file names.
  - Example: `MyModule.py`, `UserProfileHandler.py`

### Import Style
- **Relative imports** are preferred.
  - Example:
    ```python
    from .utils import helper_function
    from ..models import UserModel
    ```

### Export Style
- **Named exports** are used, explicitly specifying what is available from a module.
  - Example:
    ```python
    __all__ = ['MyClass', 'my_function']
    ```

### Commit Patterns
- Commit messages are **freeform**, without strict prefixes.
- Average commit message length is about 70 characters.
  - Example:
    ```
    Add user authentication logic and update profile handler
    ```

## Workflows

_No automated workflows detected in the repository._

## Testing Patterns

- **Framework:** Unknown (not detected)
- **File Pattern:** Test files use the `.test.ts` suffix, suggesting some TypeScript-based testing, possibly for frontend or API contracts.
  - Example: `userProfile.test.ts`

## Commands

| Command | Purpose |
|---------|---------|
| /import-example | Show how to write a relative import in this codebase |
| /export-example | Show how to define named exports in a Python module |
| /commit-guidelines | Display commit message conventions |
| /test-pattern | Show the test file naming convention |
```
