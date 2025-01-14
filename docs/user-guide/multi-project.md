# Multi-Project Workflow

Release Mate is designed to handle multiple projects within a single repository. This guide explains how to manage versions and releases across different projects and branches.

## Project Structure

A typical multi-project repository might look like this:

```
repository/
├── .release-mate/
│   ├── project1.toml
│   ├── project2.toml
│   └── feature-branch.toml
├── project1/
│   ├── src/
│   └── pyproject.toml
├── project2/
│   ├── src/
│   └── package.json
└── README.md
```

## Managing Multiple Projects

### 1. Initialize Projects

Initialize each project with a unique identifier:

```bash
# Initialize first project
release-mate init -i project1 -d ./project1

# Initialize second project
release-mate init -i project2 -d ./project2
```

### 2. Project-Specific Configuration

Each project gets its own configuration file in `.release-mate/`:

!!! example "project1.toml"
    ```toml
    [tool.semantic_release]
    version_variables = [
        "project1/src/__init__.py:__version__"
    ]
    version_toml = [
        "project1/pyproject.toml:tool.poetry.version"
    ]
    ```

!!! example "project2.toml"
    ```toml
    [tool.semantic_release]
    version_variables = [
        "project2/package.json:version"
    ]
    ```

## Branch-Based Workflows

### Feature Branch Development

1. Create a feature branch configuration:
```bash
git checkout -b feature/new-api
release-mate init -i feature-new-api -d ./project1
```

2. Use prerelease versions for feature development:
```bash
release-mate version feature-new-api --prerelease
```

### Release Branch Management

1. Create a release branch:
```bash
git checkout -b release/2.0
release-mate init -i release-2.0 -d ./project1
```

2. Configure prerelease token for release candidates:
```toml
[tool.semantic_release.branches.release-2.0]
match = "release/2.0"
prerelease_token = "rc"
prerelease = true
```

3. Create release candidates:
```bash
release-mate version release-2.0
```

## Common Scenarios

### Scenario 1: Independent Project Releases

Projects with independent version lifecycles:

```bash
# Release project1
release-mate version project1

# Release project2 separately
release-mate version project2
```

### Scenario 2: Coordinated Releases

When projects need to be released together:

```bash
# Check both projects
release-mate version project1 --noop
release-mate version project2 --noop

# Perform releases
release-mate version project1
release-mate version project2

# Generate changelogs
release-mate changelog project1
release-mate changelog project2
```

### Scenario 3: Feature Branch Development

Working on a feature across multiple projects:

```bash
# Create feature branch configs
release-mate init -i feature-auth-project1 -d ./project1
release-mate init -i feature-auth-project2 -d ./project2

# Development iterations
release-mate version feature-auth-project1 --prerelease
release-mate version feature-auth-project2 --prerelease

# Merge to main branch
git checkout main
release-mate version project1
release-mate version project2
```

## Best Practices

1. **Consistent Naming**
   - Use descriptive project IDs
   - Follow a naming convention for feature branches

2. **Version Synchronization**
   - Use `--noop` to preview changes
   - Coordinate releases when projects are interdependent

3. **Changelog Management**
   - Generate changelogs after each release
   - Use `--post-to-release-tag` for GitHub releases

4. **Branch Configuration**
   - Configure branch patterns in semantic-release settings
   - Use prerelease tokens for development branches

!!! tip "Project Organization"
    Keep your `.release-mate` directory organized:
    ```
    .release-mate/
    ├── main/
    │   ├── project1.toml
    │   └── project2.toml
    └── features/
        └── feature-auth.toml
    ``` 