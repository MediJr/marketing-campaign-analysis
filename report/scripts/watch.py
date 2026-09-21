# =====================================================
# SCRIPT: scripts/watch.py
# =====================================================

#!/usr/bin/env python3
"""
LaTeX Document Watcher
Watch for file changes and automatically recompile
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import subprocess

# Try to import watchdog, provide fallback if not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

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
    timestamp = datetime.now().strftime("%H:%M:%S")
    if prefix:
        print(f"{color}[{timestamp}] {prefix} {message}{Colors.ENDC}")
    else:
        print(f"{color}[{timestamp}] {message}{Colors.ENDC}")

def print_header():
    """Print watch header"""
    header = """
========================================
      LATEX DOCUMENT WATCHER
========================================
"""
    print_colored(header, Colors.HEADER)

class LaTeXFileHandler(FileSystemEventHandler):
    """Handle file system events for LaTeX files"""
    
    def __init__(self, main_file, compile_delay=2, quick_mode=False):
        self.main_file = main_file
        self.compile_delay = compile_delay
        self.quick_mode = quick_mode
        self.last_compile = 0
        self.pending_compile = False
        
        # File extensions to watch
        self.watch_extensions = {'.tex', '.cls', '.sty', '.bib'}
        
        # Directories to ignore
        self.ignore_dirs = {'build', '.git', '__pycache__', 'node_modules'}
    
    def should_ignore_event(self, event):
        """Check if event should be ignored"""
        if event.is_directory:
            return True
        
        file_path = Path(event.src_path)
        
        # Ignore files in ignored directories
        for ignore_dir in self.ignore_dirs:
            if ignore_dir in file_path.parts:
                return True
        
        # Only watch specific extensions
        if file_path.suffix.lower() not in self.watch_extensions:
            return True
        
        # Ignore temporary files
        if file_path.name.startswith('.') or file_path.name.startswith('~'):
            return True
        
        return False
    
    def on_modified(self, event):
        """Handle file modification"""
        if self.should_ignore_event(event):
            return
        
        file_path = Path(event.src_path)
        print_colored(f"File changed: {file_path}", Colors.OKCYAN, "[CHANGE]")
        
        # Schedule compilation
        self.schedule_compile()
    
    def on_created(self, event):
        """Handle file creation"""
        if self.should_ignore_event(event):
            return
        
        file_path = Path(event.src_path)
        print_colored(f"File created: {file_path}", Colors.OKGREEN, "[CREATE]")
        
        # Schedule compilation
        self.schedule_compile()
    
    def schedule_compile(self):
        """Schedule a compilation after delay"""
        current_time = time.time()
        
        # Prevent too frequent compilations
        if current_time - self.last_compile < self.compile_delay:
            self.pending_compile = True
            return
        
        self.compile_document()
    
    def compile_document(self):
        """Compile the LaTeX document"""
        self.last_compile = time.time()
        self.pending_compile = False
        
        print_colored("Starting compilation...", Colors.HEADER, "[COMPILE]")
        
        try:
            # Use the compile.py script
            cmd = [sys.executable, 'scripts/compile.py', '-f', self.main_file]
            
            if self.quick_mode:
                cmd.append('--quick')
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print_colored("Compilation successful", Colors.OKGREEN, "[SUCCESS]")
            else:
                print_colored("Compilation failed", Colors.FAIL, "[ERROR]")
                # Show some error output
                if result.stderr:
                    error_lines = result.stderr.split('\n')[:3]
                    for line in error_lines:
                        if line.strip():
                            print_colored(line.strip(), Colors.FAIL, "[ERROR]")
        
        except subprocess.TimeoutExpired:
            print_colored("Compilation timed out", Colors.FAIL, "[ERROR]")
        except Exception as e:
            print_colored(f"Compilation error: {e}", Colors.FAIL, "[ERROR]")
    
    def check_pending_compile(self):
        """Check if there's a pending compilation"""
        if self.pending_compile:
            current_time = time.time()
            if current_time - self.last_compile >= self.compile_delay:
                self.compile_document()

