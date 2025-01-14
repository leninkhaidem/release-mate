"""Test cases for CLI edge cases and remaining uncovered lines."""
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from release_mate.cli import (cli, get_git_info, get_normalized_project_dir,
                              run_semantic_release,
                              run_semantic_release_changelog)


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing click commands."""
    return CliRunner()


@pytest.fixture
def mock_repo():
    """Create a mock git repository."""
    mock = MagicMock()
    mock.active_branch.name = "main"
    mock.git.rev_parse.return_value = "/mock/repo/path"
    return mock


def test_get_git_info_invalid_remote_url(mock_repo):
    """Test get_git_info with invalid remote URL format."""
    mock_repo.remote.return_value.urls = iter(["invalid://url"])
    branch, url, domain, root = get_git_info(mock_repo)
    assert branch == "main"
    assert url == "invalid://url"
    assert domain == ""
    assert root == "/mock/repo/path"


def test_run_semantic_release_directory_change(tmp_path):
    """Test semantic-release maintains directory state after error."""
    config_file = tmp_path / "test.toml"
    config_file.touch()
    original_dir = os.getcwd()

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "semantic-release", "Error")
        with pytest.raises(SystemExit) as exc_info:
            run_semantic_release(config_file, ["--noop"], str(tmp_path))
        assert exc_info.value.code == 1
        assert os.getcwd() == original_dir


def test_run_semantic_release_changelog_directory_change(tmp_path):
    """Test semantic-release changelog maintains directory state after error."""
    config_file = tmp_path / "test.toml"
    config_file.touch()
    original_dir = os.getcwd()

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "semantic-release", "Error")
        with pytest.raises(SystemExit) as exc_info:
            run_semantic_release_changelog(
                config_file, ["--noop"], str(tmp_path))
        assert exc_info.value.code == 1
        assert os.getcwd() == original_dir


def test_version_worker_git_error(cli_runner):
    """Test version worker with git error."""
    with patch("release_mate.cli.validate_git_repository") as mock_validate:
        mock_validate.side_effect = Exception("Git error")
        result = cli_runner.invoke(cli, ["version"])
        assert result.exit_code == 1


def test_batch_version_no_release_mate_dir(cli_runner, mock_repo):
    """Test batch version when .release-mate directory doesn't exist."""
    with patch("release_mate.cli.validate_git_repository") as mock_validate, \
            patch("pathlib.Path.glob") as mock_glob:

        mock_validate.return_value = mock_repo
        mock_glob.return_value = []

        result = cli_runner.invoke(cli, ["batch-version"])
        assert result.output == ""  # No output when no projects are found


def test_batch_version_branch_switch_error(cli_runner, mock_repo):
    """Test batch version with branch switch error."""
    with patch("release_mate.cli.validate_git_repository") as mock_validate, \
            patch("pathlib.Path.glob") as mock_glob, \
            patch("release_mate.cli.identify_branch") as mock_identify, \
            patch("release_mate.cli.get_project_config_file") as mock_get_config, \
            patch("pathlib.Path.exists") as mock_exists:

        mock_validate.return_value = mock_repo
        mock_glob.return_value = [
            Path("/mock/repo/path/.release-mate/test.toml")]
        mock_identify.return_value = "feature"
        mock_get_config.return_value = Path(
            "/mock/repo/path/.release-mate/test.toml")
        mock_repo.git.checkout.side_effect = Exception("Checkout error")
        mock_exists.return_value = True

        result = cli_runner.invoke(cli, ["batch-version"])
        assert "Exception: Checkout error" in result.output


def test_get_normalized_project_dir_nonexistent(tmp_path):
    """Test normalizing project directory that doesn't exist."""
    with pytest.raises(SystemExit):
        get_normalized_project_dir(
            str(tmp_path / "nonexistent"), str(tmp_path))


def test_version_worker_multiple_errors(cli_runner, mock_repo):
    """Test version worker with multiple error conditions."""
    with patch("release_mate.cli.validate_git_repository") as mock_validate, \
            patch("release_mate.cli.get_project_config_file") as mock_get_config, \
            patch("pathlib.Path.exists") as mock_exists:

        mock_validate.return_value = mock_repo
        mock_get_config.return_value = Path(
            "/mock/repo/path/.release-mate/test.toml")
        mock_exists.return_value = True

        # Test multiple print flags
        result = cli_runner.invoke(cli, [
            "version",
            "--print",
            "--print-tag",
            "-i", "test"
        ])
        assert result.exit_code == 1
        assert "Only one print flag can be specified at a time" in result.output

        # Test multiple version flags
        result = cli_runner.invoke(cli, [
            "version",
            "--major",
            "--minor",
            "-i", "test"
        ])
        assert result.exit_code == 1
        assert "Only one version type flag can be specified at a time" in result.output


def test_batch_version_multiple_version_flags(cli_runner):
    """Test batch version with multiple version flags."""
    result = cli_runner.invoke(cli, [
        "batch-version",
        "--major",
        "--minor"
    ])
    assert result.exit_code == 1
    assert "Only one version type flag can be specified at a time" in result.output


def test_batch_version_with_errors(cli_runner, mock_repo):
    """Test batch version with various error conditions."""
    with patch("release_mate.cli.validate_git_repository") as mock_validate, \
            patch("pathlib.Path.glob") as mock_glob, \
            patch("release_mate.cli.identify_branch") as mock_identify, \
            patch("release_mate.cli.get_project_config_file") as mock_get_config:

        mock_validate.return_value = mock_repo
        mock_glob.return_value = [
            Path("/mock/repo/path/.release-mate/test1.toml"),
            Path("/mock/repo/path/.release-mate/test2.toml")
        ]

        # First project succeeds, second fails
        mock_identify.side_effect = [None, "main"]
        mock_get_config.return_value = Path(
            "/mock/repo/path/.release-mate/test2.toml")

        result = cli_runner.invoke(cli, ["batch-version"])
        assert result.exit_code == 1
        assert "Project 'test2' does not exist in .release-mate directory" in result.output
