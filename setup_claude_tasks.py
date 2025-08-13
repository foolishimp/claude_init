#!/usr/bin/env python3
"""
Claude Task Management System Setup Script

This script installs the Claude task management system into any project,
making it "Claude-aware" with proper development methodology.

Usage:
    python setup_claude_tasks.py [options]
    
Options:
    --source PATH/URL   Source for claude_tasks (git repo, GitHub URL, or local path)
    --target PATH       Target directory for installation (default: current directory)
    --force            Overwrite existing files
    --no-git           Don't add .gitignore entries
"""

import os
import sys
import shutil
import argparse
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import json

# Embedded templates for when no source is provided
EMBEDDED_TEMPLATES = {
    "QUICK_REFERENCE.md": """# Task Management Quick Reference

## 🚀 Session Start Checklist
```bash
# 1. Check current state
git status
cat claude_tasks/active/ACTIVE_TASKS.md
npm test

# 2. Review core docs
cat claude_tasks/PRINCIPLES_QUICK_CARD.md
cat claude_tasks/DEVELOPMENT_PROCESS.md
```

## 🔴 Start a New Task (TDD Process)
1. **CHECK**: Current state and active tasks
2. **PLAN**: Update ACTIVE_TASKS.md to "In Progress"
3. **RED**: Write failing tests FIRST
4. **GREEN**: Write minimal code to pass tests
5. **REFACTOR**: Improve code quality

## ✅ Complete a Task
1. **DOCUMENT**: Create finished file
2. **COMMIT**: With descriptive message
3. **ARCHIVE**: Move to finished/
""",
    "PRINCIPLES_QUICK_CARD.md": """# Development Principles Quick Card

## The 7 Core Principles

1. **Test Driven Development** - No code without tests
2. **Fail Fast & Root Cause** - No workarounds, fix causes
3. **Modular & Maintainable** - Single responsibility
4. **Reuse Before Build** - Check existing code first
5. **Open Source First** - Suggest alternatives
6. **No Legacy Baggage** - Clean slate, no tech debt
7. **Perfectionist Excellence** - Best of breed only

## TDD Workflow
RED → GREEN → REFACTOR

## Code Quality Standards
- >80% test coverage
- Clear naming conventions
- Documented decisions
- No commented-out code
""",
    "ACTIVE_TASKS.md": """# Active Tasks

## Current Sprint
*Last Updated: [DATE]*

---

## Task Queue

### Task 1: [Example Task]
- **ID**: 1
- **Priority**: High/Medium/Low
- **Status**: Not Started
- **Estimated Time**: X hours
- **Dependencies**: None
- **Description**: [Clear description of what needs to be done]
- **Acceptance Criteria**:
  - [ ] Criterion 1
  - [ ] Criterion 2
  - [ ] Tests pass

---

## Completed Tasks
*Move to finished/ folder when complete*

## Notes
- Follow TDD: Write tests first
- Update status as you work
- Document in finished/ when complete
"""
}

