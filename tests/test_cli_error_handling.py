"""Test cases for CLI error handling scenarios."""
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from git.exc import GitCommandError

from release_mate.api import (get_git_info, run_semantic_release,
                              run_semantic_release_changelog, version_worker)


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


def test_get_git_info_no_remote(mock_repo):
    """Test get_git_info when no remote is configured."""
    mock_repo.remote.side_effect = GitCommandError("git remote", 128)
    branch, url, domain, root = get_git_info(mock_repo)
    assert branch == "main"
    assert url == ""
    assert domain == ""
    assert root == "/mock/repo/path"


def test_run_semantic_release_error(tmp_path):
    """Test semantic-release execution with error."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "semantic-release", stderr="Error occurred")
        with pytest.raises(SystemExit):
            run_semantic_release(config_file, ["--noop"], str(tmp_path))


def test_run_semantic_release_changelog_error(tmp_path):
    """Test semantic-release changelog execution with error."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "semantic-release", stderr="Error occurred")
        with pytest.raises(SystemExit):
            run_semantic_release_changelog(
                config_file, ["--noop"], str(tmp_path))


def test_version_worker_multiple_print_flags(cli_runner, mock_repo):
    """Test version worker with multiple print flags (should fail)."""
    with patch("release_mate.api.validate_git_repository") as mock_validate:
        mock_validate.return_value = mock_repo
        with pytest.raises(SystemExit):
            version_worker(
                project_id="test",
                print_version=True,
                print_tag=True
            )


def test_version_worker_multiple_version_flags(cli_runner, mock_repo):
    """Test version worker with multiple version flags (should fail)."""
    with patch("release_mate.api.validate_git_repository") as mock_validate:
        mock_validate.return_value = mock_repo
        with pytest.raises(SystemExit):
            version_worker(
                project_id="test",
                major=True,
                minor=True
            )


def test_version_worker_nonexistent_project(cli_runner, mock_repo):
    """Test version worker with non-existent project."""
    with patch("release_mate.api.validate_git_repository") as mock_validate, \
            patch("release_mate.api.get_project_config_file") as mock_get_config:

        mock_validate.return_value = mock_repo
        config_file = Path("/mock/repo/path/.release-mate/test.toml")
        mock_get_config.return_value = config_file

        # Simulate non-existent project
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False
            with pytest.raises(SystemExit):
                version_worker(project_id="nonexistent")


def test_run_semantic_release_with_stderr(tmp_path):
    """Test semantic-release execution with stderr output."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Warning: something happened"
        run_semantic_release(config_file, ["--noop"], str(tmp_path))
        mock_run.assert_called_once()


def test_run_semantic_release_changelog_with_stderr(tmp_path):
    """Test semantic-release changelog execution with stderr output."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Warning: something happened"
        run_semantic_release_changelog(config_file, ["--noop"], str(tmp_path))
        mock_run.assert_called_once()
