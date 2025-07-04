#!/Users/andrew/venvs/scripts/bin/python3
"""
OSXPhotos to Nextcloud Export Tool

A modern Python replacement for the bash script that exports photos from
Apple Photos.app and syncs them to Nextcloud with beautiful progress bars
and robust logging.
"""

import os
import sys
import signal
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from contextlib import contextmanager

import click
from loguru import logger
from rich.console import Console
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn,
    TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn
)
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text
from rich import print as rprint

# Global flag for osxphotos availability - will be set when needed
_OSXPHOTOS_AVAILABLE = None

console = Console()

# Import version for Click
try:
    from . import __version__
except ImportError:
    __version__ = "1.0.0"


def _check_osxphotos_availability():
    """Check if osxphotos is available as a Python import."""
    global _OSXPHOTOS_AVAILABLE

    if _OSXPHOTOS_AVAILABLE is not None:
        return _OSXPHOTOS_AVAILABLE

    # Try to import osxphotos from the system installation
    sys.path.insert(0, "/opt/homebrew/Cellar/osxphotos/0.72.1/libexec/lib/python3.13/site-packages")

    try:
        import osxphotos
        _OSXPHOTOS_AVAILABLE = True
        return True
    except ImportError:
        _OSXPHOTOS_AVAILABLE = False
        return False


@dataclass
class Config:
    """Configuration for the photo export process."""
    export_dir: Path
    nc_photos_dir: Path
    log_file: Path
    dry_run: bool = False
    use_symlink: bool = True
    cleanup: bool = False
    export_aae: bool = False
    quiet: bool = False
    verbose: int = 0

    def __post_init__(self):
        """Convert string paths to Path objects."""
        self.export_dir = Path(self.export_dir).expanduser().resolve()
        self.nc_photos_dir = Path(self.nc_photos_dir).expanduser().resolve()
        self.log_file = Path(self.log_file).expanduser().resolve()


