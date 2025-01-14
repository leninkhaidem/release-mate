"""Tests for the release-mate CLI functionality."""
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import git
import pytest
from click.testing import CliRunner

from release_mate.cli import (build_version_args, cli, create_git_tag,
                              display_panel_message, get_available_project_ids,
                              get_git_info, get_normalized_project_dir,
                              identify_branch, run_semantic_release,
                              run_semantic_release_changelog,
                              validate_git_repository, version_worker)


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing click commands."""
    return CliRunner()


@pytest.fixture
def mock_repo():
    """Create a mock git repository."""
    mock = MagicMock(spec=git.Repo)
    mock.active_branch.name = "main"
    mock_remote = MagicMock()
    mock_remote.urls = iter(["https://github.com/user/repo.git"])
    mock.remote.return_value = mock_remote
    mock.git.rev_parse.return_value = "/path/to/repo"
    return mock


@pytest.fixture
def mock_repo_ssh():
    """Create a mock git repository with SSH remote URL."""
    mock = MagicMock(spec=git.Repo)
    mock.active_branch.name = "main"
    mock_remote = MagicMock()
    mock_remote.urls = iter(["git@github.com:user/repo.git"])
    mock.remote.return_value = mock_remote
    mock.git.rev_parse.return_value = "/path/to/repo"
    return mock


def test_validate_git_repository_success(mock_repo):
    """Test successful git repository validation."""
    with patch("git.Repo") as mock_git_repo:
        mock_git_repo.return_value = mock_repo
        result = validate_git_repository()
        assert result == mock_repo


def test_validate_git_repository_failure():
    """Test git repository validation failure."""
    with patch("git.Repo", side_effect=git.InvalidGitRepositoryError), \
            pytest.raises(SystemExit) as exc_info:
        validate_git_repository()
    assert exc_info.value.code == 1


def test_get_git_info(mock_repo):
    """Test getting git repository information."""
    branch_name, remote_url, domain, repo_root = get_git_info(mock_repo)
    assert branch_name == "main"
    assert remote_url == "https://github.com/user/repo.git"
    assert domain == "https://github.com"
    assert repo_root == "/path/to/repo"


def test_get_git_info_ssh(mock_repo_ssh):
    """Test getting git repository information with SSH URL."""
    branch_name, remote_url, domain, repo_root = get_git_info(mock_repo_ssh)
    assert branch_name == "main"
    assert remote_url == "git@github.com:user/repo.git"
    assert domain == "https://github.com"
    assert repo_root == "/path/to/repo"


def test_get_git_info_no_remote():
    """Test getting git repository information with no remote."""
    mock = MagicMock(spec=git.Repo)
    mock.active_branch.name = "main"
    mock_remote = MagicMock()
    mock_remote.urls = iter([])  # Empty iterator to simulate no remote
    mock.remote.return_value = mock_remote
    mock.git.rev_parse.return_value = "/path/to/repo"

    branch_name, remote_url, domain, repo_root = get_git_info(mock)
    assert branch_name == "main"
    assert remote_url == ""
    assert domain == ""
    assert repo_root == "/path/to/repo"


@patch("os.path.exists", return_value=True)
@patch("pathlib.Path.absolute")
def test_get_normalized_project_dir(mock_absolute, mock_exists):
    """Test normalizing project directory paths."""
    repo_root = "/path/to/repo"
    mock_absolute.return_value.as_posix.return_value = "/path/to/repo/project"

    # Test with current directory
    result = get_normalized_project_dir(".", repo_root)
    assert result == "project"

    # Test with absolute path
    result = get_normalized_project_dir("/path/to/repo/project", repo_root)
    assert result == "/path/to/repo/project"

    # Test with relative path
    result = get_normalized_project_dir("project", repo_root)
    assert result == "project"


@patch("pathlib.Path.exists")
@patch("pathlib.Path.mkdir")
def test_get_normalized_project_dir_errors(mock_mkdir, mock_exists, mock_repo):
    """Test error handling in project directory normalization."""
    repo_root = "/path/to/repo"
    mock_exists.return_value = False

    # Test with non-existent directory
    with pytest.raises(SystemExit) as exc_info:
        get_normalized_project_dir("nonexistent", repo_root)
    assert exc_info.value.code == 1

    # Test with error creating directory
    mock_mkdir.side_effect = OSError("Permission denied")
    with pytest.raises(SystemExit) as exc_info:
        get_normalized_project_dir("newdir", repo_root)
    assert exc_info.value.code == 1


def test_display_panel_message(capsys):
    """Test panel message display."""
    display_panel_message("Test", "Hello World", "green")
    captured = capsys.readouterr()
    assert "Hello World" in captured.out


def test_display_panel_message_error(capsys):
    """Test panel message display with error style."""
    display_panel_message("Error", "Something went wrong", "red")
    captured = capsys.readouterr()
    assert "Something went wrong" in captured.out
    assert "Error" in captured.out


@pytest.fixture
def mock_release_mate_dir(tmp_path):
    """Create a mock .release-mate directory with test projects."""
    release_mate_dir = tmp_path / ".release-mate"
    release_mate_dir.mkdir()
    (release_mate_dir / "project1.toml").touch()
    (release_mate_dir / "project2.toml").touch()
    return release_mate_dir


@patch("os.path.exists", return_value=True)
@patch("git.Repo")
def test_get_available_project_ids(mock_repo, mock_exists, mock_release_mate_dir):
    """Test retrieving available project IDs."""
    mock_repo.return_value.git.rev_parse.return_value = str(
        mock_release_mate_dir.parent)
    with patch("pathlib.Path.home", return_value=mock_release_mate_dir.parent):
        project_ids = get_available_project_ids()
        assert set(project_ids) == {"project1", "project2"}


def test_cli_version(cli_runner):
    """Test the version command of the CLI."""
    result = cli_runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


@patch("os.path.exists")
@patch("release_mate.cli.cookiecutter")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.exists", return_value=False)
@patch("pkg_resources.resource_filename")
@patch("release_mate.cli.get_normalized_project_dir")
def test_cli_init_command(mock_get_normalized_project_dir, mock_resource_filename, mock_path_exists, mock_mkdir, mock_cookiecutter, mock_exists, cli_runner, mock_repo):
    """Test the init command of the CLI."""
    mock_resource_filename.return_value = "/path/to/template"
    mock_get_normalized_project_dir.return_value = "."

    # Mock os.path.exists to return False for pyproject.toml, poetry.lock, and package-meta-data.xml
    def mock_exists_side_effect(path):
        if isinstance(path, Path):
            path = str(path)
        if any(x in str(path) for x in ['pyproject.toml', 'poetry.lock', 'package-meta-data.xml']):
            return False
        return True

    mock_exists.side_effect = mock_exists_side_effect

    with patch("git.Repo") as mock_git_repo:
        mock_git_repo.return_value = mock_repo
        result = cli_runner.invoke(cli, [
            "init",
            "--id", "test-project",
            "--current-version", "0.1.0",
            "--dir", "."
        ], catch_exceptions=False)

        print(f"Exit code: {result.exit_code}")
        print(f"Output: {result.output}")
        print(f"Exception: {result.exception}")

        assert result.exit_code == 0

        # Verify cookiecutter was called with correct arguments
        mock_cookiecutter.assert_called_once_with(
            "/path/to/template",
            no_input=True,
            output_dir="/path/to/repo",
            extra_context={
                'project_id': "test-project",
                'project_directory': ".",
                'branch': "main",
                'remote_url': "https://github.com/user/repo.git",
                'domain': "https://github.com",
                'repo_root': "/path/to/repo",
                'poetry_syntax': False
            },
            overwrite_if_exists=True
        )


def test_build_version_args():
    """Test building version command arguments."""
    # Test with all flags set to True
    args = build_version_args(True, True, False, False,
                              False, True, True, True, True)
    assert args == ["--noop", "--major"]

    # Test with all flags set to False
    args = build_version_args(
        False, False, False, False, False, False, False, False, False)
    assert args == ["--no-commit", "--no-tag", "--no-changelog", "--no-push"]

    # Test with mixed flags
    args = build_version_args(True, False, True, False,
                              True, False, True, False, True)
    assert args == ["--noop", "--minor", "--no-commit", "--no-changelog"]


@patch("subprocess.run")
@patch("os.getcwd")
@patch("os.chdir")
def test_run_semantic_release_success(mock_chdir, mock_getcwd, mock_run):
    """Test successful semantic-release command execution."""
    mock_getcwd.return_value = "/original/dir"
    mock_run.return_value = MagicMock(
        stdout="Version updated",
        stderr="",
        returncode=0
    )

    config_file = Path("/path/to/config")
    args = ["--noop"]
    repo_path = "/path/to/repo"

    run_semantic_release(config_file, args, repo_path)

    # Verify directory changes
    assert mock_chdir.call_args_list == [
        call("/path/to/repo"),
        call("/original/dir")
    ]

    # Verify semantic-release command
    mock_run.assert_called_once_with(
        ["semantic-release", "-c", str(config_file), "--noop", "version"],
        check=True,
        capture_output=True,
        text=True
    )


@patch("subprocess.run")
@patch("os.getcwd")
@patch("os.chdir")
def test_run_semantic_release_failure(mock_chdir, mock_getcwd, mock_run):
    """Test semantic-release command failure."""
    mock_getcwd.return_value = "/original/dir"
    error = subprocess.CalledProcessError(1, "cmd")
    error.stdout = ""
    error.stderr = "Failed to update version"
    mock_run.side_effect = error

    config_file = Path("/path/to/config")
    args = ["--noop"]
    repo_path = "/path/to/repo"

    with pytest.raises(SystemExit) as exc_info:
        run_semantic_release(config_file, args, repo_path)

    assert exc_info.value.code == 1
    assert mock_chdir.call_args_list == [
        call("/path/to/repo"),
        call("/original/dir")
    ]


@patch("subprocess.run")
@patch("os.getcwd")
@patch("os.chdir")
def test_run_semantic_release_changelog_success(mock_chdir, mock_getcwd, mock_run):
    """Test successful semantic-release changelog command execution."""
    mock_getcwd.return_value = "/original/dir"
    mock_run.return_value = MagicMock(
        stdout="Changelog updated",
        stderr="",
        returncode=0
    )

    config_file = Path("/path/to/config")
    args = ["--noop"]
    repo_path = "/path/to/repo"

    run_semantic_release_changelog(config_file, args, repo_path)

    # Verify directory changes
    assert mock_chdir.call_args_list == [
        call("/path/to/repo"),
        call("/original/dir")
    ]

    # Verify semantic-release command
    mock_run.assert_called_once_with(
        ["semantic-release", "-c", str(config_file), "--noop", "changelog"],
        check=True,
        capture_output=True,
        text=True
    )


@patch("subprocess.run")
@patch("os.getcwd")
@patch("os.chdir")
def test_run_semantic_release_changelog_failure(mock_chdir, mock_getcwd, mock_run):
    """Test semantic-release changelog command failure."""
    mock_getcwd.return_value = "/original/dir"
    error = subprocess.CalledProcessError(1, "cmd")
    error.stdout = ""
    error.stderr = "Failed to update changelog"
    mock_run.side_effect = error

    config_file = Path("/path/to/config")
    args = ["--noop"]
    repo_path = "/path/to/repo"

    with pytest.raises(SystemExit) as exc_info:
        run_semantic_release_changelog(config_file, args, repo_path)

    assert exc_info.value.code == 1
    assert mock_chdir.call_args_list == [
        call("/path/to/repo"),
        call("/original/dir")
    ]


def test_identify_branch(tmp_path):
    """Test parsing project configuration file for branch."""
    config_file = tmp_path / "config.toml"
    config_content = """[tool.semantic_release.branches.main]
