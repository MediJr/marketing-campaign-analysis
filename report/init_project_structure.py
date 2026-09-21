#!/usr/bin/env python3
"""
Professional LaTeX Template - Project Structure Initializer
Cross-platform project structure creation script
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import json
import re

# Colors for terminal output
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
    """Print script header"""
    header = """
========================================
   PROFESSIONAL LATEX TEMPLATE INIT
========================================
"""
    print_colored(header, Colors.HEADER)

def validate_project_name(name):
    """Validate project name"""
    if not name:
        return False, "Project name cannot be empty"
    
    # Check for invalid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return False, "Project name can only contain letters, numbers, hyphens, and underscores"
    
    # Check length
    if len(name) > 50:
        return False, "Project name must be 50 characters or less"
    
    if len(name) < 2:
        return False, "Project name must be at least 2 characters"
    
    return True, ""

def create_directory_structure(base_path):
    """Create the complete directory structure"""
    directories = [
        '.vscode',
        'assets/fonts',
        'assets/images/appendices',
        'assets/images/architecture', 
        'assets/images/badges',
        'assets/images/charts',
        'assets/images/diagrams/mermaid',
        'assets/images/diagrams/plantuml/assets',
        'assets/images/figures',
        'assets/images/screenshots',
        'assets/logos',
        'build/config',
        'build/templates',
        'config',
        'content/frontmatter',
        'content/chapters',
        'content/backmatter',
        'diagrams/plantuml',
        'diagrams/mermaid',
        'diagrams/tikz',
        'scripts',
        'templates',
        'docs'
    ]
    
    print_colored("Creating directory structure...", Colors.OKCYAN, "[INFO]")
    
    created_count = 0
    for directory in directories:
        dir_path = base_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created_count += 1
    
    print_colored(f"Created {created_count} directories successfully", Colors.OKGREEN, "[SUCCESS]")
    return len(directories)

def create_gitkeep_files(base_path):
    """Create .gitkeep files for empty directories"""
    gitkeep_dirs = [
        'assets/fonts',
        'build', 
        'diagrams/plantuml',
        'diagrams/mermaid',
        'diagrams/tikz'
    ]
    
    for directory in gitkeep_dirs:
        gitkeep_path = base_path / directory / '.gitkeep'
        gitkeep_path.touch(exist_ok=True)

def create_gitignore(base_path):
    """Create .gitignore file"""
    gitignore_content = """# LaTeX build files
*.aux
*.bbl
*.bcf
*.blg
*.fdb_latexmk
*.fls
*.log
*.out
*.run.xml
*.synctex.gz
*.toc
*.lof
*.lot
*.acn
*.acr
*.alg
*.glg
*.glo
*.gls
*.idx
*.ilg
*.ind
*.ist
*.lol
*.nav
*.snm
*.vrb
*.xdy
*.tdo

