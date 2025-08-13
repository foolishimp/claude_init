# Test Dashboard Module

A generic, project-agnostic test dashboard for any project using the Claude Task Management System.

## Features

- 🔍 **Automatic Test Discovery**: Finds all test files across your project
- 📊 **Visual Dashboard**: Beautiful UI to browse and manage tests
- 🏃 **Test Execution**: Run tests directly from the dashboard
- 🔄 **Real-time Updates**: Refresh discovery to find new tests
- 🎯 **Multi-language Support**: Works with JavaScript, TypeScript, Python, and more
- ✅ **Claude Integration**: Checks if Claude Task Management is initialized

## Installation

### As Part of Claude Init

If you installed via `claude_init`, the test dashboard is already included:

```bash
cd test-dashboard-module
npm install
npm start
```

### Standalone Installation

```bash
# Clone or copy this module to your project
cp -r test-dashboard-module /path/to/your/project/

# Install dependencies
cd /path/to/your/project/test-dashboard-module
npm install

# Start the dashboard
npm start
```

## Usage

### Starting the Dashboard

```bash
npm start
# Dashboard available at http://localhost:8000
```

### Discovering Tests

The dashboard automatically discovers tests on first run. To refresh:

```bash
npm run discover
```

### Running Tests

#### Self Tests
```bash
# Check Claude init status
npm run check

# Run browser-based self tests
npm run test:self
# Then open http://localhost:8000/tests/dashboard-self-test.html

# Run Playwright E2E tests
npm run test:e2e
```

## Test Patterns

The dashboard recognizes tests matching these patterns:

- `*.test.*` - Unit tests
- `*.spec.*` - Specification tests
- `test-*` - Test files with prefix
- `test_*` - Python-style test files
- Files in `test/`, `tests/`, `__tests__/` directories

## Supported File Types

- `.js`, `.mjs`, `.cjs` - JavaScript/Node.js
- `.ts`, `.tsx` - TypeScript
- `.py` - Python
- `.html` - Browser-based tests
- More can be added in `scripts/discover-tests.js`

## API Endpoints

The dashboard server provides these endpoints:

- `GET /api/test-registry` - Get all discovered tests
- `GET /api/test-content?path=...` - Get test file content
- `POST /api/run-test` - Execute a test
- `POST /api/refresh` - Refresh test discovery
- `GET /api/claude-status` - Check Claude init status

## Project Structure

```
test-dashboard-module/
├── dashboard.html           # Main dashboard UI
├── server.js               # Express server
├── package.json            # Dependencies
├── scripts/
│   └── discover-tests.js   # Test discovery script
└── tests/
    ├── dashboard-self-test.html  # Browser self-tests
    ├── dashboard-e2e.test.cjs    # Playwright E2E tests
    └── claude-init-check.js      # Claude setup verification
```

## Configuration

### Port Configuration

```bash
PORT=3000 npm start  # Use custom port
```

### Discovery Configuration

Edit `scripts/discover-tests.js` to customize:
- Test patterns
- Ignored directories
- File extensions
- Output format

## Integration with Projects

### For JavaScript/TypeScript Projects

```json
// Add to your package.json
{
  "scripts": {
    "dashboard": "cd test-dashboard-module && npm start",
    "test:discover": "cd test-dashboard-module && npm run discover"
  }
}
```

### For Python Projects

```python
# Add to your Makefile or scripts
dashboard:
    cd test-dashboard-module && npm start

discover:
    cd test-dashboard-module && npm run discover
```

### For Any Project

The dashboard works with any project structure. Just ensure:
1. Test files follow naming conventions
2. The dashboard module is in your project
3. Node.js is installed for running the server

## Troubleshooting

### Tests Not Found

1. Check test file naming matches patterns
2. Run `npm run discover` to refresh
3. Check `test-registry.json` was created
4. Verify paths in the registry

### Server Won't Start

1. Check port 8000 is available
2. Ensure Node.js is installed
3. Run `npm install` to get dependencies
4. Check for error messages in console

### Can't Run Tests

1. Ensure test runners are installed (pytest, jest, etc.)
2. Check file permissions
3. Verify test commands in `server.js`

## Contributing

To extend the dashboard:

1. **Add Test Types**: Edit `discover-tests.js` patterns
2. **Custom Runners**: Modify `server.js` run-test endpoint
3. **UI Features**: Enhance `dashboard.html`
4. **New Endpoints**: Add to `server.js`

## License

MIT - Part of the Claude Task Management System