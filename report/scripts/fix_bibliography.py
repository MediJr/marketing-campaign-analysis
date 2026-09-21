#!/usr/bin/env python3
"""
Bibliography Debugging and Fixing Script
Diagnoses and fixes bibliography compilation issues
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

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

def check_file_exists(file_path):
    """Check if a file exists and is readable"""
    path = Path(file_path)
    if not path.exists():
        return False, f"File does not exist: {file_path}"
    if not path.is_file():
        return False, f"Path is not a file: {file_path}"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return True, f"File exists and is readable ({len(content)} characters)"
    except Exception as e:
        return False, f"File exists but cannot be read: {e}"

def check_biber_installation():
    """Check if Biber is installed and working"""
    try:
        result = subprocess.run(['biber', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_info = result.stdout.split('\n')[0]
            return True, f"Biber found: {version_info}"
        else:
            return False, f"Biber command failed with return code {result.returncode}"
    except FileNotFoundError:
        return False, "Biber not found in PATH. Please install Biber (part of TeX Live/MiKTeX)"
    except subprocess.TimeoutExpired:
        return False, "Biber command timed out"
    except Exception as e:
        return False, f"Error checking Biber: {e}"

def check_bibliography_file_content(bib_path):
    """Check if bibliography file has valid content"""
    try:
        with open(bib_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            return False, "Bibliography file is empty"
        
        # Count entries
        entry_count = content.count('@')
        if entry_count == 0:
            return False, "No bibliography entries found (no @ symbols)"
        
        # Basic syntax check
        if content.count('{') != content.count('}'):
            return False, "Mismatched braces in bibliography file"
        
        return True, f"Bibliography file contains {entry_count} entries"
    
    except Exception as e:
        return False, f"Error reading bibliography file: {e}"

def create_sample_bibliography():
    """Create a sample bibliography file"""
    bib_content = '''@article{sample2024,
    author = {John Doe},
    title = {Sample Article for Testing Bibliography},
    journal = {Test Journal},
    year = {2024},
    volume = {1},
    number = {1},
    pages = {1-10}
}

@book{samplebook2024,
    author = {Jane Smith},
    title = {Sample Book for Testing},
    publisher = {Test Publisher},
    year = {2024},
    isbn = {978-0000000000}
}
'''
    
    # Ensure directory exists
    bib_dir = Path('content/backmatter')
    bib_dir.mkdir(parents=True, exist_ok=True)
    
    bib_path = bib_dir / 'bibliography.bib'
    
    try:
        with open(bib_path, 'w', encoding='utf-8') as f:
            f.write(bib_content)
        return True, f"Sample bibliography created at {bib_path}"
    except Exception as e:
        return False, f"Failed to create sample bibliography: {e}"

def run_biber_with_debug(main_file_stem, build_dir):
    """Run biber with detailed debugging output"""
    cmd = ['biber', '--debug', str(build_dir / main_file_stem)]
    
    print_colored(f"Running: {' '.join(cmd)}", Colors.OKCYAN, "[DEBUG]")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print_colored(f"Biber return code: {result.returncode}", Colors.OKBLUE, "[DEBUG]")
        
        if result.stdout:
            print_colored("Biber stdout:", Colors.OKBLUE, "[DEBUG]")
            print(result.stdout)
        
        if result.stderr:
            print_colored("Biber stderr:", Colors.WARNING, "[DEBUG]")
            print(result.stderr)
        
        return result.returncode == 0, result
        
    except subprocess.TimeoutExpired:
        print_colored("Biber timed out (2 minutes)", Colors.FAIL, "[ERROR]")
        return False, None
    except Exception as e:
        print_colored(f"Error running Biber: {e}", Colors.FAIL, "[ERROR]")
        return False, None

def check_latex_log_for_biber_errors(build_dir, main_file_stem):
    """Check LaTeX log for bibliography-related errors"""
    log_file = build_dir / f"{main_file_stem}.log"
    
    if not log_file.exists():
        return False, "LaTeX log file not found"
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
        
        # Look for bibliography-related messages
        bib_messages = []
        lines = log_content.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['bibliography', 'biber', 'biblatex', 'citation']):
                bib_messages.append(f"Line {i+1}: {line.strip()}")
        
        if bib_messages:
            return True, bib_messages
        else:
            return False, "No bibliography-related messages found in log"
    
    except Exception as e:
        return False, f"Error reading log file: {e}"

def main():
    """Main diagnosis function"""
    print_colored("BIBLIOGRAPHY DIAGNOSIS AND REPAIR TOOL", Colors.HEADER)
    print_colored("=" * 50, Colors.HEADER)
    
    # Step 1: Check Biber installation
    print_colored("\n1. Checking Biber installation...", Colors.OKBLUE, "[STEP]")
    biber_ok, biber_msg = check_biber_installation()
    if biber_ok:
        print_colored(biber_msg, Colors.OKGREEN, "[SUCCESS]")
    else:
        print_colored(biber_msg, Colors.FAIL, "[ERROR]")
        print_colored("Install instructions:", Colors.WARNING, "[INFO]")
        print_colored("  - Windows: Install MiKTeX or TeX Live", Colors.WARNING, "  ")
        print_colored("  - macOS: brew install --cask mactex", Colors.WARNING, "  ")
        print_colored("  - Linux: sudo apt-get install texlive-bibtex-extra", Colors.WARNING, "  ")
        return False
    
    # Step 2: Check bibliography file
    print_colored("\n2. Checking bibliography file...", Colors.OKBLUE, "[STEP]")
    bib_path = Path('content/backmatter/bibliography.bib')
    
    file_ok, file_msg = check_file_exists(bib_path)
    if not file_ok:
        print_colored(file_msg, Colors.WARNING, "[WARNING]")
        print_colored("Creating sample bibliography file...", Colors.OKCYAN, "[ACTION]")
        create_ok, create_msg = create_sample_bibliography()
        if create_ok:
            print_colored(create_msg, Colors.OKGREEN, "[SUCCESS]")
        else:
            print_colored(create_msg, Colors.FAIL, "[ERROR]")
            return False
    else:
        print_colored(file_msg, Colors.OKGREEN, "[SUCCESS]")
    
    # Step 3: Check bibliography content
    print_colored("\n3. Checking bibliography content...", Colors.OKBLUE, "[STEP]")
    content_ok, content_msg = check_bibliography_file_content(bib_path)
    if content_ok:
        print_colored(content_msg, Colors.OKGREEN, "[SUCCESS]")
    else:
        print_colored(content_msg, Colors.WARNING, "[WARNING]")
        print_colored("The bibliography file exists but may have issues", Colors.WARNING, "[INFO]")
    
    # Step 4: Check build directory and files
    print_colored("\n4. Checking build directory...", Colors.OKBLUE, "[STEP]")
    build_dir = Path('build')
    
    if not build_dir.exists():
        print_colored("Build directory does not exist", Colors.WARNING, "[WARNING]")
        print_colored("Run the compilation script first to generate build files", Colors.WARNING, "[INFO]")
        return True
    
    # Look for .aux and .bcf files
    main_files = list(build_dir.glob('*.aux'))
    if not main_files:
        print_colored("No .aux files found in build directory", Colors.WARNING, "[WARNING]")
        print_colored("Run LaTeX compilation first", Colors.WARNING, "[INFO]")
        return True
    
    main_file_stem = main_files[0].stem
    print_colored(f"Found main file: {main_file_stem}", Colors.OKGREEN, "[SUCCESS]")
    
    # Check for .bcf file (Biber control file)
    bcf_file = build_dir / f"{main_file_stem}.bcf"
    if bcf_file.exists():
        print_colored("Found Biber control file (.bcf)", Colors.OKGREEN, "[SUCCESS]")
    else:
        print_colored("No Biber control file (.bcf) found", Colors.WARNING, "[WARNING]")
        print_colored("This suggests LaTeX hasn't been run or biblatex isn't loaded", Colors.WARNING, "[INFO]")
    
    # Step 5: Check LaTeX log for bibliography messages
    print_colored("\n5. Checking LaTeX log for bibliography messages...", Colors.OKBLUE, "[STEP]")
    log_ok, log_messages = check_latex_log_for_biber_errors(build_dir, main_file_stem)
    if log_ok:
        print_colored("Found bibliography-related messages:", Colors.OKGREEN, "[SUCCESS]")
        for msg in log_messages[:10]:  # Show first 10 messages
            print_colored(msg, Colors.OKGREEN, "  ")
        if len(log_messages) > 10:
            print_colored(f"... and {len(log_messages) - 10} more messages", Colors.OKGREEN, "  ")
    else:
        print_colored(log_messages, Colors.WARNING, "[WARNING]")
    
    # Step 6: Test Biber compilation
    if bcf_file.exists():
        print_colored("\n6. Testing Biber compilation...", Colors.OKBLUE, "[STEP]")
        biber_test_ok, biber_result = run_biber_with_debug(main_file_stem, build_dir)
        if biber_test_ok:
            print_colored("Biber compilation successful", Colors.OKGREEN, "[SUCCESS]")
        else:
            print_colored("Biber compilation failed", Colors.FAIL, "[ERROR]")
            return False
    
    print_colored("\n" + "=" * 50, Colors.HEADER)
    print_colored("DIAGNOSIS COMPLETE", Colors.HEADER)
    print_colored("If issues persist, try:", Colors.OKBLUE, "[RECOMMENDATIONS]")
    print_colored("1. Run: python compile.py --clean --verbose", Colors.OKBLUE, "  ")
    print_colored("2. Check that your .tex file uses \\cite{} commands", Colors.OKBLUE, "  ")
    print_colored("3. Ensure \\printbibliography is in your document", Colors.OKBLUE, "  ")
    print_colored("4. Verify bibliography entries have valid BibTeX syntax", Colors.OKBLUE, "  ")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_colored("\nDiagnosis interrupted by user", Colors.WARNING, "[INTERRUPTED]")
        sys.exit(1)
    except Exception as e:
        print_colored(f"Unexpected error: {e}", Colors.FAIL, "[ERROR]")
        sys.exit(1)