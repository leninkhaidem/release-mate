"""Test cases for remaining uncovered lines in CLI."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from release_mate.api import (get_git_info, get_normalized_project_dir,
                              identify_branch, run_semantic_release,
                              run_semantic_release_changelog)
from release_mate.cli import cli


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


def test_get_git_info_malformed_remote_url(mock_repo):
    """Test get_git_info with malformed remote URL."""
    mock_repo.remote.return_value.urls = iter(["malformed://url"])
    branch, url, domain, root = get_git_info(mock_repo)
    assert branch == "main"
    assert url == "malformed://url"
    assert domain == ""
    assert root == "/mock/repo/path"


def test_run_semantic_release_with_output(tmp_path):
    """Test semantic-release with both stdout and stderr output."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Success output"
        mock_run.return_value.stderr = "Warning message"
        run_semantic_release(config_file, ["--noop"], str(tmp_path))


def test_run_semantic_release_changelog_with_output(tmp_path):
    """Test semantic-release changelog with both stdout and stderr output."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Success output"
        mock_run.return_value.stderr = "Warning message"
        run_semantic_release_changelog(config_file, ["--noop"], str(tmp_path))


def test_version_worker_with_all_flags(cli_runner, mock_repo):
    """Test version worker with all flags enabled."""
    with patch("release_mate.api.validate_git_repository") as mock_validate, \
            patch("release_mate.api.get_project_config_file") as mock_get_config, \
            patch("pathlib.Path.exists") as mock_exists, \
            patch("release_mate.api.run_semantic_release") as mock_run:

        mock_validate.return_value = mock_repo
        mock_get_config.return_value = Path(
            "/mock/repo/path/.release-mate/test.toml")
        mock_exists.return_value = True

        result = cli_runner.invoke(cli, [
            "version",
            "--noop",
            "--major",
            "--no-commit",
            "--no-tag",
            "--no-changelog",
            "--no-push",
            "--no-vcs-release",
            "--as-prerelease",
            "--prerelease-token=beta",
            "--build-metadata=001",
            "--skip-build",
            "-i", "test"
        ])

        assert result.exit_code == 0
        args = mock_run.call_args[0][1]
        assert "--noop" in args
        assert "--major" in args
        assert "--no-commit" in args
        assert "--no-tag" in args
        assert "--no-changelog" in args
        assert "--no-push" in args
        assert "--no-vcs-release" in args
        assert "--as-prerelease" in args
        assert "--prerelease-token=beta" in args
        assert "--build-metadata=001" in args
        assert "--skip-build" in args


def test_batch_version_with_branch_error(cli_runner, mock_repo):
    """Test batch version with branch identification error."""
    with patch("release_mate.api.validate_git_repository") as mock_validate, \
            patch("pathlib.Path.glob") as mock_glob, \
            patch("release_mate.api.identify_branch") as mock_identify, \
            patch("release_mate.api.get_project_config_file") as mock_get_config:

        mock_validate.return_value = mock_repo
        mock_glob.return_value = [
            Path("/mock/repo/path/.release-mate/test1.toml"),
            Path("/mock/repo/path/.release-mate/test2.toml")
        ]

        # First project fails to identify branch
        mock_identify.side_effect = [None, "main"]
        mock_get_config.return_value = Path(
            "/mock/repo/path/.release-mate/test2.toml")

        result = cli_runner.invoke(cli, ["batch-version"])
        assert result.exit_code == 1
        assert "Project 'test2' does not exist in .release-mate directory" in result.output


def test_identify_branch_with_empty_file(tmp_path):
    """Test identifying branch from empty file."""
    config_file = tmp_path / "empty.toml"
    config_file.touch()

    branch = identify_branch(config_file)
    assert branch is None


def test_identify_branch_with_invalid_content(tmp_path):
    """Test identifying branch with invalid file content."""
    config_file = tmp_path / "invalid.toml"
    config_file.write_text("invalid content")

    branch = identify_branch(config_file)
    assert branch is None


def test_get_normalized_project_dir_with_absolute_path(tmp_path):
    """Test normalizing project directory with absolute path."""
    tmp_path.touch()  # Create the file
    result = get_normalized_project_dir(str(tmp_path), str(tmp_path.parent))
    assert result == str(tmp_path)


def test_batch_version_with_checkout_error(cli_runner, mock_repo):
    """Test batch version with checkout error."""
    with patch("release_mate.api.validate_git_repository") as mock_validate, \
            patch("pathlib.Path.glob") as mock_glob, \
            patch("release_mate.api.identify_branch") as mock_identify, \
            patch("release_mate.api.get_project_config_file") as mock_get_config, \
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
