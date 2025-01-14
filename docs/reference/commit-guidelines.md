# Commit Guidelines

Release Mate uses the Angular-style conventional commits specification for automated versioning and changelog generation.

## Commit Message Format

!!! info "Commit Structure"
    ```
    <type>(<scope>): <description>

    [optional body]

    [optional footer(s)]
    ```
!!! important "vscode users with copilot"
    vscode with copilot supports generating conventional commit messages. It analyzes the changes for the commit and generates a commit message.

## Commit Types

| Type | Description | Version Impact |
|------|-------------|----------------|
| `feat` | New feature | Minor (0.1.0) |
| `fix` | Bug fix | Patch (0.0.1) |
| `perf` | Performance improvement | Patch (0.0.1) |
| `docs` | Documentation only changes | None |
| `style` | Code style changes (formatting, etc) | None |
| `refactor` | Code refactoring | None |
| `test` | Adding or updating tests | None |
| `build` | Build system or dependencies | None |
| `ci` | CI/CD changes | None |
| `chore` | Other changes | None |

## Breaking Changes

!!! warning "Breaking Changes"
    Breaking changes MUST be indicated by adding `!` after the type/scope or by adding `BREAKING CHANGE:` in the footer.
    ```
    feat!: remove deprecated API
    ```
    This will trigger a major version bump (1.0.0).

## Examples

### Feature Addition
```
feat(auth): add OAuth2 authentication

Implements OAuth2 authentication flow using the following providers:
- Google
- GitHub
- GitLab

Closes #123
```

### Bug Fix
```
fix(parser): handle empty commit messages

Previously, empty commit messages would cause the parser to crash.
Now it properly handles empty messages by skipping them.
```

### Breaking Change
```
feat(api)!: rename authentication endpoints

BREAKING CHANGE: The authentication endpoints have been renamed to follow
REST conventions. Old endpoints will be removed in the next major version.

- /auth/login -> /auth/token
- /auth/logout -> /auth/token/revoke
```

## Scope Guidelines

The scope should be one of the following:

- Name of the project component
- Name of the module
- Name of the feature
- Name of the package

Examples:
- `feat(cli): add new command`
- `fix(parser): handle edge case`
- `docs(api): update endpoint documentation`

## Best Practices

1. Keep the first line under 72 characters
2. Use imperative mood in the description
3. Don't end the description with a period
4. Separate subject from body with a blank line
5. Use the body to explain what and why vs. how

!!! tip "Commit Message Template"
    You can set up a commit message template:
    ```bash
    git config --global commit.template ~/.gitmessage
    ```
    
    Template content:
    ```
    <type>(<scope>): <description>

    [optional body]

    [optional footer(s)]
    ```

## Version Bumping Rules

Release Mate follows these rules for version bumping:

1. Breaking changes (with `!` or `BREAKING CHANGE`) trigger a major version bump
2. `feat` type triggers a minor version bump
3. `fix` and `perf` types trigger a patch version bump
4. Other types don't trigger version bumps

!!! note "Version Format"
    Release Mate follows semantic versioning (MAJOR.MINOR.PATCH) 