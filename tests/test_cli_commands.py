"""Additional tests for CLI commands and edge cases."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from release_mate.cli import cli


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing click commands."""
    return CliRunner()


@pytest.fixture
def mock_config_file(tmp_path):
    """Create a mock configuration file."""
    config = tmp_path / "test-project.toml"
    config.write_text("""
[tool.semantic_release]
branch = "main"
version_variable = "release_mate/__init__.py:__version__"
""")
    return config


def test_version_command_help(cli_runner):
    """Test the help output of version command."""
    result = cli_runner.invoke(cli, ["version", "--help"])
    assert result.exit_code == 0
    assert "Perform a version bump" in result.output


@patch("release_mate.api.validate_git_repository")
@patch("release_mate.api.get_project_config_file")
def test_version_command_invalid_project(mock_get_config, mock_validate, cli_runner):
    """Test version command with non-existent project."""
    mock_repo = MagicMock()
    mock_repo.git.rev_parse.return_value = "/path/to/repo"
    mock_validate.return_value = mock_repo
    mock_get_config.return_value = Path(
        "/path/to/repo/.release-mate/nonexistent.toml")

    result = cli_runner.invoke(cli, ["version", "-i", "nonexistent"])
    assert result.exit_code == 1
    assert "Project 'nonexistent' does not exist in .release-mate directory" in result.output


@patch("release_mate.api.validate_git_repository")
@patch("release_mate.api.get_project_config_file")
@patch("pathlib.Path.exists")
def test_version_command_conflicting_flags(mock_exists, mock_get_config, mock_validate, cli_runner):
    """Test version command with conflicting version bump flags."""
    mock_repo = MagicMock()
    mock_repo.git.rev_parse.return_value = "/path/to/repo"
    mock_validate.return_value = mock_repo
    mock_exists.return_value = True

    result = cli_runner.invoke(cli, [
        "version",
        "--major",
        "--minor",
        "-i", "test"
    ])
    assert result.exit_code == 1
    assert "Only one version type flag can be specified at a time" in result.output


@patch("release_mate.api.validate_git_repository")
@patch("release_mate.api.get_project_config_file")
@patch("pathlib.Path.exists")
def test_changelog_invalid_tag(mock_exists, mock_get_config, mock_validate, cli_runner):
    """Test changelog command with invalid release tag."""
    mock_repo = MagicMock()
    mock_repo.git.rev_parse.return_value = "/path/to/repo"
    mock_validate.return_value = mock_repo
    mock_exists.return_value = True

    result = cli_runner.invoke(cli, [
        "changelog",
        "test",
        "--post-to-release-tag", "invalid-tag"
    ])
    assert result.exit_code == 1
    assert "Error" in result.output


@patch("release_mate.api.validate_git_repository")
@patch("release_mate.api.version_worker")
@patch("release_mate.api.get_project_config_file")
@patch("pathlib.Path.exists")
def test_version_command_dry_run(mock_exists, mock_get_config, mock_worker, mock_validate, cli_runner):
    """Test version command in dry-run mode."""
    mock_repo = MagicMock()
    mock_repo.git.rev_parse.return_value = "/path/to/repo"
    mock_validate.return_value = mock_repo
    mock_exists.return_value = True

    result = cli_runner.invoke(cli, [
        "version",
        "-i", "test",
        "--noop"
    ])
    assert result.exit_code == 0
    mock_worker.assert_called_once_with(
        project_id="test",
        noop=True,
        print_version=False,
        print_tag=False,
        print_last_released=False,
        print_last_released_tag=False,
        major=False,
        minor=False,
        patch=False,
        prerelease=False,
        commit=True,
        tag=True,
        changelog=True,
        push=True,
        vcs_release=True,
        as_prerelease=False,
        prerelease_token=None,
        build_metadata=None,
        skip_build=False
    )


@patch("release_mate.api.validate_git_repository")
@patch("release_mate.api.version_worker")
@patch("release_mate.api.get_project_config_file")
@patch("pathlib.Path.exists")
def test_version_command_print_version(mock_exists, mock_get_config, mock_worker, mock_validate, cli_runner):
    """Test version command with print-version flag."""
    mock_repo = MagicMock()
    mock_repo.git.rev_parse.return_value = "/path/to/repo"
    mock_validate.return_value = mock_repo
    mock_exists.return_value = True

    result = cli_runner.invoke(cli, [
        "version",
        "-i", "test",
        "--print"
    ])
    assert result.exit_code == 0
    mock_worker.assert_called_once_with(
        project_id="test",
        noop=False,
        print_version=True,
        print_tag=False,
        print_last_released=False,
        print_last_released_tag=False,
        major=False,
        minor=False,
        patch=False,
        prerelease=False,
        commit=True,
        tag=True,
        changelog=True,
        push=True,
        vcs_release=True,
        as_prerelease=False,
        prerelease_token=None,
        build_metadata=None,
        skip_build=False
    )
