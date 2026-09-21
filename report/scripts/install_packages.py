# =====================================================
# SCRIPT: scripts/install-packages.py
# =====================================================

#!/usr/bin/env python3
"""
LaTeX Package Installer
Install required LaTeX packages automatically
"""

import os
import sys
import subprocess
import argparse
import time
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

def print_header():
    """Print installation header"""
    header = """
========================================
      LATEX PACKAGE INSTALLER
========================================
"""
    print_colored(header, Colors.HEADER)

def detect_latex_distribution():
    """Detect which LaTeX distribution is installed"""
    # Check for MiKTeX
    try:
        result = subprocess.run(['mpm', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return 'miktex', 'mpm'
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Check for TeX Live
    try:
        result = subprocess.run(['tlmgr', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return 'texlive', 'tlmgr'
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return None, None

def get_essential_packages():
    """Get list of essential LaTeX packages"""
    return [
        # Core packages
        'tcolorbox', 'tikz', 'pgfplots', 'enumitem', 'titlesec',
        'fancyhdr', 'geometry', 'setspace', 'graphicx', 'caption',
        'subcaption', 'booktabs', 'array', 'tabularx', 'longtable',
        'multirow', 'multicol', 'colortbl', 'xcolor', 'float',
        'hyperref', 'cleveref', 'url', 'listings', 'fancyvrb',
        
        # Mathematics and algorithms
        'amsmath', 'amsfonts', 'amssymb', 'algorithm', 'algpseudocode',
        
        # Bibliography and references
        'biblatex', 'csquotes', 'biber',
        
        # Fonts
        'times', 'mathptmx',
        
        # Additional useful packages
        'lipsum', 'blindtext', 'afterpage', 'microtype',
        'tocloft', 'appendix', 'etoolbox'
    ]

def install_miktex_packages(packages, update_first=True):
    """Install packages using MiKTeX package manager"""
    print_colored("Using MiKTeX Package Manager (mpm)", Colors.OKCYAN, "[INFO]")
    
    if update_first:
        print_colored("Updating package database...", Colors.OKCYAN, "[UPDATE]")
        try:
            result = subprocess.run(['mpm', '--update-db'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print_colored("Package database updated", Colors.OKGREEN, "[SUCCESS]")
            else:
                print_colored("Failed to update package database", Colors.WARNING, "[WARNING]")
        except subprocess.TimeoutExpired:
            print_colored("Database update timed out", Colors.WARNING, "[WARNING]")
    
    # Install packages
    installed = 0
    failed = 0
    
    for package in packages:
        print_colored(f"Installing {package}...", Colors.OKCYAN, "[INSTALL]")
        try:
            result = subprocess.run(['mpm', '--install', package], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print_colored(f"Installed {package}", Colors.OKGREEN, "[SUCCESS]")
                installed += 1
            else:
                print_colored(f"Failed to install {package}", Colors.WARNING, "[WARNING]")
                failed += 1
        except subprocess.TimeoutExpired:
            print_colored(f"Installation of {package} timed out", Colors.WARNING, "[WARNING]")
            failed += 1
        except Exception as e:
            print_colored(f"Error installing {package}: {e}", Colors.WARNING, "[WARNING]")
            failed += 1
    
    return installed, failed

def install_texlive_packages(packages, update_first=True):
    """Install packages using TeX Live manager"""
    print_colored("Using TeX Live Manager (tlmgr)", Colors.OKCYAN, "[INFO]")
    
    if update_first:
        print_colored("Updating TeX Live...", Colors.OKCYAN, "[UPDATE]")
        try:
            result = subprocess.run(['tlmgr', 'update', '--self', '--all'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print_colored("TeX Live updated", Colors.OKGREEN, "[SUCCESS]")
            else:
                print_colored("Failed to update TeX Live", Colors.WARNING, "[WARNING]")
        except subprocess.TimeoutExpired:
            print_colored("TeX Live update timed out", Colors.WARNING, "[WARNING]")
    
    # Install packages in batches to be more efficient
    print_colored("Installing packages in batch...", Colors.OKCYAN, "[INSTALL]")
    try:
        cmd = ['tlmgr', 'install'] + packages
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print_colored(f"Successfully installed {len(packages)} packages", Colors.OKGREEN, "[SUCCESS]")
            return len(packages), 0
        else:
            print_colored("Batch installation failed, trying individually...", Colors.WARNING, "[WARNING]")
    except subprocess.TimeoutExpired:
        print_colored("Batch installation timed out, trying individually...", Colors.WARNING, "[WARNING]")
    
    # Fall back to individual installation
    installed = 0
    failed = 0
    
    for package in packages:
        print_colored(f"Installing {package}...", Colors.OKCYAN, "[INSTALL]")
        try:
            result = subprocess.run(['tlmgr', 'install', package], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print_colored(f"Installed {package}", Colors.OKGREEN, "[SUCCESS]")
                installed += 1
            else:
                print_colored(f"Failed to install {package}", Colors.WARNING, "[WARNING]")
                failed += 1
        except subprocess.TimeoutExpired:
            print_colored(f"Installation of {package} timed out", Colors.WARNING, "[WARNING]")
            failed += 1
        except Exception as e:
            print_colored(f"Error installing {package}: {e}", Colors.WARNING, "[WARNING]")
            failed += 1
    
    return installed, failed

def install_packages(packages=None, update_first=True):
    """Install LaTeX packages"""
    print_header()
    
    if packages is None:
        packages = get_essential_packages()
    
    print_colored(f"Installing {len(packages)} LaTeX packages...", Colors.OKCYAN, "[INFO]")
    
    # Detect LaTeX distribution
    distribution, manager = detect_latex_distribution()
    
    if distribution is None:
        print_colored("No LaTeX package manager found", Colors.FAIL, "[ERROR]")
        print_colored("Please install MiKTeX or TeX Live", Colors.FAIL, "[ERROR]")
        return False
    
    print_colored(f"Detected: {distribution.upper()}", Colors.OKGREEN, "[DETECTED]")
    
    start_time = time.time()
    
    try:
        if distribution == 'miktex':
            installed, failed = install_miktex_packages(packages, update_first)
        elif distribution == 'texlive':
            installed, failed = install_texlive_packages(packages, update_first)
        else:
            print_colored("Unsupported package manager", Colors.FAIL, "[ERROR]")
            return False
        
        # Summary
        installation_time = time.time() - start_time
        total = installed + failed
        
        print()
        print_colored("========================================", Colors.HEADER)
        print_colored("         INSTALLATION SUMMARY", Colors.HEADER)
        print_colored("========================================", Colors.HEADER)
        print()
        
        print_colored(f"Total packages: {total}", Colors.OKCYAN, "[SUMMARY]")
        print_colored(f"Successfully installed: {installed}", Colors.OKGREEN, "[SUMMARY]")
        
        if failed > 0:
            print_colored(f"Failed installations: {failed}", Colors.WARNING, "[SUMMARY]")
        
        print_colored(f"Installation time: {installation_time:.1f} seconds", Colors.OKCYAN, "[SUMMARY]")
        
        if failed == 0:
            print_colored("All packages installed successfully!", Colors.OKGREEN, "[SUCCESS]")
            return True
        elif installed > 0:
            print_colored("Partial installation completed", Colors.WARNING, "[PARTIAL]")
            return True
        else:
            print_colored("Installation failed", Colors.FAIL, "[FAILURE]")
            return False
            
    except KeyboardInterrupt:
        print_colored("\nInstallation interrupted by user", Colors.WARNING, "[INTERRUPTED]")
        return False
    except Exception as e:
        print_colored(f"Installation error: {e}", Colors.FAIL, "[ERROR]")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Install LaTeX packages automatically',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Install essential packages
  %(prog)s --no-update         # Skip package database update
  %(prog)s --packages tikz xcolor # Install specific packages
        """
    )
    
    parser.add_argument('--packages', nargs='+', metavar='PACKAGE',
                       help='Specific packages to install (default: essential packages)')
    parser.add_argument('--no-update', action='store_true',
                       help='Skip package database update')
    parser.add_argument('--list-essential', action='store_true',
                       help='List essential packages and exit')
    
    args = parser.parse_args()
    
    if args.list_essential:
        print("Essential LaTeX packages:")
        for package in get_essential_packages():
            print(f"  - {package}")
        sys.exit(0)
    
    try:
        success = install_packages(
            packages=args.packages,
            update_first=not args.no_update
        )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print_colored("\nInstallation interrupted by user", Colors.WARNING, "[INTERRUPTED]")
        sys.exit(1)
    except Exception as e:
        print_colored(f"Unexpected error: {e}", Colors.FAIL, "[ERROR]")
        sys.exit(1)

if __name__ == "__main__":
    main()
    