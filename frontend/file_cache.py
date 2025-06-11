"""File content cache implementation.

This module provides a generic file content cache that can be used to track changes
in files matching specified glob patterns. It uses MD5 hashes of file contents to
detect changes and supports parallel hash computation.
"""

import concurrent.futures
import glob
import hashlib
import json
import os
from typing import Iterable


class FileCache:
    """Cache for tracking file content changes using MD5 hashes."""

    def __init__(self, cache_file: str, patterns: Iterable[str]) -> None:
        """Initialize the file cache.

        Args:
            cache_file: Path to the cache file
            patterns: Glob patterns for files to track
        """
        self._cache_file = cache_file
        self._patterns = patterns

    def _get_files(self) -> list[str]:
        """Get all files matching the patterns."""
        files = []
        for pattern in self._patterns:
            files.extend(glob.glob(pattern, recursive=True))
        return sorted(files)  # Sort for deterministic order

    def _get_file_hash(self, file_path: str) -> tuple[str, str]:
        """Calculate MD5 hash of file contents."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return file_path, hash_md5.hexdigest()

    def _get_file_hashes(self) -> dict[str, str]:
        """Get content hashes for all matching files in parallel."""
        files = self._get_files()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map returns results in the same order as input
            results = dict(executor.map(self._get_file_hash, files))
        return results

    def _load_cache(self) -> dict[str, str]:
        """Load the cache file if it exists."""
        if not os.path.exists(self._cache_file):
            return {}
        try:
            with open(self._cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_cache(self, hashes: dict[str, str]) -> None:
        """Save the current file hashes to cache."""
        os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
        with open(self._cache_file, "w", encoding="utf-8") as f:
            json.dump(hashes, f)

    def has_changes(self) -> bool:
        """Check if any files have changed since last cache update."""
        current_hashes = self._get_file_hashes()
        cached_hashes = self._load_cache()

        # If cache is empty or files were added/removed
        if set(current_hashes.keys()) != set(cached_hashes.keys()):
            return True

        # Check if any file content has changed
        for file_path, current_hash in current_hashes.items():
            if file_path not in cached_hashes or current_hash != cached_hashes[file_path]:
                return True

        return False

    def update_cache(self) -> None:
        """Update the cache with current file hashes."""
        current_hashes = self._get_file_hashes()
        self._save_cache(current_hashes)
