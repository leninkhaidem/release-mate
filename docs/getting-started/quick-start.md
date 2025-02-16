# Quick Start Guide

This guide will help you get started with Release Mate in just a few minutes.

## Prerequisites

1. Python 3.9 or higher
2. Git repository initialized
3. Release Mate installed

## 5-Minute Tutorial

### 1. Initialize Your Project

```bash
# Navigate to your repository
cd your-repository

# Initialize Release Mate
release-mate init
```

!!! note
    If no project ID is specified, Release Mate uses your current branch name as the project ID.

!!! note
    If no directory is specified, Release Mate uses the current directory as the project directory.

### 2. Make Some Changes

Make changes to your code and commit them using conventional commits:

```bash
# Feature commit
git commit -m "feat: add user authentication"

# Bug fix commit
git commit -m "fix: handle null user input"
```

### 3. Create a Release

```bash
# Check what would change (dry run)
release-mate version --noop

# Create the actual release
release-mate version
```

### 4. Generate Changelog

```bash
release-mate changelog
```

## Common Use Cases

### Creating a Feature Release

```bash
# Add a new feature
git commit -m "feat: add OAuth support"

# Create release
release-mate version
```

### Creating a Bug Fix Release

```bash
# Fix a bug
git commit -m "fix: prevent memory leak"

# Create release
release-mate version
```

### Creating a Breaking Change

```bash
# Make breaking changes
git commit -m "feat!: redesign API endpoints

BREAKING CHANGE: Complete API redesign for v2"

# Create major release
release-mate version
```

## Project Structure

After initialization, your repository will look like this:

```
your-repository/
├── .release-mate/
│   └── your-project.toml    # Release Mate configuration
├── CHANGELOG.md             # Generated changelog
└── your-project-files/
```

!!! tip "Development Workflow"
    1. Make changes to your code
    2. Commit using conventional commits
    3. Run `release-mate version --noop` to preview
    4. Run `release-mate version` to release
    5. Run `release-mate changelog` to generate changelog file
    6. Run `release-mate publish` to publish the release to your VCS