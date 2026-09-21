# =====================================================
# SCRIPT: scripts/check.py
# =====================================================

#!/usr/bin/env python3
"""
LaTeX Project Checker
Validate project structure and dependencies
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json

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
    """Print check header"""
    header = """
========================================
      LATEX PROJECT CHECKER
========================================
"""
    print_colored(header, Colors.HEADER)

def check_command_available(command):
    """Check if a command is available in PATH"""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout.split('\n')[0] if result.stdout else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, ""

def check_latex_installation():
    """Check LaTeX installation"""
    print_colored("Checking LaTeX installation...", Colors.OKCYAN, "[CHECK]")
    
    tools_to_check = [
        ('pdflatex', 'Required for PDF compilation'),
        ('biber', 'Required for bibliography processing'),
        ('makeindex', 'Required for index generation'),
        ('latexmk', 'Optional: Advanced build tool'),
    ]
    
    results = {}
    all_good = True
    
    for tool, description in tools_to_check:
        available, version = check_command_available(tool)
        results[tool] = {'available': available, 'version': version, 'description': description}
        
        if available:
            print_colored(f"{tool}: {version}", Colors.OKGREEN, "[OK]")
        else:
            if tool in ['pdflatex']:
                print_colored(f"{tool}: Not found - {description}", Colors.FAIL, "[ERROR]")
                all_good = False
            else:
                print_colored(f"{tool}: Not found - {description}", Colors.WARNING, "[WARNING]")
    
    return all_good, results

def check_project_structure():
    """Check project directory structure"""
    print_colored("Checking project structure...", Colors.OKCYAN, "[CHECK]")
    
    required_dirs = [
        ('config', 'Configuration files'),
        ('content', 'Document content'),
        ('assets', 'Images and resources'),
        ('scripts', 'Build scripts'),
        ('templates', 'Reusable templates'),
    ]
    
    optional_dirs = [
        ('build', 'Build output directory'),
        ('docs', 'Additional documentation'),
        ('diagrams', 'Diagram source files'),
    ]
    
    results = {}
    all_good = True
    
    # Check required directories
    for dir_name, description in required_dirs:
        dir_path = Path(dir_name)
        exists = dir_path.exists() and dir_path.is_dir()
        results[dir_name] = {'exists': exists, 'description': description, 'required': True}
        
        if exists:
            print_colored(f"{dir_name}/: {description}", Colors.OKGREEN, "[OK]")
        else:
            print_colored(f"{dir_name}/: Missing - {description}", Colors.FAIL, "[ERROR]")
            all_good = False
    
    # Check optional directories
    for dir_name, description in optional_dirs:
        dir_path = Path(dir_name)
        exists = dir_path.exists() and dir_path.is_dir()
        results[dir_name] = {'exists': exists, 'description': description, 'required': False}
        
        if exists:
            print_colored(f"{dir_name}/: {description}", Colors.OKGREEN, "[OK]")
        else:
            print_colored(f"{dir_name}/: Not found - {description}", Colors.WARNING, "[INFO]")
    
    return all_good, results

def check_essential_files():
    """Check for essential project files"""
    print_colored("Checking essential files...", Colors.OKCYAN, "[CHECK]")
    
    essential_files = [
        ('main.tex', 'Main LaTeX document'),
        ('internshipreport.cls', 'Document class file (or alternative .cls)'),
        ('config/metadata.tex', 'Document metadata configuration'),
        ('README.md', 'Project documentation'),
    ]
    
    results = {}
    all_good = True
    
    for file_path, description in essential_files:
        path = Path(file_path)
        
        # Special handling for class files
        if file_path == 'internshipreport.cls':
            cls_files = list(Path('.').glob('*.cls'))
            exists = len(cls_files) > 0
            if exists:
                actual_file = cls_files[0].name
                print_colored(f"{actual_file}: {description}", Colors.OKGREEN, "[OK]")
            else:
                print_colored(f"*.cls: Missing - {description}", Colors.FAIL, "[ERROR]")
                all_good = False
            results[file_path] = {'exists': exists, 'description': description}
            continue
        
        exists = path.exists() and path.is_file()
        results[file_path] = {'exists': exists, 'description': description}
        
        if exists:
            print_colored(f"{file_path}: {description}", Colors.OKGREEN, "[OK]")
        else:
            print_colored(f"{file_path}: Missing - {description}", Colors.FAIL, "[ERROR]")
            all_good = False
    
    return all_good, results

def check_config_files():
    """Check configuration files"""
    print_colored("Checking configuration files...", Colors.OKCYAN, "[CHECK]")
    
    config_files = [
        ('config/colors.tex', 'Color scheme definitions'),
        ('config/commands.tex', 'Custom commands'),
        ('config/packages.tex', 'Package definitions'),
        ('config/style.tex', 'Typography and layout'),
    ]
    
    results = {}
    all_good = True
    
    for file_path, description in config_files:
        path = Path(file_path)
        exists = path.exists() and path.is_file()
        results[file_path] = {'exists': exists, 'description': description}
        
        if exists:
            print_colored(f"{file_path}: {description}", Colors.OKGREEN, "[OK]")
        else:
            print_colored(f"{file_path}: Missing - {description}", Colors.WARNING, "[WARNING]")
    
    return True, results  # Config files are not critical

def check_build_scripts():
    """Check build scripts"""
    print_colored("Checking build scripts...", Colors.OKCYAN, "[CHECK]")
    
    script_files = [
        ('scripts/compile.py', 'Python compilation script'),
        ('scripts/clean.py', 'Python cleaning script'),
        ('scripts/watch.py', 'File watcher script'),
        ('scripts/check.py', 'Project checker script'),
    ]
    
    results = {}
    
    for file_path, description in script_files:
        path = Path(file_path)
        exists = path.exists() and path.is_file()
        results[file_path] = {'exists': exists, 'description': description}
        
        if exists:
            print_colored(f"{file_path}: {description}", Colors.OKGREEN, "[OK]")
        else:
            print_colored(f"{file_path}: Missing - {description}", Colors.WARNING, "[INFO]")
    
    return True, results

def check_git_setup():
    """Check Git repository setup"""
    print_colored("Checking Git setup...", Colors.OKCYAN, "[CHECK]")
    
    git_files = [
        ('.git', 'Git repository'),
        ('.gitignore', 'Git ignore file'),
    ]
    
    results = {}
    
    for item_path, description in git_files:
        path = Path(item_path)
        exists = path.exists()
        results[item_path] = {'exists': exists, 'description': description}
        
        if exists:
            print_colored(f"{item_path}: {description}", Colors.OKGREEN, "[OK]")
        else:
            print_colored(f"{item_path}: Not found - {description}", Colors.WARNING, "[INFO]")
    
    return True, results

def check_vs_code_setup():
    """Check VS Code configuration"""
    print_colored("Checking VS Code setup...", Colors.OKCYAN, "[CHECK]")
    
    vscode_files = [
        ('.vscode/settings.json', 'VS Code settings'),
        ('.vscode/extensions.json', 'Recommended extensions'),
    ]
    
    results = {}
    
    for file_path, description in vscode_files:
        path = Path(file_path)
        exists = path.exists() and path.is_file()
        results[file_path] = {'exists': exists, 'description': description}
        
        if exists:
            print_colored(f"{file_path}: {description}", Colors.OKGREEN, "[OK]")
        else:
            print_colored(f"{file_path}: Missing - {description}", Colors.WARNING, "[INFO]")
    
    return True, results

def run_comprehensive_check(output_file=None):
    """Run comprehensive project check"""
    print_header()
    
    all_checks = []
    all_results = {}
    
    # Run all checks
    checks = [
        ("LaTeX Installation", check_latex_installation),
        ("Project Structure", check_project_structure),
        ("Essential Files", check_essential_files),
        ("Configuration Files", check_config_files),
        ("Build Scripts", check_build_scripts),
        ("Git Setup", check_git_setup),
        ("VS Code Setup", check_vs_code_setup),
    ]
    
    for check_name, check_func in checks:
        try:
            success, results = check_func()
            all_checks.append(success)
            all_results[check_name] = {
                'success': success,
                'results': results
            }
        except Exception as e:
            print_colored(f"Error in {check_name}: {e}", Colors.FAIL, "[ERROR]")
            all_checks.append(False)
            all_results[check_name] = {
                'success': False,
                'error': str(e)
            }
        
        print()  # Add spacing between checks
    
    # Summary
    total_checks = len(all_checks)
    successful_checks = sum(all_checks)
    
    print_colored("========================================", Colors.HEADER)
    print_colored("              SUMMARY", Colors.HEADER)
    print_colored("========================================", Colors.HEADER)
    print()
    
    if successful_checks == total_checks:
        print_colored(f"All {total_checks} checks passed!", Colors.OKGREEN, "[SUCCESS]")
        overall_status = "READY"
    else:
        failed_checks = total_checks - successful_checks
        print_colored(f"{successful_checks}/{total_checks} checks passed", Colors.WARNING, "[PARTIAL]")
        print_colored(f"{failed_checks} checks failed", Colors.FAIL, "[ISSUES]")
        overall_status = "ISSUES_FOUND"
    
    # Save results if requested
    if output_file:
        try:
            report = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'overall_status': overall_status,
                'summary': {
                    'total_checks': total_checks,
                    'successful_checks': successful_checks,
                    'failed_checks': total_checks - successful_checks
                },
                'detailed_results': all_results
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            print_colored(f"Detailed report saved to: {output_file}", Colors.OKCYAN, "[REPORT]")
        except Exception as e:
            print_colored(f"Could not save report: {e}", Colors.WARNING, "[WARNING]")
    
    return successful_checks == total_checks

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Check LaTeX project setup and dependencies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Run all checks
  %(prog)s --report check.json # Save detailed report
  %(prog)s --quiet             # Minimal output
        """
    )
    
    parser.add_argument('--report', metavar='FILE',
                       help='Save detailed report to JSON file')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output (errors only)')
    
    args = parser.parse_args()
    
    try:
        success = run_comprehensive_check(output_file=args.report)
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print_colored("\nCheck interrupted by user", Colors.WARNING, "[INTERRUPTED]")
        sys.exit(1)
    except Exception as e:
        print_colored(f"Unexpected error: {e}", Colors.FAIL, "[ERROR]")
        sys.exit(1)

if __name__ == "__main__":
    main()
