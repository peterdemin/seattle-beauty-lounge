"""Unit tests for the FileCache class."""

import tempfile
from pathlib import Path

import pytest

from .file_cache import FileCache


@pytest.fixture(name="temp_dir")
def temp_dir_fixture():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture(name="cache_file")
def cache_file_fixture(temp_dir):
    """Create a temporary cache file path."""
    return temp_dir / "cache.json"


@pytest.fixture(name="test_files")
def test_files_fixture(temp_dir):
    """Create test files with content."""
    files = {
        "file1.js": "content1",
        "file2.js": "content2",
        "subdir/file3.js": "content3",
    }
    for path, content in files.items():
        full_path = temp_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    return files


def test_cache_creation(cache_file, temp_dir, test_files):
    """Test that cache is created and initialized correctly."""
    del test_files
    cache = FileCache(
        cache_file=str(cache_file),
        patterns=[str(temp_dir / "*.js"), str(temp_dir / "**/*.js")],
    )
    assert cache.has_changes()  # Should detect changes when cache is empty
    cache.update_cache()
    assert not cache.has_changes()  # Should be up to date after update


def test_detect_file_changes(cache_file, temp_dir, test_files):
    """Test that cache detects file content changes."""
    del test_files
    cache = FileCache(
        cache_file=str(cache_file),
        patterns=[str(temp_dir / "*.js"), str(temp_dir / "**/*.js")],
    )
    cache.update_cache()

    # Modify a file
    (temp_dir / "file1.js").write_text("modified content")
    assert cache.has_changes()  # Should detect the change


def test_detect_new_files(cache_file, temp_dir, test_files):
    """Test that cache detects new files."""
    del test_files
    cache = FileCache(
        cache_file=str(cache_file),
        patterns=[str(temp_dir / "*.js"), str(temp_dir / "**/*.js")],
    )
    cache.update_cache()

    # Add a new file
    (temp_dir / "new_file.js").write_text("new content")
    assert cache.has_changes()  # Should detect the new file


def test_detect_deleted_files(cache_file, temp_dir, test_files):
    """Test that cache detects deleted files."""
    del test_files
    cache = FileCache(
        cache_file=str(cache_file),
        patterns=[str(temp_dir / "*.js"), str(temp_dir / "**/*.js")],
    )
    cache.update_cache()

    # Delete a file
    (temp_dir / "file1.js").unlink()
    assert cache.has_changes()  # Should detect the deletion


def test_cache_persistence(cache_file, temp_dir, test_files):
    """Test that cache persists between instances."""
    del test_files
    # Create and update first cache instance
    cache1 = FileCache(
        cache_file=str(cache_file),
        patterns=[str(temp_dir / "*.js"), str(temp_dir / "**/*.js")],
    )
    cache1.update_cache()

    # Create second cache instance
    cache2 = FileCache(
        cache_file=str(cache_file),
        patterns=[str(temp_dir / "*.js"), str(temp_dir / "**/*.js")],
    )
    assert not cache2.has_changes()  # Should read from existing cache


def test_invalid_cache_file(cache_file, temp_dir, test_files):
    """Test handling of invalid cache file."""
    del test_files
    # Create invalid JSON
    cache_file.write_text("invalid json")

    cache = FileCache(
        cache_file=str(cache_file),
        patterns=[str(temp_dir / "*.js"), str(temp_dir / "**/*.js")],
    )
    assert cache.has_changes()  # Should handle invalid cache gracefully


def test_empty_patterns(cache_file, temp_dir):
    """Test behavior with empty patterns."""
    del temp_dir
    cache = FileCache(
        cache_file=str(cache_file),
        patterns=[],
    )
    assert not cache.has_changes()  # Should handle empty patterns gracefully


def test_nonexistent_files(cache_file, temp_dir):
    """Test behavior with patterns matching no files."""
    cache = FileCache(
        cache_file=str(cache_file),
        patterns=[str(temp_dir / "nonexistent/*.js")],
    )
    assert not cache.has_changes()  # Should handle no matching files gracefully
