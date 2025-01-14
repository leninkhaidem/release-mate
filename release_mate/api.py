"""Command line interface for release-mate tool."""
import dataclasses
import os
import re
import subprocess
import sys
import traceback
import typing
from pathlib import Path
from typing import List, Optional

import git
import pkg_resources
from cookiecutter.main import cookiecutter
from git.exc import GitCommandError
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

console = Console()


@dataclasses.dataclass
class ProjectConfig:
    project_id: str
    project_directory: str
    branch: str
    remote_url: str
    domain: str
    repo_root: str
    poetry_syntax: bool

    def as_dict(self):
        return dataclasses.asdict(self)


def validate_git_repository() -> git.Repo:
    """
    Validate if the current directory is a git repository.

    Returns:
        git.Repo: Git repository object
    """
    try:
        return git.Repo(os.getcwd(), search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        display_panel_message(
            "Error",
            "Not a git repository. Please run this command inside a git repository.",
            "red"
        )
        sys.exit(1)


def get_git_info(repo: git.Repo) -> typing.Tuple[str, str, str, str]:
    """
    Get git repository information.

    Args:
        repo (git.Repo): Git repository object

    Returns:
        tuple[str, str, str, str]: Current branch name, remote URL, domain in format protocol://domain.tld, and repo root path
    """
    branch = repo.active_branch.name
    remote_url = ""
    domain = ""
    try:
        remote_url = next(repo.remote().urls)
        # Extract domain from remote URL
        if remote_url:
            if remote_url.startswith('git@'):
                # SSH format: git@github.com:user/repo.git
                domain = 'https://' + remote_url.split('@')[1].split(':')[0]
            elif remote_url.startswith('https://') or remote_url.startswith('http://'):
                # HTTPS format: https://github.com/user/repo.git
                domain = remote_url.split(
                    '/')[0] + '//' + remote_url.split('/')[2]
    except (StopIteration, GitCommandError) as e:
        display_panel_message(
            "Error", f"Error retrieving remote URL: {e}", "red")
        # Return default values
        return branch, "", "", repo.git.rev_parse("--show-toplevel")

    return branch, remote_url, domain, repo.git.rev_parse("--show-toplevel")


def get_relative_path(root_path: str, target_path: str) -> str:
    """
    Get the relative path of target_path from source_path.

    Args:
        repo_root (str): The base path from which to calculate the relative path.
        target_path (str): The path to be made relative.

    Returns:
        str: The relative path from source_path to target_path.
    """
    return os.path.relpath(target_path, root_path)


def get_normalized_project_dir(project_dir: str, repo_root: str) -> str:
    """
    Get the normalized project directory.
    """
    dir = get_relative_path(repo_root, Path(project_dir).absolute(
    ).as_posix()) if project_dir == "." else project_dir
    if not os.path.exists(Path(repo_root) / dir):
        display_panel_message(
            "Error",
            f"Project directory {dir!r} does not exist",
            "red"
        )
        sys.exit(1)
    return dir


def display_panel_message(title: str, message: str, color: str = "green"):
    rprint(Panel.fit(
        message,
        title=title,
        border_style=color
    ))


def create_git_tag(tag: str):
    repo = validate_git_repository()
    try:
        repo.git.tag(tag)
    except GitCommandError:
        display_panel_message(
            "Warning",
            f"Tag {tag} already exists. Skipping tag creation.",
            "yellow"
        )


def get_project_config(project_id: str, project_dir: str) -> ProjectConfig:
    repo = validate_git_repository()
    branch, remote_url, domain, repo_root = get_git_info(repo)
    project_id = project_id or branch
    poetry_syntax = any(os.path.exists(Path(repo_root) / project_dir / _x)
                        for _x in {'pyproject.toml', 'poetry.lock'})
    return ProjectConfig(
        project_id=project_id,
        project_directory=get_normalized_project_dir(project_dir, repo_root),
        branch=branch,
        remote_url=remote_url,
        domain=domain,
        repo_root=repo_root,
        poetry_syntax=poetry_syntax
    )


def validate_config_file(project_id, config):
    config_file = get_project_config_file(project_id, config.repo_root)
    if config_file.exists():
        display_panel_message(
            "Error",
            f"Project {project_id!r} already exists in .release-mate directory",
            "red"
        )
        sys.exit(1)
    return config_file


def run_semantic_release(config_file: Path, args: List[str], repo_path: str) -> None:
    """
    Run semantic-release command with the given configuration file and arguments.

    Args:
        config_file (Path): Path to the semantic-release configuration file
        args (List[str]): List of arguments to pass to semantic-release
        repo_path (str): Path to the git repository root
    """
    # Split args into pre-version and post-version args
    pre_version_args = []
    post_version_args = []

    for arg in args:
        if arg == "--noop":
            pre_version_args.append(arg)
        else:
            post_version_args.append(arg)

    cmd = ["semantic-release", "-c",
           str(config_file)] + pre_version_args + ["version"] + post_version_args

    # Store current directory
    current_dir = os.getcwd()
    try:
        # Change to repo directory
        os.chdir(repo_path)

        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            display_panel_message(
                "Versioning Logs",
                result.stdout,
                "blue"
            )
        if result.stderr:
            display_panel_message(
                "Versioning Logs",
                result.stderr,
                "red"
            )
    except subprocess.CalledProcessError as e:
        display_panel_message(
            "Error",
            f"Failed to run semantic-release: {e.stderr}",
            "red"
        )
        sys.exit(1)
    finally:
        # Always restore original directory
        os.chdir(current_dir)


def get_available_project_ids() -> List[str]:
    """
    Get list of available project IDs from .release-mate directory.

    Returns:
        List[str]: List of project IDs
    """
    try:
        repo = validate_git_repository()
        _, _, _, repo_root = get_git_info(repo)
        release_mate_dir = Path(repo_root) / '.release-mate'

        if not release_mate_dir.exists():
            return []

        return [f.stem for f in release_mate_dir.glob('*.toml')]
    except Exception:
        return []


def project_id_completion(ctx, param, incomplete):
    """Shell completion for project IDs."""
    return [id for id in get_available_project_ids() if id.startswith(incomplete)]


def version_worker(
    project_id: Optional[str] = None,
    noop: bool = False,
    print_version: bool = False,
    print_tag: bool = False,
    print_last_released: bool = False,
    print_last_released_tag: bool = False,
    major: bool = False,
    minor: bool = False,
    patch: bool = False,
    prerelease: bool = False,
    commit: bool = True,
    tag: bool = True,
    changelog: bool = True,
    push: bool = True
) -> None:
    """
    Core worker function for performing version bumps.

    Args:
        project_id (Optional[str]): Project identifier. If None, uses current branch name.
        noop (bool): Dry run without making changes
        print_version (bool): Print the next version and exit
        print_tag (bool): Print the next version tag and exit
        print_last_released (bool): Print the last released version and exit
        print_last_released_tag (bool): Print the last released version tag and exit
        major (bool): Force major version bump
        minor (bool): Force minor version bump
        patch (bool): Force patch version bump
        prerelease (bool): Force prerelease version bump
        commit (bool): Whether to commit changes locally
        tag (bool): Whether to create a tag for the new version
        changelog (bool): Whether to update the changelog
        push (bool): Whether to push the new commit and tag to the remote
    """
    try:
        repo = validate_git_repository()
        branch, _, _, repo_root = get_git_info(repo)
        project_id = project_id or branch

        # Check if project config exists
        config_file = get_config_file(project_id, repo_root)
        if not config_file.exists():
            display_panel_message(
                "Error",
                f"Project {project_id!r} does not exist in .release-mate directory",
                "red"
            )
            sys.exit(1)

        # Validate version flags
        version_flags = [major, minor, patch, prerelease]
        if sum(version_flags) > 1:
            display_panel_message(
                "Error",
                "Only one version type flag can be specified at a time",
                "red"
            )
            sys.exit(1)

        # Build semantic-release arguments
        args = build_version_args(
            noop, major, minor, patch, prerelease,
            commit, tag, changelog, push
        )

        # Handle print flags (mutually exclusive)
        print_flags = [print_version, print_tag,
                       print_last_released, print_last_released_tag]
        if sum(print_flags) > 1:
            display_panel_message(
                "Error",
                "Only one print flag can be specified at a time",
                "red"
            )
            sys.exit(1)

        if print_version:
            args.append("--print")
        elif print_tag:
            args.append("--print-tag")
        elif print_last_released:
            args.append("--print-last-released")
        elif print_last_released_tag:
            args.append("--print-last-released-tag")

        display_panel_message(
            "Release Mate Version",
            f"Running semantic-release for project [bold green]{project_id}[/bold green]{' (dry run)' if noop else ''}",
            "blue"
        )

        run_semantic_release(config_file, args, repo_root)

    except Exception as e:
        console.print_exception()
        sys.exit(1)


def get_project_config_file(project_id: str, repo_root: str) -> Path:
    """
    Get the path to the project's configuration file.

    Args:
        project_id (str): Project identifier
        repo_root (str): Git repository root path

    Returns:
        Path: Path to the project's configuration file
    """
    return Path(repo_root) / '.release-mate' / f"{project_id}.toml"


def run_semantic_release_changelog(config_file: Path, args: List[str], repo_path: str) -> None:
    """
    Run semantic-release changelog command with the given configuration file and arguments.

    Args:
        config_file (Path): Path to the semantic-release configuration file
        args (List[str]): List of arguments to pass to semantic-release
        repo_path (str): Path to the git repository root
    """
    # Split args into pre-command and post-command args
    pre_command_args = []
    post_command_args = []

    for arg in args:
        if arg == "--noop":
            pre_command_args.append(arg)
        else:
            post_command_args.append(arg)

    cmd = ["semantic-release", "-c",
           str(config_file)] + pre_command_args + ["changelog"] + post_command_args

    # Store current directory
    current_dir = os.getcwd()
    try:
        # Change to repo directory
        os.chdir(repo_path)

        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            display_panel_message(
                "Changelog Logs",
                result.stdout,
                "blue"
            )
        if result.stderr:
            display_panel_message(
                "Changelog Logs",
                result.stderr,
                "red"
            )
    except subprocess.CalledProcessError as e:
        display_panel_message(
            "Error",
            f"Failed to run semantic-release changelog: {e.stderr}",
            "red"
        )
        sys.exit(1)
    finally:
        # Always restore original directory
        os.chdir(current_dir)


def get_config_file(project_id, repo_root):
    config_file = Path(project_id) if os.path.isfile(
        project_id) else get_project_config_file(project_id, repo_root)
    return config_file


def identify_branch(config_file: Path) -> Optional[str]:
    """
    Parse a project configuration file to extract the branch.

    Args:
        config_file (Path): Path to the project configuration file

    Returns:
        Optional[str]: The branch name if found, otherwise None
    """
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            # Look for the branch match pattern
            branch_match = re.search(
                r'\[.*semantic_release\.branches\.(\w+)\]', content)
            if branch_match:
                return branch_match.group(1)
    except Exception:
        pass
    return None


def build_version_args(noop: bool, major: bool, minor: bool, patch: bool, prerelease: bool,
                       commit: bool, tag: bool, changelog: bool, push: bool) -> List[str]:
    """
    Build the list of arguments for the version command based on the provided flags.

    Args:
        noop (bool): If true, adds the --noop flag.
        major (bool): If true, adds the --major flag.
        minor (bool): If true, adds the --minor flag.
        patch (bool): If true, adds the --patch flag.
        prerelease (bool): If true, adds the --prerelease flag.
        commit (bool): If false, adds the --no-commit flag.
        tag (bool): If false, adds the --no-tag flag.
        changelog (bool): If false, adds the --no-changelog flag.
        push (bool): If false, adds the --no-push flag.

    Returns:
        List[str]: The constructed list of arguments.
    """
    args = []
    if noop:
        args.append("--noop")
    if major:
        args.append("--major")
    elif minor:
        args.append("--minor")
    elif patch:
        args.append("--patch")
    elif prerelease:
        args.append("--prerelease")
    if not commit:
        args.append("--no-commit")
    if not tag:
        args.append("--no-tag")
    if not changelog:
        args.append("--no-changelog")
    if not push:
        args.append("--no-push")

    return args


def changelog_worker(project_id: str, post_to_release_tag: Optional[str], noop: bool) -> None:
    try:
        repo = validate_git_repository()
        branch, _, _, repo_root = get_git_info(repo)
        project_id = project_id or branch
        # Check if project config exists
        config_file = get_config_file(project_id, repo_root)
        if not config_file.exists():
            display_panel_message(
                "Error",
                f"Project {project_id!r} does not exist in .release-mate directory",
                "red"
            )
            sys.exit(1)

        # Build semantic-release arguments
        args = []

        # Add noop flag if specified
        if noop:
            args.append("--noop")

        # Add post-to-release-tag if specified
        if post_to_release_tag:
            args.append(f"--post-to-release-tag={post_to_release_tag}")

        display_panel_message(
            "Release Mate Changelog",
            f"Generating changelog for project [bold green]{project_id}[/bold green]{' (dry run)' if noop else ''}",
            "blue"
        )

        run_semantic_release_changelog(config_file, args, repo_root)

    except Exception as e:
        console.print_exception()
        sys.exit(1)


def batch_version_worker(noop: bool, major: bool, minor: bool, patch: bool, prerelease: bool, commit: bool, tag: bool, changelog: bool, push: bool):
    try:
        repo = validate_git_repository()
        _, _, _, repo_root = get_git_info(repo)
        release_mate_dir = Path(repo_root) / '.release-mate'

        # Validate version flags
        version_flags = [major, minor, patch, prerelease]
        if sum(version_flags) > 1:
            display_panel_message(
                "Error",
                "Only one version type flag can be specified at a time",
                "red"
            )
            sys.exit(1)

        # Track errors
        errors = []
        current_branch = repo.active_branch.name

        # Iterate through all project configuration files
        for config_file in release_mate_dir.glob('*.toml'):
            project_id = config_file.stem
            branch = identify_branch(config_file)

            if not branch:
                errors.append(
                    f"Could not determine branch for project {project_id}")
                continue

            try:
                # Switch to the target branch
                repo.git.checkout(branch)

                display_panel_message(
                    "Batch Version",
                    f"Processing project [bold green]{project_id}[/bold green] on branch [bold blue]{branch}[/bold blue]",
                    "blue"
                )

                # Call version_worker function directly
                version_worker(
                    project_id=project_id,
                    noop=noop,
                    print_version=False,
                    print_tag=False,
                    print_last_released=False,
                    print_last_released_tag=False,
                    major=major,
                    minor=minor,
                    patch=patch,
                    prerelease=prerelease,
                    commit=commit,
                    tag=tag,
                    changelog=changelog,
                    push=push
                )

            except Exception as e:
                errors.append(
                    f"Error processing project {project_id}: {traceback.format_exc()}")

        # Return to the original branch
        repo.git.checkout(current_branch)

        # Report any errors
        if errors:
            display_panel_message(
                "Batch Version Warnings",
                "\n".join(errors),
                "yellow"
            )

    except Exception as e:
        console.print_exception()
        sys.exit(1)


def init_worker(config: ProjectConfig, current_version: str) -> None:
    try:
        release_mate_dir = Path(config.repo_root) / '.release-mate'
        release_mate_dir.mkdir(exist_ok=True)

        # Check for duplicate project config
        config_file = validate_config_file(config.project_id, config)
        # Get template directory path
        template_dir = pkg_resources.resource_filename(
            __package__ or 'release_mate', 'templates/project')

        _ = cookiecutter(
            template_dir,
            no_input=True,
            output_dir=config.repo_root,
            extra_context=config.as_dict(),
            overwrite_if_exists=True
        )

        display_panel_message(
            "Release Mate Init",
            f"✅ Successfully initialized release-mate for project [bold green]{config.project_id}[/bold green]\n"
            f"📁 Configuration file: [bold blue]{config_file}[/bold blue]\n"
            f"🔧 Make sure to update [bold blue]build_command[/bold blue] and [bold blue]version_variables[/bold blue] in {config_file} to suit your project needs.",
            "green",
        )
        create_git_tag(f"{config.project_id}-{current_version}")

    except Exception as e:
        console.print_exception()
        sys.exit(1)
