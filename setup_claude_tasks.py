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
        
        # Check what already exists
        claude_tasks_exists = self.claude_tasks_dir.exists()
        test_dashboard_exists = (self.target / "test-dashboard-module").exists()
        claude_md_exists = self.claude_md_path.exists()
        
        print(f"\n📋 Current state:")
        print(f"   claude_tasks/: {'✅ exists' if claude_tasks_exists else '❌ missing'}")
        print(f"   test-dashboard-module/: {'✅ exists' if test_dashboard_exists else '❌ missing'}")
        print(f"   CLAUDE.md: {'✅ exists' if claude_md_exists else '❌ missing'}")
        
        # Install claude_tasks if missing or force flag is set
        if not claude_tasks_exists or self.force:
            if claude_tasks_exists and self.force:
                print(f"\n🔄 Reinstalling claude_tasks (--force flag)")
            else:
                print(f"\n📦 Installing claude_tasks...")
            
            # Create claude_tasks directory
            self._create_directory_structure()
            
            # Copy or create files
            if self.source:
                self._copy_from_source()
            else:
                self._create_from_templates()
        else:
            print(f"\n⏭️  Skipping claude_tasks (already exists)")
        
        # Handle CLAUDE.md if missing or force flag is set
        if not claude_md_exists or self.force:
            if claude_md_exists and self.force:
                print(f"\n🔄 Updating CLAUDE.md (--force flag)")
            else:
                print(f"\n📝 Creating CLAUDE.md...")
            self._handle_claude_md()
        else:
            print(f"\n⏭️  Skipping CLAUDE.md (already exists)")
        
        # Install test dashboard if missing or force flag is set
        if not test_dashboard_exists or self.force:
            if test_dashboard_exists and self.force:
                print(f"\n🔄 Reinstalling test-dashboard-module (--force flag)")
            else:
                print(f"\n📊 Installing test-dashboard-module...")
            self._install_test_dashboard()
        else:
            print(f"\n⏭️  Skipping test-dashboard-module (already exists)")
        
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
                    ["git", "clone", "--depth", "1", self.source, temp_dir],
                    check=True,
                    capture_output=True
                )
                # Remove .git folder to avoid confusion
                git_dir = Path(temp_dir) / ".git"
                if git_dir.exists():
                    shutil.rmtree(git_dir)
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
    
    def _install_test_dashboard(self):
        """Install test dashboard module."""
        test_dashboard_dir = self.target / "test-dashboard-module"
        
        # Determine source for test dashboard
        source_dashboard = None
        if self.source:
            if self.source.startswith(("http://", "https://", "git@")):
                # For git sources, we'd need to clone again - for now, use embedded files
                pass
            else:
                source_path = Path(self.source)
                potential_dashboard = source_path / "test-dashboard-module"
                if potential_dashboard.exists():
                    source_dashboard = potential_dashboard
        
        if source_dashboard:
            # Copy existing dashboard
            self._copy_test_dashboard(source_dashboard, test_dashboard_dir)
        else:
            # Create minimal dashboard from embedded template
            self._create_embedded_dashboard(test_dashboard_dir)
        
        # Install Node.js dependencies
        self._install_node_dependencies(test_dashboard_dir)
    
    def _copy_test_dashboard(self, source_dir: Path, target_dir: Path):
        """Copy test dashboard from source."""
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # Copy entire directory
        shutil.copytree(source_dir, target_dir)
        
        # Remove node_modules and package-lock.json if they exist
        for item in ["node_modules", "package-lock.json"]:
            item_path = target_dir / item
            if item_path.exists():
                if item_path.is_dir():
                    shutil.rmtree(item_path)
                else:
                    item_path.unlink()
        
        print(f"📊 Copied test dashboard to: {target_dir.relative_to(self.target)}")
    
    def _create_embedded_dashboard(self, target_dir: Path):
        """Create basic test dashboard from embedded template."""
        target_dir.mkdir(exist_ok=True)
        
        # Create package.json
        package_json = {
            "name": f"{self.target.name}-test-dashboard",
            "version": "1.0.0",
            "description": "Test dashboard for project test management",
            "main": "server.js",
            "scripts": {
                "start": "node server.js",
                "discover": "node scripts/discover-tests.js"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5"
            }
        }
        
        with open(target_dir / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
        
        # Create basic server.js (minimal version)
        server_js = '''#!/usr/bin/env node

const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8085;

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

app.get('/', (req, res) => {
    res.send(`
        <h1>Test Dashboard</h1>
        <p>Basic test dashboard installed with Claude Task Management System</p>
        <p>To enhance this dashboard:</p>
        <ol>
            <li>Run: <code>npm install</code></li>
            <li>Copy full dashboard from claude_init repository</li>
            <li>Run: <code>npm start</code></li>
        </ol>
    `);
});

app.listen(PORT, () => {
    console.log(`Test Dashboard running on http://localhost:${PORT}`);
});
'''
        
        (target_dir / "server.js").write_text(server_js)
        
        # Create scripts directory and basic discover script
        scripts_dir = target_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        discover_script = '''#!/usr/bin/env node

console.log("Basic test discovery script");
console.log("To get full test discovery, copy from claude_init repository");
'''
        
        (scripts_dir / "discover-tests.js").write_text(discover_script)
        
        print(f"📊 Created basic test dashboard at: {target_dir.relative_to(self.target)}")
        print("   For full functionality, copy complete dashboard from claude_init")
    
    def _install_node_dependencies(self, dashboard_dir: Path):
        """Install Node.js dependencies for the test dashboard."""
        package_json = dashboard_dir / "package.json"
        if not package_json.exists():
            print("⚠️  No package.json found, skipping npm install")
            return
        
        try:
            print("📦 Installing Node.js dependencies...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=dashboard_dir,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Node.js dependencies installed successfully")
            else:
                print(f"⚠️  npm install completed with warnings")
                if result.stderr:
                    print(f"   stderr: {result.stderr[:200]}...")
                    
        except subprocess.TimeoutExpired:
            print("⚠️  npm install timed out, but dashboard was created")
        except FileNotFoundError:
            print("⚠️  npm not found - install Node.js to use test dashboard")
        except Exception as e:
            print(f"⚠️  Error installing dependencies: {e}")
            print("   You can run 'npm install' manually in the test-dashboard-module directory")

    def _update_gitignore(self):
        """Add appropriate .gitignore entries."""
        gitignore_path = self.target / ".gitignore"
        
        entries_to_add = [
            "\n# Claude task management",
            "*.backup",
            "CLAUDE.md.backup",
            "\n# Test Dashboard Module",
            "test-dashboard-module/node_modules/",
            "test-dashboard-module/package-lock.json",
            "test-dashboard-module/test-registry.json",
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
        claude_tasks_exists = self.claude_tasks_dir.exists()
        test_dashboard_exists = (self.target / "test-dashboard-module").exists()
        claude_md_exists = self.claude_md_path.exists()
        
        print("\n📚 Next Steps:")
        
        step_num = 1
        
        if claude_tasks_exists:
            print(f"{step_num}. Review claude_tasks/QUICK_REFERENCE.md for workflow")
            step_num += 1
            print(f"{step_num}. Read claude_tasks/PRINCIPLES_QUICK_CARD.md for principles")
            step_num += 1
            print(f"{step_num}. Add your first task to claude_tasks/active/ACTIVE_TASKS.md")
            step_num += 1
        
        if claude_md_exists:
            print(f"{step_num}. Customize CLAUDE.md with project-specific information")
            step_num += 1
        
        # Only suggest git commit if something was actually installed
        if claude_tasks_exists or test_dashboard_exists or claude_md_exists:
            print(f"{step_num}. Commit the changes: git add . && git commit -m 'Add Claude components'")
            step_num += 1
        
        # Test dashboard instructions
        if test_dashboard_exists:
            print(f"\n📊 Test Dashboard:")
            print(f"{step_num}. Start test dashboard: cd test-dashboard-module && npm start")
            step_num += 1
            print(f"{step_num}. Open http://localhost:8085 to manage tests")
            step_num += 1
            print(f"{step_num}. Add project directories in the dashboard to scan multiple projects")
        
        if claude_tasks_exists:
            print("\n🎯 Start coding with: cat claude_tasks/SESSION_STARTER.md")
        elif test_dashboard_exists:
            print("\n🎯 Manage tests with: cd test-dashboard-module && npm start")


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