# Build directory (except structure)
build/*.pdf
build/*.aux
build/*.log
build/*.out
build/*.toc
build/*.lof
build/*.lot
build/*.bbl
build/*.bcf
build/*.blg
build/*.run.xml
build/*.synctex.gz

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
*.tmp
*.temp
*.swp
*.swo
*~

# IDE files
.vscode/settings.json
.idea/

# Backup files
*.backup
*.bak

# Python cache
__pycache__/
*.pyc
*.pyo
"""
    
    gitignore_path = base_path / '.gitignore'
    if not gitignore_path.exists():
        gitignore_path.write_text(gitignore_content, encoding='utf-8')
        print_colored("Created .gitignore file", Colors.OKGREEN, "[SUCCESS]")

def create_readme(base_path, project_name):
    """Create README.md file"""
    readme_content = f"""# {project_name}

Professional LaTeX document created with the Professional LaTeX Template.

## Quick Start

1. Configure your document metadata in `config/metadata.tex`
2. Customize colors and styles in `config/` directory  
3. Add your content in `content/` directory
4. Compile with appropriate build script

## Structure

- `config/` - Configuration files
- `content/` - Document content
- `assets/` - Images and resources
- `templates/` - Reusable templates
- `scripts/` - Build scripts

## Requirements

- LaTeX distribution (TeX Live/MiKTeX)
- Modern LaTeX packages (see template documentation)

## Build

### Windows
```cmd
scripts\\compile.bat
```

### Unix/Mac  
```bash
chmod +x scripts/*.sh
./scripts/compile.sh
```

### Python (Cross-platform)
```bash
python scripts/compile.py
```

## Contributing

Please follow the project structure and coding conventions.

## Template Source

Generated with Professional LaTeX Template Initializer
"""
    
    readme_path = base_path / 'README.md'
    if not readme_path.exists():
        readme_path.write_text(readme_content, encoding='utf-8')
        print_colored("Created README.md file", Colors.OKGREEN, "[SUCCESS]")

def create_package_json(base_path, project_name):
    """Create package.json file"""
    package_data = {
        "name": project_name,
        "version": "1.0.0", 
        "description": "Professional LaTeX Document",
        "scripts": {
            "build": "python scripts/compile.py",
            "clean": "python scripts/clean.py",
            "quick": "python scripts/compile.py --quick"
        },
        "devDependencies": {},
        "repository": {
            "type": "git",
            "url": ""
        },
        "keywords": ["latex", "document", "professional", "template"],
        "author": "",
        "license": "MIT"
    }
    
    package_path = base_path / 'package.json'
    if not package_path.exists():
        package_path.write_text(json.dumps(package_data, indent=2), encoding='utf-8')
        print_colored("Created package.json file", Colors.OKGREEN, "[SUCCESS]")

def create_vscode_config(base_path):
    """Create VS Code configuration files"""
    vscode_settings = {
        "latex-workshop.latex.tools": [
            {
                "name": "pdflatex",
                "command": "pdflatex",
                "args": [
                    "-interaction=nonstopmode",
                    "-file-line-error",
                    "-output-directory=%OUTDIR%",
                    "%DOC%"
                ]
            },
            {
                "name": "biber",
                "command": "biber",
                "args": ["%DOCFILE%"]
            }
        ],
        "latex-workshop.latex.recipes": [
            {
                "name": "pdflatex → biber → pdflatex × 2",
                "tools": ["pdflatex", "biber", "pdflatex", "pdflatex"]
            },
            {
                "name": "pdflatex",
                "tools": ["pdflatex"]
            }
        ],
        "latex-workshop.latex.outDir": "./build",
        "latex-workshop.latex.autoClean.run": "onBuilt",
        "latex-workshop.view.pdf.viewer": "tab",
        "files.associations": {
            "*.cls": "latex",
            "*.sty": "latex"
        },
        "editor.wordWrap": "on",
        "[latex]": {
            "editor.wordWrap": "on",
            "editor.formatOnSave": False
        },
        "cSpell.enableFiletypes": ["latex", "tex"],
        "python.defaultInterpreterPath": "python3"
    }
    
    vscode_extensions = {
        "recommendations": [
            "james-yu.latex-workshop",
            "streetsidesoftware.code-spell-checker", 
            "ms-python.python",
            "gruntfuggly.todo-tree"
        ]
    }
    
    vscode_dir = base_path / '.vscode'
    settings_file = vscode_dir / 'settings.json'
    extensions_file = vscode_dir / 'extensions.json'
    
    if not settings_file.exists():
        settings_file.write_text(json.dumps(vscode_settings, indent=2), encoding='utf-8')
        print_colored("Created VS Code settings", Colors.OKGREEN, "[SUCCESS]")
    
    if not extensions_file.exists():
        extensions_file.write_text(json.dumps(vscode_extensions, indent=2), encoding='utf-8')
        print_colored("Created VS Code extensions config", Colors.OKGREEN, "[SUCCESS]")

def create_project_structure_doc(base_path, project_name, dir_count):
    """Create project structure documentation"""
    content = f"""# {project_name} - Project Structure

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Directory Structure

```
{project_name}/
├── .vscode/                    # VS Code configuration
├── assets/                     # Project assets
│   ├── fonts/                 # Custom fonts
│   ├── images/                # Image files
│   │   ├── appendices/        # Appendix images
│   │   ├── architecture/      # Architecture diagrams
│   │   ├── badges/            # Status badges
│   │   ├── charts/            # Charts and graphs
│   │   ├── diagrams/          # Technical diagrams
│   │   │   ├── mermaid/       # Mermaid diagram outputs
│   │   │   └── plantuml/      # PlantUML diagram outputs
│   │   ├── figures/           # General figures
│   │   └── screenshots/       # Application screenshots
│   └── logos/                 # Company/institution logos
├── build/                     # Compilation output
├── config/                    # Modular configuration
├── content/                   # Document content
│   ├── frontmatter/           # Front matter pages
│   ├── chapters/              # Main chapters
│   └── backmatter/            # Conclusion and appendices
├── diagrams/                  # Diagram source files
├── scripts/                   # Build and utility scripts
├── templates/                 # Reusable templates
└── docs/                      # Additional documentation
```

## File Purposes

### Configuration (`config/`)
- `metadata.tex` - Document metadata and variables
- `packages.tex` - LaTeX packages and dependencies
- `colors.tex` - Color scheme definitions
- `commands.tex` - Custom commands and macros
- `style.tex` - Typography and layout settings

### Content (`content/`)
- `frontmatter/` - Title page, abstract, TOC, etc.
- `chapters/` - Main document chapters
- `backmatter/` - Conclusion, appendices, bibliography

### Templates (`templates/`)
- `boxes.tex` - Custom environment definitions
- `figures.tex` - Figure insertion templates
- `tables.tex` - Table formatting templates

## Next Steps

1. **Copy template files**: internshipreport.cls, main.tex
2. **Copy configuration files** from template config/ directory
3. **Copy build scripts** from template scripts/ directory
4. **Copy template files** from template templates/ directory
5. **Configure your document** in config/metadata.tex
6. **Start writing** your content

## Build Options

### Cross-platform (Python)
```bash
python scripts/compile.py        # Full compilation
python scripts/compile.py --quick # Quick compilation  
python scripts/clean.py          # Clean build files
```

### Platform-specific scripts
- Windows: `scripts/*.bat`
- Unix/Mac: `scripts/*.sh`
- PowerShell: `scripts/*.ps1`

## Tips

- Use VS Code with LaTeX Workshop extension for best experience
- Keep images in appropriate subdirectories of assets/images/
- Follow naming conventions for consistency
- Regular compilation helps catch errors early
- Use version control (Git) to track changes

Generated by Professional LaTeX Template Initializer (Python)
"""
    
    doc_path = base_path / 'PROJECT_STRUCTURE.md'
    if not doc_path.exists():
        doc_path.write_text(content, encoding='utf-8')
        print_colored("Created PROJECT_STRUCTURE.md", Colors.OKGREEN, "[SUCCESS]")

def check_directory_empty(path):
    """Check if directory is empty or contains only hidden files"""
    if not path.exists():
        return True
    
    try:
        items = list(path.iterdir())
        # Consider directory empty if it only contains hidden files (starting with .)
        visible_items = [item for item in items if not item.name.startswith('.')]
        return len(visible_items) == 0
    except PermissionError:
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Initialize Professional LaTeX Template project structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my-project              # Create new directory 'my-project'
  %(prog)s --current-dir           # Initialize in current directory
  %(prog)s --current-dir --force   # Force init in non-empty directory
  %(prog)s my-thesis --minimal     # Create minimal structure only
        """
    )
    
    parser.add_argument('project_name', nargs='?', default='', 
                       help='Project name (required unless --current-dir is used)')
    parser.add_argument('--current-dir', action='store_true', 
                       help='Initialize in current directory instead of creating new one')
    parser.add_argument('--minimal', action='store_true', 
                       help='Create minimal structure only')
    parser.add_argument('--force', action='store_true', 
                       help='Force initialization even if directory is not empty')
    parser.add_argument('--quiet', action='store_true', 
                       help='Suppress output messages')
    parser.add_argument('--no-git', action='store_true', 
                       help='Skip .gitignore creation')
    parser.add_argument('--no-vscode', action='store_true', 
                       help='Skip VS Code configuration')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_header()
    
    # Determine project name and target directory
    if args.current_dir:
        target_path = Path.cwd()
        project_name = target_path.name
        
        if not args.quiet:
            print_colored(f"Initializing in current directory: {target_path}", Colors.OKCYAN, "[INFO]")
        
        # Check if directory is empty
        if not check_directory_empty(target_path) and not args.force:
            print_colored("Current directory is not empty. Use --force to initialize anyway.", Colors.FAIL, "[ERROR]")
            print_colored("Current directory contents:", Colors.WARNING, "[WARNING]")
            try:
                items = [item.name for item in target_path.iterdir() if not item.name.startswith('.')]
                for item in items[:5]:  # Show first 5 items
                    print(f"  - {item}")
                if len(items) > 5:
                    print(f"  ... and {len(items) - 5} more items")
            except PermissionError:
                print_colored("Cannot read directory contents (permission denied)", Colors.FAIL, "[ERROR]")
            sys.exit(1)
    else:
        project_name = args.project_name
        if not project_name:
            project_name = input("Enter project name: ").strip()
            if not project_name:
                print_colored("Project name is required", Colors.FAIL, "[ERROR]")
                sys.exit(1)
        
        # Validate project name
        is_valid, error_msg = validate_project_name(project_name)
        if not is_valid:
            print_colored(f"Invalid project name: {error_msg}", Colors.FAIL, "[ERROR]")
            sys.exit(1)
        
        target_path = Path(project_name)
        
        # Create project directory
        if target_path.exists():
            if not check_directory_empty(target_path) and not args.force:
                print_colored(f"Directory '{project_name}' already exists and is not empty", Colors.FAIL, "[ERROR]")
                print_colored("Use --force to initialize anyway", Colors.WARNING, "[WARNING]")
                sys.exit(1)
        else:
            target_path.mkdir()
            if not args.quiet:
                print_colored(f"Created project directory: {project_name}", Colors.OKGREEN, "[SUCCESS]")
    
    # Change to target directory
    original_cwd = Path.cwd()
    os.chdir(target_path)
    
    try:
        # Create structure
        if not args.quiet:
            print_colored("Creating project structure...", Colors.OKCYAN, "[INFO]")
        
        dir_count = create_directory_structure(Path('.'))
        create_gitkeep_files(Path('.'))
        
        if not args.no_git:
            create_gitignore(Path('.'))
        
        create_readme(Path('.'), project_name)
        create_package_json(Path('.'), project_name)
        
        if not args.no_vscode:
            create_vscode_config(Path('.'))
        
        create_project_structure_doc(Path('.'), project_name, dir_count)
        
        if not args.quiet:
            print_colored("Project structure created successfully", Colors.OKGREEN, "[SUCCESS]")
            print()
        
        # Summary
        if not args.quiet:
            print_colored("========================================", Colors.HEADER)
            print_colored("           INITIALIZATION COMPLETE", Colors.HEADER)
            print_colored("========================================", Colors.HEADER)
            print()
            print_colored(f"Project: {project_name}", Colors.OKGREEN, "[SUCCESS]")
            print_colored(f"Location: {target_path.absolute()}", Colors.OKGREEN, "[SUCCESS]")
            print_colored(f"Directories created: {dir_count}", Colors.OKGREEN, "[SUCCESS]")
            
            files_created = []
            if not args.no_git:
                files_created.append(".gitignore")
            if not args.no_vscode:
                files_created.append("VS Code config")
            files_created.extend(["README.md", "PROJECT_STRUCTURE.md", "package.json"])
            
            print_colored(f"Files created: {', '.join(files_created)}", Colors.OKGREEN, "[SUCCESS]")
            print()
            print_colored("NEXT STEPS:", Colors.OKCYAN, "[INFO]")
            print("   1. Copy template files (internshipreport.cls, main.tex)")
            print("   2. Copy config/ templates from the main template")
            print("   3. Copy scripts/ from the main template")
            print("   4. Copy templates/ from the main template")
            print("   5. Start editing your content!")
            print()
            print_colored("See PROJECT_STRUCTURE.md for detailed information", Colors.OKCYAN, "[INFO]")
        
    except Exception as e:
        print_colored(f"Error during initialization: {str(e)}", Colors.FAIL, "[ERROR]")
        sys.exit(1)
    
    finally:
        # Return to original directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()
