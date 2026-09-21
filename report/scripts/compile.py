#!/usr/bin/env python3
"""
Professional LaTeX Template - Project Management Scripts
Collection of essential Python scripts for LaTeX project management
"""

# =====================================================
# SCRIPT: scripts/compile.py
# =====================================================

#!/usr/bin/env python3
"""
LaTeX Document Compiler
Cross-platform compilation script with advanced features
"""

import os
import sys
import subprocess
import argparse
import time
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
    """Print compilation header"""
    header = """
========================================
      LATEX DOCUMENT COMPILATION
========================================
"""
    print_colored(header, Colors.HEADER)

def check_latex_installation():
    """Check if LaTeX is installed and available"""
    try:
        result = subprocess.run(['pdflatex', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print_colored(f"LaTeX found: {version_line}", Colors.OKGREEN, "[INFO]")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print_colored("LaTeX not found in PATH", Colors.FAIL, "[ERROR]")
    print_colored("Please install LaTeX (MiKTeX/TeX Live)", Colors.WARNING, "[WARNING]")
    return False

def check_biber_installation():
    """Check if Biber is installed for bibliography"""
    try:
        result = subprocess.run(['biber', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def create_build_directory():
    """Create build directory if it doesn't exist"""
    build_dir = Path('build')
    if not build_dir.exists():
        build_dir.mkdir()
        print_colored("Created build directory", Colors.OKGREEN, "[INFO]")
    return build_dir

def copy_class_files(build_dir):
    """Copy class files to build directory"""
    class_files = [
        'internshipreport.cls',
        'rapportstage.cls',  # Alternative name
    ]
    
    for class_file in class_files:
        class_path = Path(class_file)
        if class_path.exists():
            shutil.copy2(class_path, build_dir)
            print_colored(f"Copied {class_file} to build directory", Colors.OKGREEN, "[INFO]")
            return True
    
    print_colored("No class file found to copy", Colors.WARNING, "[WARNING]")
    return False

def run_pdflatex(main_file, build_dir, interaction_mode='nonstopmode'):
    """Run pdflatex compilation"""
    cmd = [
        'pdflatex',
        f'-interaction={interaction_mode}',
        f'-output-directory={build_dir}',
        str(main_file)
    ]
    
    print_colored(f"Running: {' '.join(cmd)}", Colors.OKCYAN, "[COMPILE]")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result
    except subprocess.TimeoutExpired:
        print_colored("Compilation timed out (5 minutes)", Colors.FAIL, "[ERROR]")
        return False, None

def run_biber(main_file_stem, build_dir):
    """Run biber for bibliography"""
    cmd = ['biber', str(build_dir / main_file_stem)]
    
    print_colored(f"Running: {' '.join(cmd)}", Colors.OKCYAN, "[BIBER]")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result
    except subprocess.TimeoutExpired:
        print_colored("Biber timed out (1 minute)", Colors.FAIL, "[ERROR]")
        return False, None

def analyze_log_file(build_dir, main_file_stem):
    """Analyze LaTeX log file for errors and warnings"""
    log_file = build_dir / f"{main_file_stem}.log"
    
    if not log_file.exists():
        return [], []
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
    except Exception:
        return [], []
    
    errors = []
    warnings = []
    
    lines = log_content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('!'):
            errors.append(f"Line {i+1}: {line}")
        elif 'Warning:' in line or 'warning:' in line:
            warnings.append(f"Line {i+1}: {line}")
    
    return errors, warnings

def get_output_stats(build_dir, main_file_stem):
    """Get compilation statistics from log file"""
    log_file = build_dir / f"{main_file_stem}.log"
    
    if not log_file.exists():
        return None
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
        
        # Look for output written line
        for line in log_content.split('\n'):
            if 'Output written on' in line:
                return line.strip()
    except Exception:
        pass
    
    return None

def compile_document(main_file='main.tex', quick=False, verbose=False, clean_first=False):
    """Main compilation function"""
    
    print_header()
    
    # Validate main file
    main_path = Path(main_file)
    if not main_path.exists():
        print_colored(f"Main file not found: {main_file}", Colors.FAIL, "[ERROR]")
        return False
    
    # Check LaTeX installation
    if not check_latex_installation():
        return False
    
    # Check if we need Biber
    has_biber = check_biber_installation()
    if not has_biber:
        print_colored("Biber not found - bibliography will be skipped", Colors.WARNING, "[WARNING]")
    
    # Create build directory
    build_dir = create_build_directory()
    
    # Copy class files
    copy_class_files(build_dir)
    
    # Clean if requested
    if clean_first:
        print_colored("Cleaning build directory...", Colors.OKCYAN, "[CLEAN]")
        for file in build_dir.glob('*.aux'):
            file.unlink()
        for file in build_dir.glob('*.log'):
            file.unlink()
        for file in build_dir.glob('*.out'):
            file.unlink()
    
    main_file_stem = main_path.stem
    success = True
    
    print_colored("Starting compilation process...", Colors.OKCYAN, "[INFO]")
    start_time = time.time()
    
    if quick:
        # Quick compilation - single pass
        print_colored("[1/1] Quick compilation pass...", Colors.OKCYAN, "[STEP]")
        success, result = run_pdflatex(main_path, build_dir)
        
        if not success and result:
            print_colored("Quick compilation failed", Colors.FAIL, "[ERROR]")
            if verbose:
                print_colored("Error output:", Colors.FAIL, "[DEBUG]")
                print(result.stderr)
    else:
        # Full compilation process
        compilation_steps = [
            ("[1/4] First compilation pass...", lambda: run_pdflatex(main_path, build_dir)),
        ]
        
        if has_biber:
            compilation_steps.append(
                ("[2/4] Processing bibliography...", lambda: run_biber(main_file_stem, build_dir))
            )
            compilation_steps.extend([
                ("[3/4] Second compilation pass...", lambda: run_pdflatex(main_path, build_dir)),
                ("[4/4] Final compilation pass...", lambda: run_pdflatex(main_path, build_dir))
            ])
        else:
            compilation_steps.extend([
                ("[2/3] Second compilation pass...", lambda: run_pdflatex(main_path, build_dir)),
                ("[3/3] Final compilation pass...", lambda: run_pdflatex(main_path, build_dir))
            ])
        
        for step_desc, step_func in compilation_steps:
            print_colored(step_desc, Colors.OKCYAN, "[STEP]")
            step_success, result = step_func()
            
            if not step_success:
                success = False
                if result:
                    print_colored(f"Step failed: {step_desc}", Colors.FAIL, "[ERROR]")
                    if verbose:
                        print_colored("Error output:", Colors.FAIL, "[DEBUG]")
                        print(result.stderr)
                break
    
    # Analyze results
    compilation_time = time.time() - start_time
    
    if success:
        print_colored(f"Compilation completed successfully in {compilation_time:.2f}s", Colors.OKGREEN, "[SUCCESS]")
        
        # Show output statistics
        output_stats = get_output_stats(build_dir, main_file_stem)
        if output_stats:
            print_colored(output_stats, Colors.OKGREEN, "[INFO]")
        
        # Check for warnings
        errors, warnings = analyze_log_file(build_dir, main_file_stem)
        
        if warnings:
            print_colored(f"Found {len(warnings)} warnings:", Colors.WARNING, "[WARNING]")
            for warning in warnings[:5]:  # Show first 5 warnings
                print_colored(warning, Colors.WARNING, "  ")
            if len(warnings) > 5:
                print_colored(f"... and {len(warnings) - 5} more warnings", Colors.WARNING, "  ")
        
        # Check if PDF was created
        pdf_file = build_dir / f"{main_file_stem}.pdf"
        if pdf_file.exists():
            print_colored(f"PDF created: {pdf_file}", Colors.OKGREEN, "[OUTPUT]")
        else:
            print_colored("PDF file not found", Colors.WARNING, "[WARNING]")
    else:
        print_colored(f"Compilation failed after {compilation_time:.2f}s", Colors.FAIL, "[FAILURE]")
        
        # Show errors
        errors, warnings = analyze_log_file(build_dir, main_file_stem)
        
        if errors:
            print_colored(f"Found {len(errors)} errors:", Colors.FAIL, "[ERROR]")
            for error in errors[:3]:  # Show first 3 errors
                print_colored(error, Colors.FAIL, "  ")
        
        print_colored(f"Check log file: {build_dir}/{main_file_stem}.log", Colors.FAIL, "[DEBUG]")
    
    return success

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Compile LaTeX document with advanced options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Full compilation
  %(prog)s --quick             # Quick single-pass compilation
  %(prog)s --clean             # Clean and compile
  %(prog)s -f custom.tex       # Compile custom file
  %(prog)s --verbose           # Show detailed output
        """
    )
    
    parser.add_argument('-f', '--file', default='main.tex',
                       help='Main LaTeX file to compile (default: main.tex)')
    parser.add_argument('-q', '--quick', action='store_true',
                       help='Quick compilation (single pass)')
    parser.add_argument('-c', '--clean', action='store_true',
                       help='Clean build directory before compilation')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show verbose output and error details')
    parser.add_argument('--open', action='store_true',
                       help='Open PDF after successful compilation')
    
    args = parser.parse_args()
    
    try:
        success = compile_document(
            main_file=args.file,
            quick=args.quick,
            verbose=args.verbose,
            clean_first=args.clean
        )
        
        if success and args.open:
            pdf_path = Path('build') / f"{Path(args.file).stem}.pdf"
            if pdf_path.exists():
                try:
                    if sys.platform.startswith('win'):
                        os.startfile(pdf_path)
                    elif sys.platform.startswith('darwin'):
                        subprocess.run(['open', pdf_path])
                    else:
                        subprocess.run(['xdg-open', pdf_path])
                    print_colored("PDF opened successfully", Colors.OKGREEN, "[INFO]")
                except Exception as e:
                    print_colored(f"Could not open PDF: {e}", Colors.WARNING, "[WARNING]")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print_colored("\nCompilation interrupted by user", Colors.WARNING, "[INTERRUPTED]")
        sys.exit(1)
    except Exception as e:
        print_colored(f"Unexpected error: {e}", Colors.FAIL, "[ERROR]")
        sys.exit(1)

if __name__ == "__main__":
    main()