class SimpleFileWatcher:
    """Simple file watcher fallback when watchdog is not available"""
    
    def __init__(self, watch_path, handler):
        self.watch_path = Path(watch_path)
        self.handler = handler
        self.file_mtimes = {}
        self.running = False
    
    def scan_files(self):
        """Scan for LaTeX files and their modification times"""
        current_files = {}
        
        for ext in self.handler.watch_extensions:
            for file_path in self.watch_path.rglob(f'*{ext}'):
                # Skip ignored directories
                skip = False
                for ignore_dir in self.handler.ignore_dirs:
                    if ignore_dir in file_path.parts:
                        skip = True
                        break
                
                if not skip:
                    try:
                        current_files[str(file_path)] = file_path.stat().st_mtime
                    except (OSError, FileNotFoundError):
                        pass
        
        return current_files
    
    def start(self):
        """Start watching for file changes"""
        self.running = True
        self.file_mtimes = self.scan_files()
        
        print_colored(f"Watching {len(self.file_mtimes)} files for changes...", Colors.OKCYAN, "[WATCH]")
        
        try:
            while self.running:
                time.sleep(1)
                
                current_files = self.scan_files()
                
                # Check for new or modified files
                for file_path, mtime in current_files.items():
                    if file_path not in self.file_mtimes:
                        # New file
                        class MockEvent:
                            def __init__(self, path):
                                self.src_path = path
                                self.is_directory = False
                        
                        self.handler.on_created(MockEvent(file_path))
                        self.file_mtimes[file_path] = mtime
                    
                    elif mtime > self.file_mtimes[file_path]:
                        # Modified file
                        class MockEvent:
                            def __init__(self, path):
                                self.src_path = path
                                self.is_directory = False
                        
                        self.handler.on_modified(MockEvent(file_path))
                        self.file_mtimes[file_path] = mtime
                
                # Check for pending compilations
                self.handler.check_pending_compile()
                
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop watching"""
        self.running = False

def watch_files(main_file='main.tex', quick_mode=False, compile_delay=2):
    """Watch LaTeX files for changes and recompile"""
    
    print_header()
    
    # Validate main file
    main_path = Path(main_file)
    if not main_path.exists():
        print_colored(f"Main file not found: {main_file}", Colors.FAIL, "[ERROR]")
        return False
    
    print_colored(f"Watching for changes to: {main_file}", Colors.OKCYAN, "[INFO]")
    print_colored(f"Compile delay: {compile_delay} seconds", Colors.OKCYAN, "[INFO]")
    print_colored(f"Quick mode: {'enabled' if quick_mode else 'disabled'}", Colors.OKCYAN, "[INFO]")
    
    if not WATCHDOG_AVAILABLE:
        print_colored("Watchdog not available, using simple file watcher", Colors.WARNING, "[WARNING]")
        print_colored("Install watchdog for better performance: pip install watchdog", Colors.WARNING, "[TIP]")
    
    # Create file handler
    handler = LaTeXFileHandler(main_file, compile_delay, quick_mode)
    
    # Initial compilation
    print_colored("Performing initial compilation...", Colors.OKCYAN, "[INIT]")
    handler.compile_document()
    
    try:
        if WATCHDOG_AVAILABLE:
            # Use watchdog observer
            observer = Observer()
            observer.schedule(handler, '.', recursive=True)
            observer.start()
            
            print_colored("Press Ctrl+C to stop watching", Colors.OKCYAN, "[INFO]")
            
            try:
                while True:
                    time.sleep(1)
                    handler.check_pending_compile()
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
        else:
            # Use simple file watcher
            watcher = SimpleFileWatcher('.', handler)
            print_colored("Press Ctrl+C to stop watching", Colors.OKCYAN, "[INFO]")
            watcher.start()
        
        print_colored("Watching stopped", Colors.WARNING, "[STOPPED]")
        return True
        
    except Exception as e:
        print_colored(f"Watcher error: {e}", Colors.FAIL, "[ERROR]")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Watch LaTeX files and automatically recompile on changes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Watch main.tex and recompile on changes
  %(prog)s -f custom.tex       # Watch custom file
  %(prog)s --quick             # Use quick compilation mode
  %(prog)s --delay 5           # Wait 5 seconds between compilations
        """
    )
    
    parser.add_argument('-f', '--file', default='main.tex',
                       help='Main LaTeX file to compile (default: main.tex)')
    parser.add_argument('-q', '--quick', action='store_true',
                       help='Use quick compilation mode (single pass)')
    parser.add_argument('-d', '--delay', type=int, default=2,
                       help='Delay between file change and compilation (seconds)')
    
    args = parser.parse_args()
    
    if args.delay < 1:
        print_colored("Delay must be at least 1 second", Colors.FAIL, "[ERROR]")
        sys.exit(1)
    
    try:
        success = watch_files(
            main_file=args.file,
            quick_mode=args.quick,
            compile_delay=args.delay
        )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print_colored("\nWatching stopped by user", Colors.WARNING, "[STOPPED]")
        sys.exit(0)
    except Exception as e:
        print_colored(f"Unexpected error: {e}", Colors.FAIL, "[ERROR]")
        sys.exit(1)

if __name__ == "__main__":
    main()
