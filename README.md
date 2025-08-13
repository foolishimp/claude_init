# Claude Task Management System

A structured methodology for AI-assisted software development using Claude Code (claude.ai/code).

## 🚀 Quick Start

Install the Claude task management system in any project:

```bash
# Clone this repository
git clone https://github.com/foolishimp/claude_init.git

# Run setup in your project
python claude_init/setup_claude_tasks.py

# Or install from GitHub directly
curl -sSL https://raw.githubusercontent.com/foolishimp/claude_init/main/setup_claude_tasks.py | python3
```

## 📋 What This Provides

The Claude Task Management System establishes:

1. **Test-Driven Development (TDD) workflow**
2. **Structured task tracking and documentation**
3. **Clear development principles**
4. **Pair programming patterns with AI**
5. **Session management tools**

## 🏗️ Structure Created

```
your-project/
├── CLAUDE.md                    # Project guidance for Claude
└── claude_tasks/
    ├── QUICK_REFERENCE.md       # Commands and workflow
    ├── PRINCIPLES_QUICK_CARD.md # Core principles
    ├── DEVELOPMENT_PROCESS.md   # TDD methodology
    ├── TASK_TEMPLATE.md         # Template for tasks
    ├── active/
    │   └── ACTIVE_TASKS.md      # Current tasks
    └── finished/                 # Completed tasks archive (tracked in git)
```

## 🎯 Core Principles

1. **Test Driven Development** - Write tests first
2. **Fail Fast & Root Cause** - Fix problems at source
3. **Modular & Maintainable** - Single responsibility
4. **Reuse Before Build** - Check existing code first
5. **Open Source First** - Suggest alternatives
6. **No Legacy Baggage** - Clean slate approach
7. **Perfectionist Excellence** - Best of breed only

## 💻 Usage

### Basic Installation

```bash
# In your project directory
python setup_claude_tasks.py
```

### From This Repository

```bash
python setup_claude_tasks.py --source https://github.com/foolishimp/claude_init
```

### From Local Clone

```bash
python setup_claude_tasks.py --source /path/to/claude_init --target ./myproject
```

### Options

- `--source PATH/URL` - Source for templates (default: embedded)
- `--target PATH` - Target directory (default: current)
- `--force` - Overwrite existing files
- `--no-git` - Skip .gitignore updates

## 📚 Workflow

1. **Start Session**: Review `claude_tasks/SESSION_STARTER.md`
2. **Check Tasks**: Read `claude_tasks/active/ACTIVE_TASKS.md`
3. **Follow TDD**: RED → GREEN → REFACTOR
4. **Document**: Move completed tasks to `finished/`
5. **Commit**: Use descriptive messages

## 🤝 Working with Claude

When Claude Code works on your project, it will:

1. Check `CLAUDE.md` for project context
2. Follow principles in `claude_tasks/`
3. Use TDD methodology
4. Track tasks systematically
5. Document decisions

## 📖 Documentation

### For Developers

- Review `QUICK_REFERENCE.md` for commands
- Follow `DEVELOPMENT_PROCESS.md` for TDD
- Check `PRINCIPLES_QUICK_CARD.md` for standards

### For Claude

The system makes your project "Claude-aware" by:
- Providing clear development methodology
- Establishing consistent patterns
- Defining quality standards
- Creating task tracking structure

## 🔧 Customization

After installation:

1. Edit `CLAUDE.md` with project-specific details
2. Add initial tasks to `active/ACTIVE_TASKS.md`
3. Customize templates as needed
4. Commit changes to your repository

## 📦 Requirements

- Python 3.6+
- Git (for repository sources)
- Target project (any language)

## 📝 License

MIT License - Use freely in your projects

## 🙏 Contributing

Contributions welcome! The methodology is designed to be language-agnostic and universally applicable.

---

*Make your projects Claude-aware with structured, test-driven development.*