version_variable = "example/__init__.py:__version__"
branch = "main"
"""
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(config_content)

    with patch("tomli.load") as mock_load:
        mock_load.return_value = {
            "tool": {"semantic_release": {"branch": "main"}}}
        branch = identify_branch(config_file)
        assert branch == "main"

    # Test with missing branch
    config_content = """[tool.semantic_release]
version_variable = "example/__init__.py:__version__"
"""
    config_file.write_text(config_content)

    branch = identify_branch(config_file)
    assert branch is None


def test_identify_branch_error(tmp_path):
    """Test error handling in branch identification."""
    config_file = tmp_path / "config.toml"

    # Test with invalid TOML
    config_file.write_text("Invalid TOML")
    branch = identify_branch(config_file)
    assert branch is None

    # Test with missing semantic_release section
    config_content = """[tool.other_tool]
branch = "main"
"""
    config_file.write_text(config_content)
    branch = identify_branch(config_file)
    assert branch is None


@patch("release_mate.cli.run_semantic_release")
@patch("release_mate.cli.get_project_config_file")
@patch("git.Repo")
def test_version_worker(mock_repo, mock_get_config, mock_run_semantic_release):
    """Test version worker function."""
    # Setup mocks
    mock_repo.return_value.active_branch.name = "main"
    mock_get_config.return_value = Path("/path/to/config.toml")
    mock_repo.return_value.git.rev_parse.return_value = "/path/to/repo"

    # Mock config file existence
    with patch("pathlib.Path.exists", return_value=True):
        # Test with default arguments
        version_worker(project_id="test-project")
        mock_run_semantic_release.assert_called_once()
        args = mock_run_semantic_release.call_args[0][1]
        assert not any(arg in args for arg in [
                       "--noop", "--major", "--minor", "--patch", "--prerelease"])

        # Test with various flags
        mock_run_semantic_release.reset_mock()
        version_worker(
            project_id="test-project",
            noop=True,
            major=True,
            commit=False,
            tag=False,
            changelog=False,
            push=False
        )
        mock_run_semantic_release.assert_called_once()
        args = mock_run_semantic_release.call_args[0][1]
        assert "--noop" in args
        assert "--major" in args
        assert "--no-commit" in args
        assert "--no-tag" in args
        assert "--no-changelog" in args
        assert "--no-push" in args


@patch("release_mate.cli.run_semantic_release")
@patch("release_mate.cli.get_project_config_file")
@patch("git.Repo")
def test_version_worker_error_handling(mock_repo, mock_get_config, mock_run_semantic_release):
    """Test version worker error handling."""
    # Setup mocks
    mock_repo.return_value.active_branch.name = "main"
    mock_get_config.return_value = Path("/path/to/config.toml")
    mock_repo.return_value.git.rev_parse.return_value = "/path/to/repo"

    # Test with non-existent config file
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(SystemExit) as exc_info:
            version_worker(project_id="test-project")
        assert exc_info.value.code == 1

    # Test with semantic-release error
    with patch("pathlib.Path.exists", return_value=True):
        mock_run_semantic_release.side_effect = Exception(
            "Semantic release failed")
        with pytest.raises(SystemExit) as exc_info:
            version_worker(project_id="test-project")
        assert exc_info.value.code == 1


@patch("git.Repo")
def test_create_git_tag_success(mock_repo):
    """Test successful git tag creation."""
    mock_instance = MagicMock()
    mock_repo.return_value = mock_instance
    mock_instance.git.tag.side_effect = None

    create_git_tag("v1.0.0")
    mock_instance.git.tag.assert_called_once_with("v1.0.0")


@patch("git.Repo")
def test_create_git_tag_failure(mock_repo):
    """Test git tag creation failure."""
    mock_instance = MagicMock()
    mock_repo.return_value = mock_instance
    mock_instance.git.tag.side_effect = git.GitCommandError(
        "git tag", 128, stderr="fatal: tag 'v1.0.0' already exists")

    # Should not raise SystemExit, just display warning
    create_git_tag("v1.0.0")


def test_batch_version_success(cli_runner):
    """Test successful batch version update."""
    with patch("release_mate.cli.get_available_project_ids") as mock_get_projects, \
            patch("release_mate.cli.validate_git_repository") as mock_validate_repo, \
            patch("release_mate.cli.version_worker") as mock_version_worker, \
            patch("release_mate.cli.get_git_info") as mock_get_git_info, \
            patch("release_mate.cli.get_project_config_file") as mock_get_config, \
            patch("release_mate.cli.identify_branch") as mock_identify_branch, \
            patch("pathlib.Path.glob") as mock_glob:

        mock_repo_instance = MagicMock()
        mock_repo_instance.active_branch.name = "main"
        mock_repo_instance.git.checkout.return_value = None
        mock_validate_repo.return_value = mock_repo_instance
        mock_version_worker.return_value = None
        mock_get_git_info.return_value = ("main", "", "", "/path/to/repo")
        mock_get_config.return_value = Path("/path/to/config")
        mock_identify_branch.return_value = "main"
        mock_glob.return_value = [Path("/path/to/repo/.release-mate/project1.toml"),
                                  Path("/path/to/repo/.release-mate/project2.toml")]

        result = cli_runner.invoke(cli, ["batch-version", "--minor"])
        assert result.exit_code == 0
        assert mock_version_worker.call_count == 2


def test_batch_version_no_projects(cli_runner):
    """Test batch version with no available projects."""
    with patch("release_mate.cli.get_available_project_ids") as mock_get_projects, \
            patch("release_mate.cli.validate_git_repository") as mock_validate_repo, \
            patch("release_mate.cli.get_git_info") as mock_get_git_info:

        mock_get_projects.return_value = []
        mock_validate_repo.return_value = MagicMock()
        mock_get_git_info.return_value = ("main", "", "", "/path/to/repo")

        result = cli_runner.invoke(cli, ["batch-version", "--minor"])
        assert result.exit_code == 0  # Should not fail, just skip processing


def test_changelog_success(cli_runner):
    """Test successful changelog generation."""
    with patch("release_mate.cli.validate_git_repository") as mock_validate_repo, \
            patch("release_mate.cli.get_project_config_file") as mock_get_config, \
            patch("release_mate.cli.run_semantic_release_changelog") as mock_run_changelog, \
            patch("release_mate.cli.get_git_info") as mock_get_git_info, \
            patch("release_mate.cli.identify_branch") as mock_identify_branch, \
            patch("pathlib.Path.exists") as mock_exists:

        mock_repo_instance = MagicMock()
        mock_repo_instance.active_branch.name = "main"
        mock_validate_repo.return_value = mock_repo_instance
        mock_config_path = Path("/path/to/config")
        mock_get_config.return_value = mock_config_path
        mock_exists.return_value = True
        mock_run_changelog.return_value = None
        mock_get_git_info.return_value = ("main", "", "", "/path/to/repo")
        mock_identify_branch.return_value = "main"

        result = cli_runner.invoke(cli, ["changelog"])
        assert result.exit_code == 0


def test_changelog_failure(cli_runner):
    """Test changelog generation failure."""
    with patch("release_mate.cli.validate_git_repository") as mock_validate_repo, \
            patch("release_mate.cli.get_project_config_file") as mock_get_config, \
            patch("release_mate.cli.run_semantic_release_changelog") as mock_run_changelog, \
            patch("release_mate.cli.get_git_info") as mock_get_git_info, \
            patch("release_mate.cli.identify_branch") as mock_identify_branch, \
            patch("pathlib.Path.exists") as mock_exists:

        mock_repo_instance = MagicMock()
        mock_repo_instance.active_branch.name = "main"
        mock_validate_repo.return_value = mock_repo_instance
        mock_config_path = Path("/path/to/config")
        mock_get_config.return_value = mock_config_path
        mock_exists.return_value = True
        mock_run_changelog.side_effect = subprocess.CalledProcessError(
            1, "semantic-release changelog", stderr=b"Error generating changelog")
        mock_get_git_info.return_value = ("main", "", "", "/path/to/repo")
        mock_identify_branch.return_value = "main"

        result = cli_runner.invoke(cli, ["changelog"])
        assert result.exit_code == 1


@patch("release_mate.cli.validate_git_repository")
@patch("release_mate.cli.get_project_config_file")
def test_version_worker_print_version(mock_get_config, mock_validate_repo, mock_repo, tmp_path):
    """Test version worker with print version flag."""
    mock_validate_repo.return_value = mock_repo

    # Create a mock project configuration
    config_file = tmp_path / ".release-mate" / "test-project" / "config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""[tool.semantic_release]
version_variable = "example/__init__.py:__version__"
branch = "main"
""")

    mock_get_config.return_value = config_file

    with patch("release_mate.cli.run_semantic_release") as mock_run, \
            patch("release_mate.cli.get_git_info") as mock_get_git_info:
        mock_run.return_value = None  # run_semantic_release doesn't return anything
        mock_get_git_info.return_value = ("main", "", "", str(tmp_path))

        result = version_worker(
            project_id="test-project",
            print_version=True,
            noop=False,
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
            push=True
        )
        assert result is None  # version_worker doesn't return anything
