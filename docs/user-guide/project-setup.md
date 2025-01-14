# Project Setup

This guide will walk you through setting up a project with Release Mate.

## Prerequisites

Before you begin, ensure you have:

1. A Git repository initialized
2. Conventional commits (Angular style) is followed
3. Release Mate installed in your environment

## Initializing a Project

To initialize a project with Release Mate, use the `init` command:

```bash
release-mate init -d <project-directory>
```

### Options

- `-i, --id`: Project identifier (defaults to current branch name)
- `-d, --dir`: Project directory (defaults to current directory)
- `-v0, --current-version`: Initial version (defaults to '0.0.0')

### Example

```bash
# Initialize a project in the current directory
release-mate init -i my-project

# Initialize a project in a specific directory with initial version
release-mate init -i my-project -d ./packages/my-project -v0 1.0.0

# Initialize a Python project with poetry syntax
release-mate init -i python-pkg -p
```

## Configuration File

The `init` command creates a configuration file in the `.release-mate` directory:

```tree
.release-mate/
└── my-project.toml
```

This file contains all the necessary settings for your project, including:

- Branch configuration
- Commit message parsing rules
- Version bump rules
- Changelog generation settings

## Multiple Projects Setup

Release Mate supports managing multiple projects within a single repository

Each branch is isolated to manage one project, along with its unique changelog and version file. For N projects, there are N branches, ensuring clear separation of code, versions, and updates.

```text
*---* Main Branch (Base) -----------------------------------
     \
      \-- Branch A (Project A)
           |--- Code A
           |--- Changelog A
           |--- Version A
           
      \-- Branch B (Project B)
           |--- Code B
           |--- Changelog B
           |--- Version B

      \-- Branch N (Project N)
           |--- Code N
           |--- Changelog N
           |--- Version N
```

!!! important
    Branch A, B .. N should be protected. Version bump should ideally be done after successful regression.

### Example Multi-Project Setup

Execute the below commands in corresponding branches.

```bash
# Initialize first project. 
release-mate init -d ./packages/project1 

# Initialize second project
release-mate init -d ./packages/project2

# Initialize third project with different initial version
release-mate init -d ./packages/project3 -v0 1.0.0
```
