# Installation Guide

## Requirements

Before installing Release Mate, ensure you have the following prerequisites:

- Python 3.9 or higher
- pip or poetry package manager
- Git installed and configured

## Installation Methods

### Using pip

<!-- termynal -->
```bash
$ pip install release-mate
```

## Verify Installation

After installation, verify that Release Mate is installed correctly:

```bash
release-mate --version
```

## Shell Completion

Release Mate supports command-line completion for bash, zsh, and fish shells. To enable it, simply run:

```bash
release-mate install-completion
```

This command will automatically install the appropriate shell completion for your current shell (bash, zsh, or fish). After installation, restart your shell or source your shell's config file to enable completion.

## Dependencies

Release Mate automatically installs the following core dependencies:

| Package | Version | Purpose |
|---------|---------|----------|
| click | ^8.1.7 | Command-line interface creation |
| rich | ^13.7.0 | Rich text and formatting in terminal |
| gitpython | ^3.1.40 | Git operations handling |
| cookiecutter | ^2.5.0 | Project template management |

## System-wide vs Virtual Environment

!!! tip "Best Practice"
    We recommend installing Release Mate in a virtual environment to avoid conflicts with other Python packages.

### Using venv

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Unix or MacOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install Release Mate
pip install release-mate
```