#!/usr/bin/env python3
"""
🚀 Release Management Script for LaTeX Report Template
======================================================

This script helps create and manage releases for the LaTeX Report Template.
It provides utilities for version management, tag creation, and release validation.

Usage:
    python scripts/release.py create 2.1.0
    python scripts/release.py check
    python scripts/release.py list
    python scripts/release.py validate

Author: SIKATI KENMOGNE Samuel
License: MIT
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ReleaseManager:
    """Manages release creation and validation for the LaTeX template."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.required_files = [
            "main.tex",
            "metadata.tex", 
            "titlepage.tex",
            "internshipreport.cls"
        ]
        self.required_dirs = [
            "config",
            "content", 
            "templates"
        ]
    
    def run_command(self, cmd: List[str], capture=True) -> Tuple[int, str]:
        """Run a shell command and return exit code and output."""
        try:
            if capture:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    cwd=self.project_root
                )
                return result.returncode, result.stdout + result.stderr
            else:
                result = subprocess.run(cmd, cwd=self.project_root)
                return result.returncode, ""
        except Exception as e:
            return 1, str(e)
    
    def print_status(self, message: str, status: str = "info"):
        """Print colored status message."""
        color_map = {
            "success": Colors.GREEN,
            "error": Colors.RED,
            "warning": Colors.YELLOW,
            "info": Colors.BLUE
        }
        color = color_map.get(status, Colors.WHITE)
        icon_map = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }
        icon = icon_map.get(status, "•")
        print(f"{color}{icon} {message}{Colors.END}")
    
    def validate_version(self, version: str) -> bool:
        """Validate semantic version format."""
        pattern = r'^[0-9]+\.[0-9]+\.[0-9]+$'
        return bool(re.match(pattern, version))
    
    def get_current_branch(self) -> str:
        """Get current git branch."""
        code, output = self.run_command(["git", "branch", "--show-current"])
        return output.strip() if code == 0 else "unknown"
    
    def is_working_directory_clean(self) -> bool:
        """Check if git working directory is clean."""
        code, output = self.run_command(["git", "status", "--porcelain"])
        return code == 0 and not output.strip()
    
    def tag_exists(self, tag: str) -> bool:
        """Check if git tag exists."""
        code, _ = self.run_command(["git", "rev-parse", tag])
        return code == 0
    
    def get_latest_tag(self) -> Optional[str]:
        """Get the latest git tag."""
        code, output = self.run_command([
            "git", "describe", "--tags", "--abbrev=0"
        ])
        return output.strip() if code == 0 else None
    
    def list_tags(self) -> List[str]:
        """List all version tags."""
        code, output = self.run_command([
            "git", "tag", "-l", "v*.*.*", "--sort=-version:refname"
        ])
        if code == 0:
            return [tag.strip() for tag in output.strip().split('\n') if tag.strip()]
        return []
    
    def validate_project_structure(self) -> bool:
        """Validate that all required files and directories exist."""
        self.print_status("Validating project structure...", "info")
        
        all_valid = True
        
        # Check required files
        for file in self.required_files:
            file_path = self.project_root / file
            if file_path.exists():
                self.print_status(f"Found: {file}", "success")
            else:
                self.print_status(f"Missing: {file}", "error")
                all_valid = False
        
        # Check required directories
        for directory in self.required_dirs:
            dir_path = self.project_root / directory
            if dir_path.exists() and dir_path.is_dir():
                self.print_status(f"Found: {directory}/", "success")
            else:
                self.print_status(f"Missing: {directory}/", "error")
                all_valid = False
        
        return all_valid
    
    def test_latex_compilation(self) -> bool:
        """Test LaTeX compilation locally."""
        self.print_status("Testing LaTeX compilation...", "info")
        
        # Create build directory
        build_dir = self.project_root / "build"
        build_dir.mkdir(exist_ok=True)
        
        # Try compilation
        commands = [
            ["pdflatex", "-interaction=nonstopmode", "-output-directory=build", "main.tex"],
            ["biber", "build/main"],
            ["pdflatex", "-interaction=nonstopmode", "-output-directory=build", "main.tex"]
        ]
        
        for i, cmd in enumerate(commands, 1):
            self.print_status(f"Running pass {i}: {' '.join(cmd)}", "info")
            code, output = self.run_command(cmd)
            
            if code != 0 and i != 2:  # Biber might fail if no bibliography
                if "biber" in cmd[0] and "Cannot find control file" in output:
                    self.print_status("No bibliography found, skipping biber", "warning")
                    continue
                self.print_status(f"Compilation failed at step {i}", "error")
                print(output[-500:])  # Show last 500 chars of output
                return False
        
        # Check if PDF was generated
        pdf_path = build_dir / "main.pdf"
        if pdf_path.exists():
            size = pdf_path.stat().st_size
            self.print_status(f"PDF generated successfully ({size:,} bytes)", "success")
            return True
        else:
            self.print_status("PDF generation failed", "error")
            return False
    
    def create_release(self, version: str, dry_run: bool = False) -> bool:
        """Create a new release."""
        if not self.validate_version(version):
            self.print_status(f"Invalid version format: {version}", "error")
            return False
        
        tag = f"v{version}"
        
        # Pre-flight checks
        self.print_status(f"Creating release {tag}...", "info")
        
        # Check current branch
        branch = self.get_current_branch()
        if branch != "main":
            self.print_status(f"Not on main branch (current: {branch})", "warning")
            if not dry_run:
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    return False
        
        # Check working directory
        if not self.is_working_directory_clean():
            self.print_status("Working directory is not clean", "error")
            self.print_status("Please commit or stash changes first", "error")
            return False
        
        # Check if tag already exists
        if self.tag_exists(tag):
            self.print_status(f"Tag {tag} already exists", "error")
            return False
        
        # Validate project structure
        if not self.validate_project_structure():
            self.print_status("Project structure validation failed", "error")
            return False
        
        # Test compilation
        if not self.test_latex_compilation():
            self.print_status("LaTeX compilation test failed", "error")
            return False
        
        if dry_run:
            self.print_status("Dry run completed successfully", "success")
            self.print_status("Would create tag and push to trigger release", "info")
            return True
        
        # Pull latest changes
        self.print_status("Pulling latest changes...", "info")
        code, output = self.run_command(["git", "pull", "origin", "main"])
        if code != 0:
            self.print_status(f"Failed to pull latest changes: {output}", "error")
            return False
        
        # Create and push tag
        self.print_status(f"Creating tag {tag}...", "info")
        code, output = self.run_command([
            "git", "tag", "-a", tag, "-m", f"Release version {version}"
        ])
        if code != 0:
            self.print_status(f"Failed to create tag: {output}", "error")
            return False
        
        self.print_status(f"Pushing tag {tag}...", "info")
        code, output = self.run_command(["git", "push", "origin", tag])
        if code != 0:
            self.print_status(f"Failed to push tag: {output}", "error")
            # Clean up local tag
            self.run_command(["git", "tag", "-d", tag])
            return False
        
        self.print_status(f"Release {tag} created successfully!", "success")
        self.print_status("GitHub Actions will now build and publish the release", "info")
        
        # Get repository info for URL
        code, remote_output = self.run_command(["git", "remote", "get-url", "origin"])
        if code == 0:
            repo_url = remote_output.strip()
            if "github.com" in repo_url:
                # Convert SSH/HTTPS URL to web URL
                repo_path = repo_url.split("github.com")[-1].replace(":", "/").replace(".git", "")
                if repo_path.startswith("/"):
                    repo_path = repo_path[1:]
                actions_url = f"https://github.com/{repo_path}/actions"
                self.print_status(f"Monitor progress: {actions_url}", "info")
        
        return True
    
    def list_releases(self):
        """List all releases."""
        tags = self.list_tags()
        
        if not tags:
            self.print_status("No releases found", "warning")
            return
        
        self.print_status(f"Found {len(tags)} releases:", "info")
        
        for i, tag in enumerate(tags):
            # Get tag date
            code, date_output = self.run_command([
                "git", "log", "-1", "--format=%ai", tag
            ])
            date_str = date_output.strip()[:10] if code == 0 else "unknown"
            
            # Get commit message
            code, msg_output = self.run_command([
                "git", "tag", "-l", "--format=%(contents:subject)", tag
            ])
            message = msg_output.strip() or "No message"
            
            latest = " (latest)" if i == 0 else ""
            print(f"  {Colors.CYAN}{tag}{Colors.END}{latest}")
            print(f"    📅 {date_str}")
            print(f"    📝 {message}")
            print()
    
    def check_environment(self):
        """Check development environment."""
        self.print_status("Checking development environment...", "info")
        
        # Check Git
        code, git_version = self.run_command(["git", "--version"])
        if code == 0:
            self.print_status(f"Git: {git_version.strip()}", "success")
        else:
            self.print_status("Git: Not found", "error")
        
        # Check LaTeX
        code, latex_version = self.run_command(["pdflatex", "--version"])
        if code == 0:
            version_line = latex_version.split('\n')[0]
            self.print_status(f"pdfLaTeX: {version_line}", "success")
        else:
            self.print_status("pdfLaTeX: Not found", "error")
        
        # Check Biber
        code, biber_version = self.run_command(["biber", "--version"])
        if code == 0:
            version_line = biber_version.split('\n')[0]
            self.print_status(f"Biber: {version_line}", "success")
        else:
            self.print_status("Biber: Not found", "warning")
        
        # Check Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.print_status(f"Python: {python_version}", "success")
        
        # Check project structure
        self.validate_project_structure()
        
        # Get repository status
        self.print_status("\nRepository Status:", "info")
        branch = self.get_current_branch()
        print(f"  Branch: {branch}")
        
        clean = self.is_working_directory_clean()
        status = "clean" if clean else "modified"
        print(f"  Working directory: {status}")
        
        latest_tag = self.get_latest_tag()
        if latest_tag:
            print(f"  Latest tag: {latest_tag}")
        else:
            print("  Latest tag: none")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Release management for LaTeX Report Template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/release.py check
  python scripts/release.py create 2.1.0
  python scripts/release.py create 2.1.0 --dry-run
  python scripts/release.py list
  python scripts/release.py validate
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new release")
    create_parser.add_argument("version", help="Version number (e.g., 2.1.0)")
    create_parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Test release creation without actually creating it"
    )
    
    # List command
    subparsers.add_parser("list", help="List all releases")
    
    # Check command
    subparsers.add_parser("check", help="Check development environment")
    
    # Validate command
    subparsers.add_parser("validate", help="Validate project structure")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = ReleaseManager()
    
    try:
        if args.command == "create":
            success = manager.create_release(args.version, args.dry_run)
            sys.exit(0 if success else 1)
        
        elif args.command == "list":
            manager.list_releases()
        
        elif args.command == "check":
            manager.check_environment()
        
        elif args.command == "validate":
            success = manager.validate_project_structure()
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Operation cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()