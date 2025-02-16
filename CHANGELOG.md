# CHANGELOG


## v0.3.0 (2025-02-16)

### Chores

- **pyproject**: Update GitHub token environment variable for publishing
  ([`4bc5a72`](https://github.com/leninkhaidem/release-mate/commit/4bc5a72508ecbe66490393269d8cbf577a6bc630))

- Changed environment variable from GH_TOKEN to GH_TOKEN_PUB

### Documentation

- Add new options for version command in CLI reference
  ([`6943dc1`](https://github.com/leninkhaidem/release-mate/commit/6943dc16e33353912fba96f2edf68d19b2154ffc))

- Add `--[no-]vcs-release` to control VCS release creation.

- Introduce `--as-prerelease` and `--prerelease-token` for prerelease versions.

- Include `--build-metadata` for appending build metadata.

- Add `--skip-build` to skip building during version updates.

- **cli**: Update quick start and user guide for publish command
  ([`2e95b22`](https://github.com/leninkhaidem/release-mate/commit/2e95b222d7321a7d28a2b9e049f8cdf5f43dae9b))

- Added `release-mate publish` command to quick start guide

- Introduced detailed section on publishing releases in user guide

- Included examples for using the publish command with options

### Features

- **api, cli**: Add additional options for versioning
  ([`4cc530c`](https://github.com/leninkhaidem/release-mate/commit/4cc530ca8e8207cbaccfe498703f5892b8ef4fce))

- Introduced `vcs_release` option to control VCS release creation.

- Added `as_prerelease`, `prerelease_token`, `build_metadata`, and `skip_build` options for enhanced
  versioning flexibility.

### Testing

- **cli**: Enhance version argument tests with additional flags
  ([`2533c12`](https://github.com/leninkhaidem/release-mate/commit/2533c12794ece9447e8482ba56ce54c4ef9ccb22))

- Added tests for new versioning flags including `as_prerelease`, `prerelease_token`,
  `build_metadata`, and `skip_build`.

- Updated existing tests to reflect changes in the `build_version_args` function.


## v0.2.0 (2025-02-15)

### Features

- **api, cli**: Add publish command and improve error handling
  ([`34e4516`](https://github.com/leninkhaidem/release-mate/commit/34e4516be8970f8efb338c5ba91bf963c83b6f75))

- Introduced a new publish command in the CLI for semantic-release.

- Enhanced error handling by suppressing exceptions in various functions.

- Refactored code for better readability and maintainability.

- **api, cli**: Add tag option to publish command
  ([`bb89924`](https://github.com/leninkhaidem/release-mate/commit/bb89924af2f9ea83c2ffd1cb523adbe9f0ad016e))

- Enhanced the publish_worker function to accept an optional tag argument for release publishing.

- Updated the CLI command to include the new tag option for better release management.

### Testing

- **cli**: Add additional tests for publish functionality
  ([`69cc62d`](https://github.com/leninkhaidem/release-mate/commit/69cc62dd8ded7261a99e37ed6901990785083417))

- Implement tests for successful publish execution.

- Add tests for publish execution with specific tag.

- Include error handling tests for publish execution.

- Test publish with non-existent project.


## v0.1.5 (2025-01-29)

### Bug Fixes

- **api**: Improve shell completion installation robustness
  ([`d6c22a0`](https://github.com/leninkhaidem/release-mate/commit/d6c22a0a7494e6b9de7dc6fc9a167db0c5bdeb08))

- Enhanced shell completion installation for bash, zsh, and fish shells

- Added conditional checks to prevent errors if command is not available

- Implemented error suppression and fallback mechanisms for completion script sourcing

### Documentation

- Updated docs formatting
  ([`c51f0e3`](https://github.com/leninkhaidem/release-mate/commit/c51f0e352d48729dc30652b58954110eb0d3ea7f))


## v0.1.4 (2025-01-14)

### Bug Fixes

- **api, cli**: Enhance worker initialization with template directory
  ([`dc195b3`](https://github.com/leninkhaidem/release-mate/commit/dc195b32d78cbfd47a159fcdd36f3f010c8ac463))

- Updated the `init_worker` function in the API to accept a `template_dir` parameter, allowing for
  more flexible template management. - Modified the CLI command to retrieve the template directory
  using `pkg_resources` before invoking `init_worker`, improving code clarity and maintainability.

### Code Style

- **cli**: Add help description for install_completion command
  ([`cd6c08c`](https://github.com/leninkhaidem/release-mate/commit/cd6c08c1c19c02cb81b30c5914d85479b2be6cbb))

- Enhanced the `install_completion` CLI command by adding a help description to clarify its purpose
  for installing shell completion for bash, zsh, or fish shells.

### Documentation

- Updated docs for shell autocomplete
  ([`e5bcb7a`](https://github.com/leninkhaidem/release-mate/commit/e5bcb7a609bd97b1e153eb51d43de6db0de29f72))


## v0.1.3 (2025-01-14)

### Bug Fixes

- **api**: Streamline project directory handling in get_project_config to correctly identify poetry
  project
  ([`d1fe900`](https://github.com/leninkhaidem/release-mate/commit/d1fe900194c153a164022e7e46851cbc903f8ae9))

- Updated the `get_project_config` function to normalize the project directory before checking for
  Poetry configuration files.

- **cli**: Add shell completion installation command
  ([`6a91825`](https://github.com/leninkhaidem/release-mate/commit/6a91825cdeae041db7de903eb83b37162a7d7f2f))

- Introduced a new CLI command `install_completion` to facilitate the installation of shell
  completion for bash, zsh, and fish shells. - Implemented the `install_shell_completion` function
  in the API to handle the detection of the shell type, update the appropriate rc file, and provide
  user feedback on the installation status.


## v0.1.2 (2025-01-14)

### Refactoring

- Update worker initialization in CLI and API
  ([`291e2fb`](https://github.com/leninkhaidem/release-mate/commit/291e2fb8f6cc7f7812157ddf0a23a4a7c3a47fae))

- Refactored the `init_worker` function in the API to accept a `ProjectConfig` object instead of
  individual parameters. - Modified the CLI command to retrieve the project configuration before
  calling `init_worker`, improving code clarity and maintainability.


## v0.1.1 (2025-01-14)

### Documentation

- Add support for custom configuration files in CLI commands
  ([`eb5caac`](https://github.com/leninkhaidem/release-mate/commit/eb5caacdd62eb3ed04740f4fdb097d47f0e69b1f))

- Updated `release-mate version` and `release-mate changelog` commands to allow users to specify a
  custom TOML configuration file path. - Included usage examples for custom configuration in the
  documentation. - Enhanced clarity on how to utilize custom configurations outside of the default
  `.release-mate` directory.

- Update README to include documentation link
  ([`4b333ac`](https://github.com/leninkhaidem/release-mate/commit/4b333ac3ec8eefbaa8b4d73d0bec6cc192d656a8))

### Refactoring

- Move CLI logic to API module and clean up code
  ([`202b2ca`](https://github.com/leninkhaidem/release-mate/commit/202b2ca4571d1e404d864bc27efca22a584f7460))

- Refactored the CLI commands to utilize a new `api` module, improving code organization and
  maintainability. - Removed redundant functions from the CLI and replaced them with calls to the
  `api` module. - Updated import statements across multiple files to reflect the new structure. -
  Enhanced the `__init__.py` file to include the `api` module in the package's public API.


## v0.1.0 (2025-01-14)

### Chores

- First draft
  ([`849e3e9`](https://github.com/leninkhaidem/release-mate/commit/849e3e931df7d14c6764508efd829fa21d227b4e))

### Features

- Enhance CLI initialization and configuration handling
  ([`69e1ef6`](https://github.com/leninkhaidem/release-mate/commit/69e1ef6ea04896f704f4d8929f81fdd127f2708f))

- Updated the initialization message to include a reminder for users to update the `build_command`
  and `version_variables` in the configuration file. - Refactored the method for obtaining the
  project configuration file to improve clarity and maintainability. - Added a new helper function
  `_get_config_file` to streamline the process of retrieving the configuration file. - Initialized
  `build_command` and `version_variables` in the project template to provide a clearer starting
  point for users.
