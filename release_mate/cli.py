"""Command line interface for release-mate tool."""
from typing import Optional

import click
import pkg_resources
from rich.console import Console

from . import __version__, api

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """Release Mate - Simplify release and changelog management."""


@cli.command()
@click.option('--id', '-i', 'project_id', required=False, help='Project identifier')
@click.option('--current-version', '-v0', required=False, default='0.0.0', help='Initial version')
@click.option('--dir', '-d', 'project_dir', default='.', help='Project directory')
def init(
    project_id: str,
    current_version: str,
    project_dir: str,
):
    """Initialize a new release-mate project."""
    config = api.get_project_config(project_id, project_dir)
    template_dir = pkg_resources.resource_filename(
        "release_mate", 'templates/project')
    api.init_worker(config, current_version, template_dir=template_dir)


@cli.command()
@click.option('--id', '-i', 'project_id', required=False, help='Project identifier', shell_complete=api.project_id_completion)
@click.option('--noop', is_flag=True, help='Dry run without making any changes')
@click.option('--print', 'print_version', is_flag=True, help='Print the next version and exit')
@click.option('--print-tag', is_flag=True, help='Print the next version tag and exit')
@click.option('--print-last-released', is_flag=True, help='Print the last released version and exit')
@click.option('--print-last-released-tag', is_flag=True, help='Print the last released version tag and exit')
@click.option('--major', is_flag=True, help='Force the next version to be a major release')
@click.option('--minor', is_flag=True, help='Force the next version to be a minor release')
@click.option('--patch', is_flag=True, help='Force the next version to be a patch release')
@click.option('--prerelease', is_flag=True, help='Force the next version to be a prerelease')
@click.option('--commit/--no-commit', default=True, help='Whether or not to commit changes locally')
@click.option('--tag/--no-tag', default=True, help='Whether or not to create a tag for the new version')
@click.option('--changelog/--no-changelog', default=True, help='Whether or not to update the changelog')
@click.option('--push/--no-push', default=True, help='Whether or not to push the new commit and tag to the remote')
@click.option('--vcs-release/--no-vcs-release', default=True,
              help='Whether or not to create a release in the remote VCS, if supported')
@click.option('--as-prerelease', is_flag=True, help='Ensure the next version to be released is a prerelease version')
@click.option('--prerelease-token', help='Force the next version to use this prerelease token, if it is a prerelease')
@click.option('--build-metadata', help='Build metadata to append to the new version')
@click.option('--skip-build', is_flag=True, help='Skip building the current project')
def version(
    project_id: Optional[str],
    noop: bool,
    print_version: bool,
    print_tag: bool,
    print_last_released: bool,
    print_last_released_tag: bool,
    major: bool,
    minor: bool,
    patch: bool,
    prerelease: bool,
    commit: bool,
    tag: bool,
    changelog: bool,
    push: bool,
    vcs_release: bool,
    as_prerelease: bool,
    prerelease_token: Optional[str],
    build_metadata: Optional[str],
    skip_build: bool
):
    """Perform a version bump using semantic-release."""
    api.version_worker(
        project_id=project_id,
        noop=noop,
        print_version=print_version,
        print_tag=print_tag,
        print_last_released=print_last_released,
        print_last_released_tag=print_last_released_tag,
        major=major,
        minor=minor,
        patch=patch,
        prerelease=prerelease,
        commit=commit,
        tag=tag,
        changelog=changelog,
        push=push,
        vcs_release=vcs_release,
        as_prerelease=as_prerelease,
        prerelease_token=prerelease_token,
        build_metadata=build_metadata,
        skip_build=skip_build
    )


@cli.command()
@click.argument('project-id', required=False, shell_complete=api.project_id_completion)
@click.option('--post-to-release-tag', help='Post the generated release notes to the remote VCS\'s release for this tag')
@click.option('--noop', is_flag=True, help='Dry run without making any changes')
def changelog(
    project_id: str,
    post_to_release_tag: Optional[str],
    noop: bool,
):
    """Generate and optionally publish a changelog for your project."""
    api.changelog_worker(project_id, post_to_release_tag, noop)


@cli.command()
@click.option('--noop', is_flag=True, help='Dry run without making any changes')
@click.option('--major', is_flag=True, help='Force the next version to be a major release')
@click.option('--minor', is_flag=True, help='Force the next version to be a minor release')
@click.option('--patch', is_flag=True, help='Force the next version to be a patch release')
@click.option('--prerelease', is_flag=True, help='Force the next version to be a prerelease')
@click.option('--commit/--no-commit', default=True, help='Whether or not to commit changes locally')
@click.option('--tag/--no-tag', default=True, help='Whether or not to create a tag for the new version')
@click.option('--changelog/--no-changelog', default=True, help='Whether or not to update the changelog')
@click.option('--push/--no-push', default=True, help='Whether or not to push the new commit and tag to the remote')
def batch_version(
    noop: bool,
    major: bool,
    minor: bool,
    patch: bool,
    prerelease: bool,
    commit: bool,
    tag: bool,
    changelog: bool,
    push: bool
):
    """Perform version bumps for all projects in the repository."""
    api.batch_version_worker(noop, major, minor, patch,
                             prerelease, commit, tag, changelog, push)


@cli.command(help="install shell completion for bash, zsh or fish shells")
def install_completion():
    """Install shell completion for bash, zsh, or fish shells."""
    api.install_shell_completion('release-mate')


@cli.command()
@click.option('--id', '-i', 'project_id', required=False, help='Project identifier', shell_complete=api.project_id_completion)
@click.option('--noop', is_flag=True, help='Dry run without making changes')
@click.option('--tag', help='The tag associated with the release to publish to')
def publish(project_id: str, noop: bool, tag: Optional[str]):
    """Build and publish a distribution to a VCS release."""
    api.publish_worker(project_id, noop, tag)


if __name__ == '__main__':
    cli()
