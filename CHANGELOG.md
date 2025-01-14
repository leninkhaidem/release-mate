# CHANGELOG


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
