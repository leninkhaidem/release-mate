# CLI Commands Reference

Release Mate provides a set of command-line tools to manage your project releases. Each command serves a specific purpose in the release management workflow.

## Global Options

All Release Mate commands support the following global options:

- `--help`: Show help message and exit

## `init` Command

**Purpose**: Initialize and configure a new project for release management with Release Mate. This command sets up the necessary configuration files and establishes version tracking.

**Key Functions**:

- Creates project-specific configuration in `.release-mate` directory
- Sets up version tracking for different file types
- Configures branch-specific release rules
- Establishes changelog generation settings

```bash
release-mate init [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `-i, --id TEXT` | Project identifier (defaults to current branch name) |
| `-v0, --current-version TEXT` | Initial version (defaults to '0.0.0') |
| `-d, --dir TEXT` | Project directory (defaults to current directory) |

### Examples

```bash
# Initialize with default settings
release-mate init

# Initialize with custom project ID and directory
release-mate init -i my-project -d ./packages/my-project

# Initialize a version tracking configuration for an existing python project managed with poetry
release-mate init -i python-pkg -d ./packages/python-pkg

# Initialize with specific initial version
release-mate init -i my-project -v0 1.0.0
```

## `version` Command

**Purpose**: Manage version numbers for a specific project based on conventional commits. This command analyzes commit messages to determine the appropriate version bump and handles all version-related operations.

**Key Functions**:

- Analyzes commit messages since last release
- Determines appropriate version bump (major, minor, patch)
- Updates version numbers in configured files
- Creates git tags for releases
- Generates changelogs
- Pushes changes to remote repository

```bash
release-mate version [OPTIONS]
```

### Options

!!! note
    These options are the subset of options supported by python-semantic-release.

| Option | Description |
|--------|-------------|
| `-i, --id TEXT` | Project identifier (defaults to current branch name) |
| `--noop` | Dry run without making any changes |
| `--print` | Print the next version and exit |
| `--print-tag` | Print the next version tag and exit |
| `--print-last-released` | Print the last released version and exit |
| `--print-last-released-tag` | Print the last released version tag and exit |
| `--major` | Force the next version to be a major release |
| `--minor` | Force the next version to be a minor release |
| `--patch` | Force the next version to be a patch release |
| `--prerelease` | Force the next version to be a prerelease |
| `--[no-]commit` | Whether to commit changes locally (default: true) |
| `--[no-]tag` | Whether to create a tag for the new version (default: true) |
| `--[no-]changelog` | Whether to update the changelog (default: true) |
| `--[no-]push` | Whether to push the new commit and tag to the remote (default: true) |

!!! note "Using Custom Configuration File"
    Instead of using the project ID, you can directly provide a path to a TOML configuration file. This allows you to use custom configuration files outside of the `.release-mate` directory:
    ```bash
    release-mate version -i /path/to/custom-config.toml
    ```

## `batch-version` Command

**Purpose**: Efficiently manage version updates across multiple projects in a repository. This command automates the versioning process for all configured projects while maintaining their individual versioning rules.

**Key Functions**:

- Processes all projects in the repository
- Handles branch switching automatically
- Maintains project-specific version rules
- Provides parallel version management

```bash
release-mate batch-version [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--noop` | Dry run without making any changes |
| `--major` | Force the next version to be a major release |
| `--minor` | Force the next version to be a minor release |
| `--patch` | Force the next version to be a patch release |
| `--prerelease` | Force the next version to be a prerelease |
| `--[no-]commit` | Whether to commit changes locally (default: true) |
| `--[no-]tag` | Whether to create a tag for the new version (default: true) |
| `--[no-]changelog` | Whether to update the changelog (default: true) |
| `--[no-]push` | Whether to push the new commit and tag to the remote (default: true) |

## `changelog` Command

**Purpose**: Generate and manage project changelogs based on conventional commits. This command creates structured, readable changelogs and can integrate with remote repository release notes.

**Key Functions**:

- Analyzes commit history
- Categorizes changes (features, fixes, breaking changes)
- Generates formatted changelog entries
- Updates changelog files
- Posts release notes to remote repositories
- Supports customizable templates

!!! warning "note"
    The changelog file is automatically generated by the `version` command in the corresponding project folder.

```bash
release-mate changelog [OPTIONS] [PROJECT_ID]
```

### Options

!!! note
    These options are the subset of options supported by python-semantic-release.

| Option | Description |
|--------|-------------|
| `--post-to-release-tag TAG` | Post release notes to the remote VCS's release for this tag |
| `--noop` | Dry run without making any changes |

!!! note "Using Custom Configuration File"
    Similar to the version command, you can directly provide a path to a TOML configuration file:
    ```bash
    release-mate changelog /path/to/custom-config.toml
    ```

## Common Workflows

### Initial Setup

```bash
# Initialize a new project
release-mate init -i my-project -d ./src/my-project

# Verify the configuration
cat .release-mate/my-project.toml
```

### Version Bump Workflow

```bash
# Check what the next version would be
release-mate version -i my-project --noop

# Perform the version bump
release-mate version -i my-project

# Generate and publish changelog
release-mate changelog
```

### Using Custom Configuration

```bash
# Use a custom configuration file for versioning
release-mate version -i ./my-custom-config.toml

# Generate changelog using custom configuration
release-mate changelog ./my-custom-config.toml
```

### Batch Version Workflow

```bash
# Check what would change across all projects
release-mate batch-version --noop

# Perform version bump for all projects
release-mate batch-version

# Generate changelog for a specific project in the current branch
release-mate changelog
```