class ClaudeTasksSetup:
    """Setup Claude task management system in a project."""
    
    def __init__(self, source: Optional[str] = None, target: str = ".", 
                 force: bool = False, no_git: bool = False):
        self.source = source
        self.target = Path(target).resolve()
        self.force = force
        self.no_git = no_git
        self.claude_tasks_dir = self.target / "claude_tasks"
        self.claude_md_path = self.target / "CLAUDE.md"
        
    def run(self):
        """Execute the setup process."""
        print("🚀 Claude Task Management System Setup")
        print(f"📁 Target directory: {self.target}")
        
        # Create claude_tasks directory
        self._create_directory_structure()
        
        # Copy or create files
        if self.source:
            self._copy_from_source()
        else:
            self._create_from_templates()
        
        # Handle CLAUDE.md
        self._handle_claude_md()
        
        # Add .gitignore entries
        if not self.no_git:
            self._update_gitignore()
        
        print("\n✅ Setup complete!")
        self._print_next_steps()
    
    def _create_directory_structure(self):
        """Create the claude_tasks directory structure."""
        directories = [
            self.claude_tasks_dir,
            self.claude_tasks_dir / "active",
            self.claude_tasks_dir / "finished",
        ]
        
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created: {directory.relative_to(self.target)}")
    
    def _copy_from_source(self):
        """Copy files from source repository or directory."""
        temp_dir = None
        
        try:
            # Determine source type and get path
            if self.source.startswith(("http://", "https://", "git@")):
                # Clone from git
                temp_dir = tempfile.mkdtemp()
                print(f"📥 Cloning from: {self.source}")
                subprocess.run(
                    ["git", "clone", self.source, temp_dir],
                    check=True,
                    capture_output=True
                )
                source_path = Path(temp_dir) / "claude_tasks"
            else:
                # Local path
                source_path = Path(self.source)
                if not source_path.exists():
                    raise FileNotFoundError(f"Source not found: {source_path}")
                
                # Check if source has claude_tasks subdirectory
                if (source_path / "claude_tasks").exists():
                    source_path = source_path / "claude_tasks"
            
            # Copy files
            self._copy_files(source_path)
            
        finally:
            # Clean up temp directory
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
    
    def _copy_files(self, source_path: Path):
        """Copy files from source to target."""
        if not source_path.exists():
            print(f"⚠️  Source claude_tasks not found, using embedded templates")
            self._create_from_templates()
            return
        
        # Files to copy
        files_to_copy = [
            "QUICK_REFERENCE.md",
            "PRINCIPLES_QUICK_CARD.md",
            "DEVELOPMENT_PROCESS.md",
            "PAIR_PROGRAMMING_WITH_CLAUDE.md",
            "UNIFIED_PRINCIPLES.md",
            "SESSION_STARTER.md",
            "TASK_TEMPLATE.md",
        ]
        
        for file_name in files_to_copy:
            source_file = source_path / file_name
            target_file = self.claude_tasks_dir / file_name
            
            if source_file.exists():
                if target_file.exists() and not self.force:
                    print(f"⏭️  Skipping existing: {file_name}")
                else:
                    shutil.copy2(source_file, target_file)
                    print(f"📄 Copied: {file_name}")
        
        # Copy active tasks if exists
        active_tasks = source_path / "active" / "ACTIVE_TASKS.md"
        if active_tasks.exists():
            target_active = self.claude_tasks_dir / "active" / "ACTIVE_TASKS.md"
            if not target_active.exists() or self.force:
                shutil.copy2(active_tasks, target_active)
                print(f"📄 Copied: active/ACTIVE_TASKS.md")
    
    def _create_from_templates(self):
        """Create files from embedded templates."""
        print("📝 Creating from embedded templates...")
        
        for file_name, content in EMBEDDED_TEMPLATES.items():
            if file_name == "ACTIVE_TASKS.md":
                target_file = self.claude_tasks_dir / "active" / file_name
            else:
                target_file = self.claude_tasks_dir / file_name
            
            if target_file.exists() and not self.force:
                print(f"⏭️  Skipping existing: {file_name}")
            else:
                # Update date in content
                content = content.replace("[DATE]", datetime.now().strftime("%Y-%m-%d"))
                target_file.write_text(content)
                print(f"📄 Created: {file_name}")
    
    def _handle_claude_md(self):
        """Create or update CLAUDE.md file."""
        if self.claude_md_path.exists():
            self._update_existing_claude_md()
        else:
            self._create_new_claude_md()
    
    def _update_existing_claude_md(self):
        """Prepend task system reference to existing CLAUDE.md."""
        print(f"📝 Updating existing CLAUDE.md...")
        
        existing_content = self.claude_md_path.read_text()
        
        # Check if already has task system reference
        if "claude_tasks" in existing_content:
            print("✓ CLAUDE.md already references task system")
            return
        
        # Prepend reference section
        reference_section = """# CLAUDE.md

## 📋 Claude Development Process
This project now uses the Claude Task Management System for AI-assisted development.

### Key Documents
- `claude_tasks/QUICK_REFERENCE.md` - Quick commands and workflow
- `claude_tasks/DEVELOPMENT_PROCESS.md` - Full TDD methodology
- `claude_tasks/PRINCIPLES_QUICK_CARD.md` - Core development principles
- `claude_tasks/active/ACTIVE_TASKS.md` - Current task tracking

---

""" 
        
        # Remove existing header if present
        if existing_content.startswith("# CLAUDE.md"):
            existing_content = existing_content[existing_content.find("\n")+1:]
        
        new_content = reference_section + existing_content
        
        if not self.force:
            # Backup existing file
            backup_path = self.claude_md_path.with_suffix(".md.backup")
            shutil.copy2(self.claude_md_path, backup_path)
            print(f"📋 Backed up to: {backup_path.name}")
        
        self.claude_md_path.write_text(new_content)
        print("✅ Updated CLAUDE.md with task system reference")
    
    def _create_new_claude_md(self):
        """Create new CLAUDE.md from template."""
        print("📝 Creating new CLAUDE.md...")
        
        # Get template from source if available
        template_path = None
        if self.source:
            if self.source.startswith(("http://", "https://", "git@")):
                # Would need to clone again, skip for now
                pass
            else:
                source_path = Path(self.source)
                if (source_path / "CLAUDE.md").exists():
                    template_path = source_path / "CLAUDE.md"
        
        if template_path and template_path.exists():
            shutil.copy2(template_path, self.claude_md_path)
        else:
            # Use embedded template
            content = self._get_claude_md_template()
            self.claude_md_path.write_text(content)
        
        print("✅ Created CLAUDE.md")
    
    def _get_claude_md_template(self) -> str:
        """Get the CLAUDE.md template."""
        return """# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Development Process

This project follows the Claude Task Management System. See `claude_tasks/` for:
- `QUICK_REFERENCE.md` - Quick commands and TDD workflow
- `DEVELOPMENT_PROCESS.md` - Complete methodology
- `PRINCIPLES_QUICK_CARD.md` - Core principles
- `active/ACTIVE_TASKS.md` - Current tasks

## Repository Overview

[TODO: Add project description]

## Project Structure

```
[TODO: Document structure]
```

## Common Development Commands

### Testing
```bash
# Run tests
npm test  # or appropriate command

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

## Working with this Codebase

Follow TDD: RED → GREEN → REFACTOR

See `claude_tasks/` for detailed methodology.
"""
    
    def _update_gitignore(self):
        """Add appropriate .gitignore entries."""
        gitignore_path = self.target / ".gitignore"
        
        entries_to_add = [
            "\n# Claude task management",
            "*.backup",
            "CLAUDE.md.backup",
        ]
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            
            # Check if already has claude entries
            if "claude_tasks" in content:
                print("✓ .gitignore already configured")
                return
            
            # Append entries
            if not content.endswith("\n"):
                content += "\n"
            
            content += "\n".join(entries_to_add) + "\n"
            gitignore_path.write_text(content)
            print("📝 Updated .gitignore")
        else:
            # Create new .gitignore
            content = "\n".join(entries_to_add) + "\n"
            gitignore_path.write_text(content)
            print("📝 Created .gitignore")
    
    def _print_next_steps(self):
        """Print next steps for the user."""
        print("\n📚 Next Steps:")
        print("1. Review claude_tasks/QUICK_REFERENCE.md for workflow")
        print("2. Read claude_tasks/PRINCIPLES_QUICK_CARD.md for principles")
        print("3. Add your first task to claude_tasks/active/ACTIVE_TASKS.md")
        print("4. Customize CLAUDE.md with project-specific information")
        print("5. Commit the changes: git add . && git commit -m 'Add Claude task management'")
        print("\n🎯 Start coding with: cat claude_tasks/SESSION_STARTER.md")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Setup Claude Task Management System in your project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use embedded templates in current directory
  python setup_claude_tasks.py
  
  # From GitHub repository
  python setup_claude_tasks.py --source https://github.com/user/claude_init
  
  # From local directory
  python setup_claude_tasks.py --source /path/to/claude_tasks --target ./myproject
  
  # Force overwrite existing files
  python setup_claude_tasks.py --force
        """
    )
    
    parser.add_argument(
        "--source",
        help="Source for claude_tasks (git repo URL or local path)",
        default=None
    )
    
    parser.add_argument(
        "--target",
        help="Target directory for installation (default: current directory)",
        default="."
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files"
    )
    
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Don't add .gitignore entries"
    )
    
    args = parser.parse_args()
    
    # Run setup
    setup = ClaudeTasksSetup(
        source=args.source,
        target=args.target,
        force=args.force,
        no_git=args.no_git
    )
    
    try:
        setup.run()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()