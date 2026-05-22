"""
Tests for Git Ignore Patterns

Validates that sensitive files are properly ignored by git.
"""

import os
import subprocess
import tempfile
from pathlib import Path


def test_env_backup_files_ignored():
    """Test that .env backup files are ignored"""
    # Read gitignore
    gitignore_path = Path(__file__).parent.parent.parent / '.gitignore'
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
    
    # Check for .env patterns
    assert '.env.*' in gitignore_content or '.env*' in gitignore_content
    assert '!.env.example' in gitignore_content
    
    # Verify patterns
    sensitive_patterns = [
        '.env.backup',
        '.env.backup.20251102_134032',
        '.env.local',
        '.env.production',
        '*.backup',
        '*.backup.*',
    ]
    
    for pattern in sensitive_patterns:
        # These should be ignored (note: this is a simplified check)
        # In real scenario, would use gitpython or similar
        assert '.env' in gitignore_content or '*.backup' in gitignore_content


def test_env_example_not_ignored():
    """Test that .env.example is explicitly NOT ignored"""
    gitignore_path = Path(__file__).parent.parent.parent / '.gitignore'
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
    
    # Should have exception for .env.example
    assert '!.env.example' in gitignore_content


def test_secret_files_ignored():
    """Test that secret files are ignored"""
    gitignore_path = Path(__file__).parent.parent.parent / '.gitignore'
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
    
    secret_patterns = [
        '*.key',
        '*.pem',
        '.secrets.*',
        'keys/',
    ]
    
    for pattern in secret_patterns:
        assert pattern in gitignore_content


def test_backup_files_ignored():
    """Test that backup files are ignored"""
    gitignore_path = Path(__file__).parent.parent.parent / '.gitignore'
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
    
    backup_patterns = [
        'backups/',
        '*.backup',
        '*.backup.*',
    ]
    
    for pattern in backup_patterns:
        assert pattern in gitignore_content


def test_git_check_ignore_command():
    """Test using git check-ignore to verify patterns"""
    test_files = [
        '.env.backup.20251102_134032',
        '.env.local',
        '.env.production',
        'secrets.key',
        'private.pem',
        'test.backup',
    ]
    
    allowed_files = [
        '.env.example',
    ]
    
    repo_root = Path(__file__).parent.parent.parent
    
    # Test that sensitive files would be ignored
    for test_file in test_files:
        result = subprocess.run(
            ['git', 'check-ignore', test_file],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        # Exit code 0 means file IS ignored (which is what we want)
        # Exit code 1 means file is NOT ignored
        assert result.returncode == 0, f"{test_file} should be ignored but isn't"
    
    # Test that .env.example is not ignored
    for allowed_file in allowed_files:
        result = subprocess.run(
            ['git', 'check-ignore', allowed_file],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        # Exit code 1 means file is NOT ignored (which is what we want for .env.example)
        assert result.returncode == 1, f"{allowed_file} should NOT be ignored but is"


def test_env_backup_not_in_git():
    """Test that .env.backup.20251102_134032 was removed from git"""
    repo_root = Path(__file__).parent.parent.parent
    
    # Check if file exists in git
    result = subprocess.run(
        ['git', 'ls-files', '.env.backup.20251102_134032'],
        cwd=repo_root,
        capture_output=True,
        text=True
    )
    
    # Should return empty (file not tracked)
    assert result.stdout.strip() == '', ".env.backup.20251102_134032 should not be in git"
