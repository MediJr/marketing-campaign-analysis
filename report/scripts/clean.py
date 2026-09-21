# =====================================================
# SCRIPT: scripts/clean.py
# =====================================================

#!/usr/bin/env python3
"""
LaTeX Project Cleaner
Remove temporary and build files
"""

import os
import sys
import argparse
from pathlib import Path
import shutil

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.ENDC, prefix=""):
    """Print colored message with optional prefix"""
    if prefix:
        print(f"{color}{prefix} {message}{Colors.ENDC}")
    else:
        print(f"{color}{message}{Colors.ENDC}")

def print_header():
    """Print cleaning header"""
    header = """
========================================
      LATEX PROJECT CLEANER
========================================
"""
    print_colored(header, Colors.HEADER)

def get_latex_temp_extensions():
    """Get list of LaTeX temporary file extensions"""
    return [
        '*.aux', '*.bbl', '*.bcf', '*.blg', '*.fdb_latexmk', '*.fls',
        '*.log', '*.out', '*.run.xml', '*.synctex.gz', '*.toc',
        '*.lof', '*.lot', '*.acn', '*.acr', '*.alg', '*.glg',
        '*.glo', '*.gls', '*.idx', '*.ilg', '*.ind', '*.ist',
        '*.lol', '*.nav', '*.snm', '*.vrb', '*.xdy', '*.tdo',
        '*.figlist', '*.makefile', '*.figlist', '*.figlist'
    ]

def find_files_to_clean(base_path, patterns, recursive=True):
    """Find files matching patterns to clean"""
    files_to_clean = []
    
    for pattern in patterns:
        if recursive:
            files_found = list(base_path.rglob(pattern))
        else:
            files_found = list(base_path.glob(pattern))
        files_to_clean.extend(files_found)
    
    return files_to_clean

def clean_build_directory(build_dir, keep_pdf=True):
    """Clean build directory"""
    if not build_dir.exists():
        print_colored("Build directory doesn't exist", Colors.WARNING, "[INFO]")
        return 0
    
    files_removed = 0
    
    # Get all files in build directory
    for file_path in build_dir.iterdir():
        if file_path.is_file():
            # Keep PDF files if requested
            if keep_pdf and file_path.suffix.lower() == '.pdf':
                continue
            
            try:
                file_path.unlink()
                files_removed += 1
            except PermissionError:
                print_colored(f"Permission denied: {file_path}", Colors.WARNING, "[WARNING]")
            except Exception as e:
                print_colored(f"Error removing {file_path}: {e}", Colors.WARNING, "[WARNING]")
    
    return files_removed

def clean_temp_files(base_path, extensions, recursive=True):
    """Clean temporary files by extension"""
    files_to_clean = find_files_to_clean(base_path, extensions, recursive)
    files_removed = 0
    
    for file_path in files_to_clean:
        try:
            file_path.unlink()
            files_removed += 1
            print_colored(f"Removed: {file_path}", Colors.OKCYAN, "[CLEAN]")
        except PermissionError:
            print_colored(f"Permission denied: {file_path}", Colors.WARNING, "[WARNING]")
        except Exception as e:
            print_colored(f"Error removing {file_path}: {e}", Colors.WARNING, "[WARNING]")
    
    return files_removed

def clean_cache_directories(base_path):
    """Clean cache directories"""
    cache_dirs = ['__pycache__', '.pytest_cache', 'node_modules']
    dirs_removed = 0
    
    for cache_dir_name in cache_dirs:
        for cache_dir in base_path.rglob(cache_dir_name):
            if cache_dir.is_dir():
                try:
                    shutil.rmtree(cache_dir)
                    dirs_removed += 1
                    print_colored(f"Removed directory: {cache_dir}", Colors.OKCYAN, "[CLEAN]")
                except PermissionError:
                    print_colored(f"Permission denied: {cache_dir}", Colors.WARNING, "[WARNING]")
                except Exception as e:
                    print_colored(f"Error removing {cache_dir}: {e}", Colors.WARNING, "[WARNING]")
    
    return dirs_removed

