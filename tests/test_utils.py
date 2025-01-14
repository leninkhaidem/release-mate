"""Test cases for utility functions."""
import os
from pathlib import Path

from release_mate.api import (get_project_config_file, get_relative_path,
                              identify_branch)


def test_get_relative_path():
    """Test getting relative path."""
    root = "/path/to/repo"
    target = "/path/to/repo/project/file.txt"
    assert get_relative_path(root, target) == "project/file.txt"


def test_get_relative_path_different_drive():
    """Test getting relative path with different drives."""
    if os.name == 'nt':  # Windows
        root = "C:\\path\\to\\repo"
        target = "D:\\other\\path\\file.txt"
        assert get_relative_path(root, target) == "D:/other/path/file.txt"
    else:  # Unix-like
        root = "/path/to/repo"
        target = "/other/path/file.txt"
        assert get_relative_path(
            root, target) == "../../../other/path/file.txt"


def test_identify_branch_empty_file(tmp_path):
    """Test identifying branch from empty file."""
    config = tmp_path / "empty.toml"
    config.touch()
    assert identify_branch(config) is None


def test_identify_branch_invalid_toml(tmp_path):
    """Test identifying branch from invalid TOML file."""
    config = tmp_path / "invalid.toml"
    config.write_text("invalid toml content")
    branch = identify_branch(config)
    assert branch is None


def test_identify_branch_no_branch(tmp_path):
    """Test identifying branch when no branch is configured."""
    config = tmp_path / "no_branch.toml"
    config.write_text("""
[tool.semantic_release]
version_variable = "package/__init__.py:__version__"
""")
    assert identify_branch(config) is None


def test_get_project_config_file_relative_path():
    """Test getting project config file with relative path."""
    result = get_project_config_file("test", "relative/path")
    assert isinstance(result, Path)
    assert str(result) == "relative/path/.release-mate/test.toml"


def test_build_version_args_all_flags():
    """Test building version arguments with all flags enabled."""
    from release_mate.api import build_version_args
    args = build_version_args(True, True, False, False,
                              False, True, True, True, True)
    assert "--noop" in args
    assert "--major" in args


def test_build_version_args_no_flags():
    """Test building version arguments with no flags enabled."""
    from release_mate.api import build_version_args
    args = build_version_args(
        False, False, False, False, False, True, True, True, True)
    assert "--noop" not in args
    assert "--major" not in args
    assert "--minor" not in args
    assert "--patch" not in args
    assert "--prerelease" not in args


def test_display_panel_message_long_text():
    """Test displaying panel message with long text."""
    from release_mate.api import display_panel_message
    long_text = "A" * 100
    display_panel_message("Test", long_text)


def test_display_panel_message_special_chars():
    """Test displaying panel message with special characters."""
    from release_mate.api import display_panel_message
    special_chars = "!@#$%^&*()"
    display_panel_message("Test", special_chars)


def test_display_panel_message_empty():
    """Test displaying panel message with empty text."""
    from release_mate.api import display_panel_message
    display_panel_message("Test", "")
