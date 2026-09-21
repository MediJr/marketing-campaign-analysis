# Makefile for LaTeX Report Template

.PHONY: help build clean watch release list-releases setup

# Default target
help:
	@echo "LaTeX Report Template - Available Commands:"
	@echo ""
	@echo "  make build         - Compile the LaTeX document"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make watch         - Watch files and auto-compile"
	@echo "  make release TAG=  - Create a new release (e.g., make release TAG=v1.0.0)"
	@echo "  make list-releases - List existing releases"
	@echo "  make setup         - Setup development environment"
	@echo ""

# Build the document
build:
	@echo "Building LaTeX document..."
	@python scripts/compile.py

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -f *.aux *.log *.out *.toc *.lof *.lot *.bbl *.blg *.bcf *.run.xml *.synctex.gz

# Watch for changes and auto-compile
watch:
	@echo "Starting file watcher..."
	@python scripts/watch.py

# Create a release
release:
	@if [ -z "$(TAG)" ]; then \
		echo "Error: TAG is required. Use: make release TAG=v1.0.0"; \
		exit 1; \
	fi
	@echo "Creating release: $(TAG)"
	@python scripts/release.py create $(TAG)

# List existing releases
list-releases:
	@echo "Existing releases:"
	@python scripts/release.py list

# Setup development environment
setup:
	@echo "Setting up development environment..."
	@chmod +x scripts/*.py
	@echo "Scripts made executable"
	@echo "Setup complete!"

# Quick compile (single pass)
quick:
	@echo "Quick compilation..."
	@python scripts/compile.py --quick

# Force release (ignore uncommitted changes)
force-release:
	@if [ -z "$(TAG)" ]; then \
		echo "Error: TAG is required. Use: make force-release TAG=v1.0.0"; \
		exit 1; \
	fi
	@echo "Force creating release: $(TAG)"
	@python scripts/release.py create $(TAG) --force