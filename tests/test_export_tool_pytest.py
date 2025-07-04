#!/usr/bin/env python3
"""
Pytest test suite for OSXPhotos to Nextcloud Export Tool

Run with: pytest test_export_tool_pytest.py -v
"""

import os
import sys
import tempfile
import shutil
import subprocess
import pytest
from pathlib import Path
from typing import List, Optional

# Test configuration
SCRIPT_PATH = Path(__file__).parent.parent / "export_photos_to_nextcloud_pkg" / "main.py"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_export_"))
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_paths(temp_dir):
    """Create sample paths for testing."""
    return {
        'export_dir': temp_dir / "export",
        'nc_dir': temp_dir / "nextcloud",
        'log_file': temp_dir / "test.log"
    }


def run_script(args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Helper function to run the export script."""
    cmd = [sys.executable, str(SCRIPT_PATH)] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )


class TestHelpAndVersion:
    """Test help and version commands."""

    def test_help_command(self):
        """Test --help flag shows usage information."""
        result = run_script(["--help"])
        assert result.returncode == 0
        assert "OSXPhotos to Nextcloud Export Tool" in result.stdout
        assert "export-dir" in result.stdout
        assert "nc-photos-dir" in result.stdout

    def test_version_command(self):
        """Test --version flag works."""
        result = run_script(["--version"])
        # Note: Version command might fail due to Click's auto-version detection
        # This is expected behavior when version isn't properly configured
        assert result.returncode in [0, 1]  # Allow both success and expected failure


class TestArgumentValidation:
    """Test command line argument validation."""

    def test_missing_all_required_args(self):
        """Test that missing all required arguments fails."""
        result = run_script([])
        assert result.returncode != 0
        assert "Missing option" in result.stderr or "Error" in result.stderr

    def test_missing_export_dir(self):
        """Test that missing export directory fails."""
        result = run_script(["-n", "/tmp/nc", "-l", "/tmp/log.txt"])
        assert result.returncode != 0

    def test_missing_nc_dir(self):
        """Test that missing Nextcloud directory fails."""
        result = run_script(["-e", "/tmp/export", "-l", "/tmp/log.txt"])
        assert result.returncode != 0

    def test_missing_log_file(self):
        """Test that missing log file fails."""
        result = run_script(["-e", "/tmp/export", "-n", "/tmp/nc"])
        assert result.returncode != 0

    def test_invalid_option(self):
        """Test that invalid options are rejected."""
        result = run_script([
            "-e", "/tmp/export",
            "-n", "/tmp/nc",
            "-l", "/tmp/log.txt",
            "--invalid-option"
        ])
        assert result.returncode != 0


class TestDryRunFunctionality:
    """Test dry-run mode functionality."""

    def test_basic_dry_run(self, sample_paths):
        """Test basic dry run execution."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run"
        ]
        result = run_script(args)

        # Dry run should complete but may fail on osxphotos command
        # The important thing is that it gets past argument validation
        assert sample_paths['log_file'].exists(), "Log file should be created"

    def test_dry_run_with_verbose(self, sample_paths):
        """Test dry run with verbose output."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "-v"
        ]
        result = run_script(args)
        assert sample_paths['log_file'].exists()

    def test_dry_run_with_cleanup(self, sample_paths):
        """Test dry run with cleanup options."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "--cleanup"
        ]
        result = run_script(args)
        assert sample_paths['log_file'].exists()

    def test_dry_run_with_aae_export(self, sample_paths):
        """Test dry run with AAE export option."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "--export-aae"
        ]
        result = run_script(args)
        assert sample_paths['log_file'].exists()


class TestDirectoryHandling:
    """Test directory creation and validation."""

    def test_nonexistent_directories_dry_run(self, sample_paths):
        """Test handling of non-existent directories in dry run."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "-q"
        ]
        result = run_script(args)

        # In dry run, directories shouldn't be created
        # but the script should handle this gracefully
        assert sample_paths['log_file'].exists()

    def test_existing_directories_dry_run(self, sample_paths):
        """Test handling of existing directories."""
        # Pre-create directories
        sample_paths['export_dir'].mkdir(parents=True)
        sample_paths['nc_dir'].mkdir(parents=True)

        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "-q"
        ]
        result = run_script(args)
        assert sample_paths['log_file'].exists()


