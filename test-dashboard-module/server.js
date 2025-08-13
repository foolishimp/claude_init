#!/usr/bin/env node

const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);
const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Serve dashboard
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// API: Get test registry
app.get('/api/test-registry', async (req, res) => {
    try {
        const registryPath = path.join(process.cwd(), 'test-registry.json');
        
        // Check if registry exists, if not run discovery
        try {
            await fs.access(registryPath);
        } catch {
            console.log('Test registry not found, running discovery...');
            const discoveryScript = path.join(__dirname, 'scripts', 'discover-tests.js');
            await execAsync(`node "${discoveryScript}"`);
        }
        
        const registry = await fs.readFile(registryPath, 'utf-8');
        res.json(JSON.parse(registry));
    } catch (error) {
        console.error('Error loading test registry:', error);
        res.status(500).json({ error: error.message });
    }
});

// API: Get test content
app.get('/api/test-content', async (req, res) => {
    try {
        const testPath = req.query.path;
        if (!testPath) {
            return res.status(400).send('Path parameter required');
        }
        
        const fullPath = path.join(process.cwd(), testPath);
        const content = await fs.readFile(fullPath, 'utf-8');
        res.send(content);
    } catch (error) {
        console.error('Error reading test file:', error);
        res.status(500).send(error.message);
    }
});

// API: Run test
app.post('/api/run-test', async (req, res) => {
    try {
        const { path: testPath } = req.body;
        if (!testPath) {
            return res.status(400).json({ error: 'Path parameter required' });
        }
        
        const fullPath = path.join(process.cwd(), testPath);
        const ext = path.extname(fullPath);
        let command;
        
        // Determine how to run the test based on extension
        switch (ext) {
            case '.cjs':
                command = `node "${fullPath}"`;
                break;
            case '.js':
            case '.mjs':
                command = `node "${fullPath}"`;
                break;
            case '.py':
                command = `python "${fullPath}"`;
                break;
            case '.html':
                // For HTML tests, we can't run them directly
                return res.json({ 
                    output: `HTML test file. Open in browser: ${testPath}`,
                    type: 'html'
                });
            default:
                // Try to run with node by default
                command = `node "${fullPath}"`;
        }
        
        const { stdout, stderr } = await execAsync(command, { 
            cwd: process.cwd(),
            timeout: 30000 // 30 second timeout
        });
        
        res.json({ 
            output: stdout || stderr,
            success: !stderr || stderr.length === 0
        });
    } catch (error) {
        console.error('Error running test:', error);
        res.status(500).json({ 
            error: error.message,
            output: error.stdout || error.stderr
        });
    }
});

// API: Refresh test discovery
app.post('/api/refresh', async (req, res) => {
    try {
        const discoveryScript = path.join(__dirname, 'scripts', 'discover-tests.js');
        const { stdout } = await execAsync(`node "${discoveryScript}"`, {
            cwd: process.cwd()
        });
        
        res.json({ success: true, message: stdout });
    } catch (error) {
        console.error('Error refreshing tests:', error);
        res.status(500).json({ error: error.message });
    }
});

// API: Check Claude init status
app.get('/api/claude-status', async (req, res) => {
    try {
        const claudeMdPath = path.join(process.cwd(), 'CLAUDE.md');
        const claudeTasksPath = path.join(process.cwd(), 'claude_tasks');
        
        const hasClaude = await fs.access(claudeMdPath).then(() => true).catch(() => false);
        const hasTasks = await fs.access(claudeTasksPath).then(() => true).catch(() => false);
        
        res.json({
            initialized: hasClaude && hasTasks,
            hasCLAUDE_md: hasClaude,
            has_claude_tasks: hasTasks
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════╗
║         Test Dashboard Server          ║
╠════════════════════════════════════════╣
║  Server running at:                    ║
║  http://localhost:${PORT}                 ║
║                                        ║
║  API Endpoints:                        ║
║  GET  /api/test-registry               ║
║  GET  /api/test-content                ║
║  POST /api/run-test                    ║
║  POST /api/refresh                     ║
║  GET  /api/claude-status               ║
╚════════════════════════════════════════╝
    `);
});