def get_directory_size(path):
    """Get total size of directory"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
    return total_size

def format_size(size_bytes):
    """Format size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def clean_project(clean_build=True, clean_temp=True, clean_cache=False, 
                 keep_pdf=True, recursive=True, dry_run=False):
    """Main cleaning function"""
    
    if not dry_run:
        print_header()
    
    base_path = Path('.')
    total_files_removed = 0
    total_dirs_removed = 0
    space_freed = 0
    
    # Calculate initial sizes for space calculation
    initial_sizes = {}
    if clean_build and Path('build').exists():
        initial_sizes['build'] = get_directory_size('build')
    
    print_colored("Scanning for files to clean...", Colors.OKCYAN, "[INFO]")
    
    if clean_temp:
        # Find temporary files
        temp_extensions = get_latex_temp_extensions()
        temp_files = find_files_to_clean(base_path, temp_extensions, recursive)
        
        if temp_files:
            print_colored(f"Found {len(temp_files)} temporary files", Colors.OKCYAN, "[INFO]")
            
            if dry_run:
                print_colored("Temporary files that would be removed:", Colors.WARNING, "[DRY-RUN]")
                for file_path in temp_files[:10]:  # Show first 10
                    print_colored(f"  {file_path}", Colors.WARNING)
                if len(temp_files) > 10:
                    print_colored(f"  ... and {len(temp_files) - 10} more files", Colors.WARNING)
            else:
                # Calculate size before removal
                temp_size = sum(file_path.stat().st_size for file_path in temp_files if file_path.exists())
                space_freed += temp_size
                
                # Clean temporary files
                files_removed = clean_temp_files(base_path, temp_extensions, recursive)
                total_files_removed += files_removed
                print_colored(f"Removed {files_removed} temporary files", Colors.OKGREEN, "[SUCCESS]")
    
    if clean_build:
        build_dir = Path('build')
        if build_dir.exists():
            if dry_run:
                build_files = [f for f in build_dir.iterdir() if f.is_file()]
                if keep_pdf:
                    build_files = [f for f in build_files if f.suffix.lower() != '.pdf']
                
                print_colored(f"Build files that would be removed: {len(build_files)}", Colors.WARNING, "[DRY-RUN]")
                for file_path in build_files[:5]:  # Show first 5
                    print_colored(f"  {file_path}", Colors.WARNING)
                if len(build_files) > 5:
                    print_colored(f"  ... and {len(build_files) - 5} more files", Colors.WARNING)
            else:
                # Clean build directory
                files_removed = clean_build_directory(build_dir, keep_pdf)
                total_files_removed += files_removed
                
                if 'build' in initial_sizes:
                    final_size = get_directory_size('build')
                    space_freed += initial_sizes['build'] - final_size
                
                print_colored(f"Cleaned build directory: {files_removed} files removed", Colors.OKGREEN, "[SUCCESS]")
    
    if clean_cache:
        if dry_run:
            cache_dirs = []
            for cache_dir_name in ['__pycache__', '.pytest_cache', 'node_modules']:
                cache_dirs.extend(base_path.rglob(cache_dir_name))
            
            if cache_dirs:
                print_colored(f"Cache directories that would be removed: {len(cache_dirs)}", Colors.WARNING, "[DRY-RUN]")
                for cache_dir in cache_dirs:
                    print_colored(f"  {cache_dir}", Colors.WARNING)
        else:
            # Clean cache directories
            dirs_removed = clean_cache_directories(base_path)
            total_dirs_removed += dirs_removed
            
            if dirs_removed > 0:
                print_colored(f"Removed {dirs_removed} cache directories", Colors.OKGREEN, "[SUCCESS]")
    
    # Summary
    print()
    if dry_run:
        print_colored("DRY RUN COMPLETE - No files were actually removed", Colors.WARNING, "[DRY-RUN]")
    else:
        print_colored("CLEANING COMPLETE", Colors.OKGREEN, "[SUCCESS]")
        print_colored(f"Files removed: {total_files_removed}", Colors.OKGREEN, "[SUMMARY]")
        if total_dirs_removed > 0:
            print_colored(f"Directories removed: {total_dirs_removed}", Colors.OKGREEN, "[SUMMARY]")
        if space_freed > 0:
            print_colored(f"Disk space freed: {format_size(space_freed)}", Colors.OKGREEN, "[SUMMARY]")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Clean LaTeX project files and directories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Clean temp files and build directory
  %(prog)s --all               # Clean everything including cache
  %(prog)s --dry-run           # Show what would be cleaned
  %(prog)s --keep-pdf          # Keep PDF files in build directory
  %(prog)s --temp-only         # Clean only temporary files
        """
    )
    
    parser.add_argument('--all', action='store_true',
                       help='Clean everything (temp, build, cache)')
    parser.add_argument('--temp-only', action='store_true',
                       help='Clean only temporary LaTeX files')
    parser.add_argument('--build-only', action='store_true',
                       help='Clean only build directory')
    parser.add_argument('--cache', action='store_true',
                       help='Include cache directories (__pycache__, etc.)')
    parser.add_argument('--keep-pdf', action='store_true', default=True,
                       help='Keep PDF files in build directory (default)')
    parser.add_argument('--remove-pdf', action='store_true',
                       help='Remove PDF files from build directory')
    parser.add_argument('--recursive', action='store_true', default=True,
                       help='Clean files recursively in subdirectories (default)')
    parser.add_argument('--current-only', action='store_true',
                       help='Clean only current directory (not recursive)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be cleaned without removing files')
    
    args = parser.parse_args()
    
    # Determine what to clean
    if args.all:
        clean_build = True
        clean_temp = True
        clean_cache = True
    elif args.temp_only:
        clean_build = False
        clean_temp = True
        clean_cache = False
    elif args.build_only:
        clean_build = True
        clean_temp = False
        clean_cache = False
    else:
        # Default: clean temp and build
        clean_build = True
        clean_temp = True
        clean_cache = args.cache
    
    # PDF handling
    keep_pdf = not args.remove_pdf
    
    # Recursive handling
    recursive = not args.current_only
    
    try:
        clean_project(
            clean_build=clean_build,
            clean_temp=clean_temp,
            clean_cache=clean_cache,
            keep_pdf=keep_pdf,
            recursive=recursive,
            dry_run=args.dry_run
        )
        
    except KeyboardInterrupt:
        print_colored("\nCleaning interrupted by user", Colors.WARNING, "[INTERRUPTED]")
        sys.exit(1)
    except Exception as e:
        print_colored(f"Unexpected error: {e}", Colors.FAIL, "[ERROR]")
        sys.exit(1)

if __name__ == "__main__":
    main()
