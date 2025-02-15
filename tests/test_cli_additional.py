"""Additional test cases for CLI functionality to increase coverage."""
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from release_mate.api import (_execute_publish, build_version_args,
                              display_panel_message, get_git_info,
                              get_normalized_project_dir,
                              get_project_config_file, identify_branch,
                              run_semantic_release,
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


def test_get_git_info_http_url(mock_repo):
    """Test get_git_info with HTTP remote URL."""
    mock_repo.remote().urls = iter(["https://github.com/user/repo.git"])
    branch, url, domain, root = get_git_info(mock_repo)
    assert branch == "main"
    assert url == "https://github.com/user/repo.git"
    assert domain == "https://github.com"
    assert root == "/mock/repo/path"


def test_get_git_info_ssh_url(mock_repo):
    """Test get_git_info with SSH remote URL."""
    mock_repo.remote().urls = iter(["git@github.com:user/repo.git"])
    branch, url, domain, root = get_git_info(mock_repo)
    assert branch == "main"
    assert url == "git@github.com:user/repo.git"
    assert domain == "https://github.com"
    assert root == "/mock/repo/path"


def test_run_semantic_release_success(tmp_path):
    """Test successful semantic-release execution."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Version updated"
        mock_run.return_value.stderr = ""
        run_semantic_release(config_file, ["--noop"], str(tmp_path))
        mock_run.assert_called_once()


def test_run_semantic_release_changelog_success(tmp_path):
    """Test successful semantic-release changelog execution."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Changelog updated"
        mock_run.return_value.stderr = ""
        run_semantic_release_changelog(config_file, ["--noop"], str(tmp_path))
        mock_run.assert_called_once()


@patch("pathlib.Path.exists")
def test_version_worker_print_flags(mock_exists, cli_runner, mock_repo):
    """Test version worker with print flags."""
    with patch("release_mate.api.validate_git_repository") as mock_validate, \
            patch("release_mate.api.get_project_config_file") as mock_get_config, \
            patch("release_mate.api.run_semantic_release") as mock_run:

        mock_validate.return_value = mock_repo
        config_file = Path("/mock/repo/path/.release-mate/test.toml")
        mock_get_config.return_value = config_file
        mock_exists.return_value = True

        # Test print version
        version_worker(project_id="test", print_version=True)
        mock_run.assert_called_with(
            config_file, ["--print"], "/mock/repo/path")

        # Test print tag
        version_worker(project_id="test", print_tag=True)
        mock_run.assert_called_with(
            config_file, ["--print-tag"], "/mock/repo/path")


def test_build_version_args_combinations():
    """Test building version arguments with different combinations."""
    # Test with all flags enabled
    args = build_version_args(True, True, False, False, False,
                              True, True, True, True)
    assert "--noop" in args
    assert "--major" in args

    # Test with all flags disabled
    args = build_version_args(
        False, False, False, False, False, False, False, False, False)
    assert "--no-commit" in args
    assert "--no-tag" in args
    assert "--no-changelog" in args
    assert "--no-push" in args


@patch("os.path.exists")
@patch("os.getcwd")
def test_get_normalized_project_dir_current_dir(mock_getcwd, mock_exists, tmp_path):
    """Test normalizing project directory with current directory."""
    mock_exists.return_value = True
    mock_getcwd.return_value = str(tmp_path)
    result = get_normalized_project_dir(".", str(tmp_path))
    assert result == "."


def test_identify_branch_with_multiple_branches(tmp_path):
    """Test identifying branch from config with multiple branch sections."""
    config_content = """
[tool.semantic_release.branches.main]
match = "main"
prerelease = false

[tool.semantic_release.branches.develop]
match = "develop"
prerelease = true
"""
    config_file = tmp_path / "test.toml"
    config_file.write_text(config_content)

    branch = identify_branch(config_file)
    assert branch == "main"  # Should return the first branch found


def test_display_panel_message_with_special_chars():
    """Test displaying panel message with special characters."""
    with patch("rich.console.Console.print") as mock_print:
        display_panel_message("Test", "Message with 🚀 emoji", "blue")
        mock_print.assert_called_once()


def test_get_project_config_file_absolute_path():
    """Test getting project config file with absolute repository path."""
    config = get_project_config_file("test", "/absolute/path")
    assert config.is_absolute()
    assert str(config).endswith(".release-mate/test.toml")


def test_execute_publish_success(tmp_path):
    """Test successful publish execution."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Published successfully"
        mock_run.return_value.stderr = ""
        _execute_publish(config_file, ["--noop"], str(tmp_path))
        mock_run.assert_called_with(
            ["semantic-release", "-c", str(config_file), "--noop", "publish"],
            check=True, capture_output=True, text=True
        )


def test_execute_publish_with_tag(tmp_path):
    """Test publish execution with specific tag."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Published with tag"
        mock_run.return_value.stderr = ""
        _execute_publish(config_file, ["--tag=v1.0.0"], str(tmp_path))
        mock_run.assert_called_with(
            ["semantic-release", "-c",
                str(config_file), "publish", "--tag=v1.0.0"],
            check=True, capture_output=True, text=True
        )


def test_execute_publish_error(tmp_path):
    """Test publish execution with error."""
    config_file = tmp_path / "test.toml"
    config_file.touch()

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "semantic-release", stderr="Failed to publish")
        with pytest.raises(SystemExit):
            _execute_publish(config_file, [], str(tmp_path))


@patch("pathlib.Path.exists")
def test_publish_nonexistent_project(mock_exists, cli_runner, mock_repo):
    """Test publish with non-existent project."""
    with patch("release_mate.api.validate_git_repository") as mock_validate:
        mock_validate.return_value = mock_repo
        mock_exists.return_value = False

        from release_mate.api import publish_worker
        with pytest.raises(SystemExit):
            publish_worker(project_id="nonexistent")