class PhotoExporter:
    """Main class for handling photo export operations."""

    def __init__(self, config: Config):
        self.config = config
        self.setup_logging()
        self.export_process: Optional[subprocess.Popen] = None

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def setup_logging(self):
        """Configure loguru logging with appropriate levels and formats."""
        # Remove default logger
        logger.remove()

        # Determine log level based on verbosity
        if self.config.quiet:
            console_level = "WARNING"
            file_level = "INFO"
        elif self.config.verbose == 0:
            console_level = "INFO"
            file_level = "DEBUG"
        elif self.config.verbose == 1:
            console_level = "DEBUG"
            file_level = "TRACE"
        else:  # verbose >= 2
            console_level = "TRACE"
            file_level = "TRACE"

        # Console logging with colors and emojis
        logger.add(
            sys.stderr,
            level=console_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            colorize=True,
        )

        # File logging with detailed format
        logger.add(
            self.config.log_file,
            level=file_level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="7 days",
            compression="gz",
        )

        logger.info("📝 Logging configured")

    def _signal_handler(self, signum: int, frame):
        """Handle interrupt signals gracefully."""
        logger.warning(f"🛑 Received signal {signum}, cleaning up...")
        if self.export_process and self.export_process.poll() is None:
            logger.info("🔪 Terminating export process...")
            self.export_process.terminate()
            try:
                self.export_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("⚡ Force killing export process...")
                self.export_process.kill()

        logger.info("🧹 Cleanup complete")
        sys.exit(130)

    def validate_dependencies(self):
        """Check that required tools are available."""
        logger.debug("🔍 Checking dependencies...")

        # Check osxphotos Python import availability
        if not _check_osxphotos_availability():
            logger.warning("osxphotos not available as Python import, will use CLI")

        # Check osxphotos CLI
        if not shutil.which("osxphotos"):
            logger.error("❌ osxphotos not found. Install with: brew tap rhetbull/osxphotos && brew install osxphotos")
            raise click.ClickException("osxphotos not found")

        # Test osxphotos
        try:
            result = subprocess.run(["osxphotos", "version"],
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip().split()[-1] if result.stdout else "unknown"
            logger.info(f"✅ osxphotos version {version}")
        except subprocess.CalledProcessError:
            logger.error("❌ osxphotos installation appears broken")
            raise click.ClickException("osxphotos installation broken")

        # Check tree (optional)
        if not shutil.which("tree"):
            logger.warning("⚠️ tree not found, install with: brew install tree")
        else:
            logger.debug("✅ tree available")

    def setup_directories(self):
        """Create necessary directories."""
        logger.debug("📁 Setting up directories...")

        if self.config.dry_run:
            logger.info(f"🏃‍♂️ [DRY RUN] Would create: {self.config.export_dir}")
            logger.info(f"🏃‍♂️ [DRY RUN] Would create: {self.config.nc_photos_dir}")
            return

        try:
            self.config.export_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📂 Created/verified export directory: {self.config.export_dir}")

            self.config.nc_photos_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📂 Created/verified Nextcloud directory: {self.config.nc_photos_dir}")

        except PermissionError as e:
            logger.error(f"❌ Permission denied creating directories: {e}")
            raise click.ClickException(f"Cannot create directories: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to create directories: {e}")
            raise click.ClickException(f"Directory creation failed: {e}")

    def build_export_command(self) -> List[str]:
        """Build the osxphotos export command."""
        cmd = [
            "osxphotos", "export", str(self.config.export_dir),
            "--skip-original-if-edited",
            "--directory", "{created.year}/{created.month:02d}",
            "--update", "--verbose", "--download-missing", "--use-photokit",
            "--exiftool", "--retry", "3",
            "--filename", "IMG_{edited_version?E,}{id:04d}",
            "--edited-suffix", "",
            "--strip", "--ramdb",
            "--exiftool-option", "-m",
            "--exiftool-option", "-fast10"
        ]

        # Add quiet flag for exiftool if not verbose
        if self.config.verbose == 0:
            cmd.extend(["--exiftool-option", "-q"])

        # Add cleanup options
        if self.config.cleanup:
            cmd.extend([
                "--fix-orientation",
                "--exiftool-merge-keywords",
                "--exiftool-merge-persons",
                "--cleanup"
            ])

        # Add AAE export option
        if self.config.export_aae:
            cmd.append("--export-aae")
            logger.debug("🎨 AAE adjustments files will be exported")

        # Add dry-run flag
        if self.config.dry_run:
            cmd.append("--dry-run")

        logger.debug(f"🚀 Export command: {' '.join(cmd)}")
        return cmd

    @contextmanager
    def export_progress(self):
        """Create a progress bar context for the export process."""
        if self.config.quiet:
            yield None
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Exporting photos..."),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=False
        ) as progress:
            task = progress.add_task("export", total=None)
            yield progress, task

    def run_export(self):
        """Execute the photo export process."""
        logger.info("📸 Starting photo export...")

        cmd = self.build_export_command()

        if not self.config.quiet:
            rprint(Panel.fit(
                f"[bold cyan]Export Command[/bold cyan]\n[dim]{' '.join(cmd)}[/dim]",
                border_style="blue"
            ))

        try:
            with self.export_progress() as progress_info:
                if progress_info:
                    progress, task = progress_info

                # Start the export process
                self.export_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                # Monitor the process output
                if self.export_process.stdout:
                    for line in iter(self.export_process.stdout.readline, ''):
                        line = line.strip()
                        if line:
                            logger.debug(f"osxphotos: {line}")

                            # Update progress if we have it
                            if progress_info and "Processing" in line:
                                if progress_info:
                                    progress, task = progress_info
                                    progress.update(task, advance=1)

                # Wait for completion
                return_code = self.export_process.wait()

                if return_code == 0:
                    logger.success("✅ Export completed successfully")
                    return True
                else:
                    logger.error(f"❌ Export failed with return code {return_code}")
                    return False

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Export process failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during export: {e}")
            return False
        finally:
            self.export_process = None

    def validate_export(self) -> Dict[str, Any]:
        """Validate the export results and return statistics."""
        if self.config.dry_run:
            logger.info("🏃‍♂️ [DRY RUN] Skipping export validation")
            return {"dry_run": True}

        logger.debug("🔍 Validating export results...")

        stats = {
            "year_dirs": 0,
            "total_files": 0,
            "total_size": 0
        }

        try:
            # Count year directories
            year_dirs = [d for d in self.config.export_dir.iterdir()
                        if d.is_dir() and d.name.isdigit() and len(d.name) == 4]
            stats["year_dirs"] = len(year_dirs)

            if stats["year_dirs"] == 0:
                logger.warning(f"⚠️ No year directories found in {self.config.export_dir}")
            else:
                logger.info(f"📅 Found {stats['year_dirs']} year directories")

            # Count total files and calculate size
            for file_path in self.config.export_dir.rglob("*"):
                if file_path.is_file():
                    stats["total_files"] += 1
                    stats["total_size"] += file_path.stat().st_size

            if stats["total_files"] == 0:
                logger.warning("⚠️ No files found in export (incremental export?)")
            else:
                size_mb = stats["total_size"] / (1024 * 1024)
                logger.info(f"📊 Total: {stats['total_files']} files ({size_mb:.1f} MB)")

        except Exception as e:
            logger.error(f"❌ Error validating export: {e}")

        return stats

    def manage_symlinks(self) -> Dict[str, int]:
        """Create symlinks from export directories to Nextcloud."""
        if self.config.dry_run or not self.config.use_symlink:
            logger.info("🔗 Symlink step skipped")
            return {"created": 0, "errors": 0}

        logger.info("🔗 Creating symlinks to Nextcloud...")

        stats = {"created": 0, "errors": 0}

        # Find year directories to link
        year_dirs = [d for d in self.config.export_dir.iterdir()
                    if d.is_dir() and d.name.isdigit() and len(d.name) == 4]

        if not year_dirs:
            logger.warning("⚠️ No year directories to link")
            return stats

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]Creating symlinks..."),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=not self.config.verbose
        ) as progress:

            task = progress.add_task("symlinks", total=len(year_dirs))

            for year_dir in year_dirs:
                try:
                    target_link = self.config.nc_photos_dir / year_dir.name

                    # Remove existing symlink if it exists
                    if target_link.is_symlink():
                        target_link.unlink()
                    elif target_link.exists():
                        logger.warning(f"⚠️ Target exists and is not a symlink: {target_link}")
                        stats["errors"] += 1
                        continue

                    # Create the symlink
                    target_link.symlink_to(year_dir)
                    stats["created"] += 1
                    logger.debug(f"🔗 Linked: {year_dir.name} -> {target_link}")

                except Exception as e:
                    logger.error(f"❌ Failed to link {year_dir.name}: {e}")
                    stats["errors"] += 1

                progress.update(task, advance=1)

        if stats["errors"] > 0:
            logger.warning(f"⚠️ Symlinks completed with {stats['errors']} errors")
        else:
            logger.success(f"✅ Created {stats['created']} symlinks successfully")

        return stats

    def generate_report(self):
        """Generate a final report of the export process."""
        logger.info("📋 Generating final report...")

        if not self.config.quiet:
            console.print("\n")
            console.rule("[bold cyan]📊 Export Summary", style="cyan")

        # Show directory tree if tree is available
        if shutil.which("tree") and self.config.nc_photos_dir.exists():
            try:
                result = subprocess.run(
                    ["tree", "-d", "-L", "2", str(self.config.nc_photos_dir)],
                    capture_output=True, text=True, check=True
                )
                if not self.config.quiet:
                    console.print(f"\n[bold]Directory Structure:[/bold]\n{result.stdout}")
            except subprocess.CalledProcessError:
                logger.warning("⚠️ tree command failed, falling back to ls")
                try:
                    result = subprocess.run(
                        ["ls", "-la", str(self.config.nc_photos_dir)],
                        capture_output=True, text=True, check=True
                    )
                    if not self.config.quiet:
                        console.print(f"\n[bold]Directory Contents:[/bold]\n{result.stdout}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"❌ Failed to list directory: {e}")

        logger.info(f"📄 Full log available at: {self.config.log_file}")

        if not self.config.quiet:
            console.print(f"\n[dim]Log file: {self.config.log_file}[/dim]")

    def run(self) -> bool:
        """Execute the complete export process."""
        try:
            if not self.config.quiet:
                rprint(Panel.fit(
                    "[bold cyan]🚀 OSXPhotos to Nextcloud Export[/bold cyan]\n"
                    f"Export: [yellow]{self.config.export_dir}[/yellow]\n"
                    f"Nextcloud: [yellow]{self.config.nc_photos_dir}[/yellow]\n"
                    f"Dry Run: [{'green' if self.config.dry_run else 'red'}]{self.config.dry_run}[/]",
                    border_style="cyan"
                ))

            logger.info("🏁 Starting photo export and sync process...")

            # Validation and setup
            self.validate_dependencies()
            self.setup_directories()

            # Main export process
            export_success = self.run_export()
            if not export_success:
                logger.error("❌ Export failed, aborting")
                return False

            # Post-export tasks
            export_stats = self.validate_export()
            symlink_stats = self.manage_symlinks()

            # Final report
            self.generate_report()

            if not self.config.quiet:
                console.print("\n")
                rprint("[bold green]✅ Photo export and sync completed successfully![/bold green]")

            logger.success("🎉 All operations completed successfully")
            return True

        except KeyboardInterrupt:
            logger.warning("🛑 Process interrupted by user")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False


@click.command()
@click.option('-e', '--export-dir', required=True, type=click.Path(),
              help='Export destination directory')
@click.option('-n', '--nc-photos-dir', required=True, type=click.Path(),
              help='Nextcloud sync directory')
@click.option('-l', '--log-file', required=True, type=click.Path(),
              help='Path to log file')
@click.option('--dry-run', is_flag=True,
              help='Show what would happen, but don\'t write or link')
@click.option('--no-symlink', is_flag=True,
              help='Do not create symlinks into Nextcloud')
@click.option('--use-symlink', is_flag=True, default=True,
              help='Create symlinks into Nextcloud (default)')
@click.option('-c', '--cleanup', is_flag=True,
              help='Do automated cleanup tasks (orientation, keywords, etc.)')
@click.option('--export-aae', is_flag=True,
              help='Export AAE adjustments files detailing edits made to originals')
@click.option('-v', '--verbose', count=True,
              help='Increase verbosity (-v, -vv, -vvv)')
@click.option('-q', '--quiet', is_flag=True,
              help='Suppress non-essential output')
@click.version_option(version=__version__, package_name="export-photos-to-nextcloud")
def main(export_dir: str, nc_photos_dir: str, log_file: str,
         dry_run: bool, no_symlink: bool, use_symlink: bool,
         cleanup: bool, export_aae: bool, verbose: int, quiet: bool):
    """
    OSXPhotos to Nextcloud Export Tool

    A modern Python tool for exporting photos from Apple Photos.app
    and syncing them to Nextcloud with beautiful progress tracking.

    Example:
        python export_photos_to_nextcloud.py \\
            --export-dir ~/PhotosExport \\
            --nc-photos-dir ~/Nextcloud/Photos \\
            --log-file ~/sync.log \\
            --dry-run -v
    """

    # Handle symlink logic
    if no_symlink:
        use_symlink = False

    # Create configuration
    config = Config(
        export_dir=Path(export_dir),
        nc_photos_dir=Path(nc_photos_dir),
        log_file=Path(log_file),
        dry_run=dry_run,
        use_symlink=use_symlink,
        cleanup=cleanup,
        export_aae=export_aae,
        verbose=verbose,
        quiet=quiet
    )

    # Create and run exporter
    exporter = PhotoExporter(config)
    success = exporter.run()

    sys.exit(0 if success else 1)

__all__ = ["main", "Config", "PhotoExporter"]

if __name__ == "__main__":
    main()