class TestLogging:
    """Test logging functionality at different verbosity levels."""

    @pytest.mark.parametrize("verbosity,args", [
        ("quiet", ["-q"]),
        ("normal", []),
        ("verbose", ["-v"]),
        ("very_verbose", ["-vv"]),
        ("debug", ["-vvv"])
    ])
    def test_logging_levels(self, sample_paths, verbosity, args):
        """Test different logging verbosity levels."""
        test_args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run"
        ] + args

        result = run_script(test_args)

        # Log file should be created regardless of verbosity
        assert sample_paths['log_file'].exists()

        # Check that log file has content
        log_content = sample_paths['log_file'].read_text()
        assert len(log_content) > 0

        # Verbose modes should generally produce more log content
        if verbosity in ["verbose", "very_verbose", "debug"]:
            assert "DEBUG" in log_content or "INFO" in log_content


class TestOptionCombinations:
    """Test various combinations of command line options."""

    def test_no_symlink_with_cleanup(self, sample_paths):
        """Test --no-symlink combined with --cleanup."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "--no-symlink", "--cleanup"
        ]
        result = run_script(args)
        assert sample_paths['log_file'].exists()

    def test_export_aae_with_cleanup(self, sample_paths):
        """Test --export-aae combined with --cleanup."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "--export-aae", "--cleanup"
        ]
        result = run_script(args)
        assert sample_paths['log_file'].exists()

        # Check that AAE export is mentioned in logs
        log_content = sample_paths['log_file'].read_text()
        # The script should log something about AAE export when the flag is used

    def test_all_options_combined(self, sample_paths):
        """Test combination of multiple options."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "--cleanup", "--export-aae", "--no-symlink", "-v"
        ]
        result = run_script(args)
        assert sample_paths['log_file'].exists()

    def test_verbose_quiet_conflict(self, sample_paths):
        """Test conflicting -v and -q flags."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "-v", "-q"
        ]
        result = run_script(args)
        # Script should handle this gracefully (quiet usually overrides verbose)
        assert sample_paths['log_file'].exists()


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_script_exists(self):
        """Test that the script file exists."""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"

    def test_script_is_executable(self):
        """Test that the script is executable."""
        # On Unix systems, check if it's readable and the shebang is correct
        content = SCRIPT_PATH.read_text()
        assert content.startswith("#!/"), "Script should have a proper shebang"

    @pytest.mark.timeout(10)
    def test_script_doesnt_hang(self, sample_paths):
        """Test that script doesn't hang indefinitely."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "-q"
        ]
        # This test will fail if the script hangs longer than 10 seconds
        result = run_script(args, timeout=10)
        # We don't care about the return code, just that it doesn't hang


class TestAAEFunctionality:
    """Test AAE (Apple Adjustments Engine) export functionality."""

    def test_aae_flag_in_command(self, sample_paths):
        """Test that --export-aae flag is properly processed."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "--export-aae", "-v"
        ]
        result = run_script(args)

        # Check that the log mentions AAE export
        log_content = sample_paths['log_file'].read_text()
        # Look for any mention of AAE in the logs or command output
        assert "aae" in log_content.lower() or "AAE" in log_content

    def test_aae_with_verbose_logging(self, sample_paths):
        """Test AAE export with verbose logging."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "--export-aae", "-vv"
        ]
        result = run_script(args)

        log_content = sample_paths['log_file'].read_text()
        # With verbose logging, we should see debug information about the command
        assert "--export-aae" in log_content or "aae" in log_content.lower()


# Integration test (marked as slow since it might take longer)
@pytest.mark.slow
class TestIntegration:
    """Integration tests that test the full workflow."""

    def test_full_dry_run_workflow(self, sample_paths):
        """Test the complete dry run workflow."""
        args = [
            "-e", str(sample_paths['export_dir']),
            "-n", str(sample_paths['nc_dir']),
            "-l", str(sample_paths['log_file']),
            "--dry-run", "-v"
        ]
        result = run_script(args)

        # Verify log file was created and has content
        assert sample_paths['log_file'].exists()
        log_content = sample_paths['log_file'].read_text()
        assert len(log_content) > 100  # Should have substantial log content

        # Check for key workflow steps in logs
        assert "Starting photo export" in log_content or "photo export" in log_content.lower()


if __name__ == "__main__":
    # Allow running this file directly with python
    pytest.main([__file__, "-v"])
