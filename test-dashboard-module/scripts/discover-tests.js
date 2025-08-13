#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

// Configuration
const TEST_PATTERNS = {
    // Test file patterns
    files: [
        /\.test\.[jt]sx?$/,
        /\.spec\.[jt]sx?$/,
        /^test[-_]/,
        /_test\.[jt]sx?$/,
        /\.test\.py$/,
        /^test_.*\.py$/,
        /\.test\.cjs$/,
        /\.test\.mjs$/,
        /\.test\.html$/
    ],
    // Test directory patterns
    directories: [
        'test',
        'tests',
        '__tests__',
        'spec',
        'specs',
        'e2e',
        'integration'
    ]
};

const IGNORE_DIRS = [
    'node_modules',
    '.git',
    '.venv',
    'venv',
    'env',
    '__pycache__',
    'dist',
    'build',
    'coverage',
    '.nyc_output',
    '.pytest_cache',
    'vendor',
    'bower_components',
    '.next',
    '.nuxt',
    'out'
];

const VALID_EXTENSIONS = [
    '.js', '.jsx', '.ts', '.tsx',
    '.mjs', '.cjs',
    '.py',
    '.html',
    '.test', '.spec'
];

class TestDiscovery {
    constructor() {
        this.tests = {};
        this.rootDir = process.cwd();
    }

    async discover() {
        console.log(`🔍 Discovering tests in: ${this.rootDir}`);
        await this.scanDirectory(this.rootDir);
        return this.tests;
    }

    async scanDirectory(dir, depth = 0, maxDepth = 10) {
        if (depth > maxDepth) return;

        try {
            const entries = await fs.readdir(dir, { withFileTypes: true });

            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                const relativePath = path.relative(this.rootDir, fullPath);

                if (entry.isDirectory()) {
                    // Skip ignored directories
                    if (IGNORE_DIRS.includes(entry.name)) continue;
                    if (entry.name.startsWith('.')) continue;

                    // Recursively scan
                    await this.scanDirectory(fullPath, depth + 1, maxDepth);
                } else if (entry.isFile()) {
                    // Check if it's a test file
                    if (this.isTestFile(entry.name)) {
                        this.addTest(fullPath, relativePath);
                    }
                }
            }
        } catch (error) {
            if (error.code !== 'EACCES' && error.code !== 'EPERM') {
                console.error(`Error scanning ${dir}:`, error.message);
            }
        }
    }

    isTestFile(filename) {
        // Check extension first
        const ext = path.extname(filename);
        if (!VALID_EXTENSIONS.some(validExt => filename.endsWith(validExt))) {
            return false;
        }

        // Check against test patterns
        return TEST_PATTERNS.files.some(pattern => pattern.test(filename));
    }

    addTest(fullPath, relativePath) {
        const dir = path.dirname(relativePath);
        const filename = path.basename(relativePath);
        const category = this.categorizeTest(dir);

        if (!this.tests[category]) {
            this.tests[category] = [];
        }

        this.tests[category].push({
            file: filename,
            relativePath: relativePath,
            directory: dir,
            fullPath: fullPath
        });
    }

    categorizeTest(dir) {
        const parts = dir.split(path.sep);
        
        // If in root, return 'root'
        if (dir === '.' || dir === '') return 'Root Tests';
        
        // If in a test directory, use parent + test dir
        for (const testDir of TEST_PATTERNS.directories) {
            if (parts.includes(testDir)) {
                const testDirIndex = parts.indexOf(testDir);
                if (testDirIndex > 0) {
                    return parts.slice(0, testDirIndex + 1).join('/');
                }
                return testDir;
            }
        }
        
        // Otherwise use the immediate directory
        if (parts.length > 2) {
            return parts.slice(0, 2).join('/');
        }
        
        return parts.join('/');
    }

    async saveRegistry() {
        const outputPath = path.join(this.rootDir, 'test-registry.json');
        
        // Sort tests within each category
        for (const category in this.tests) {
            this.tests[category].sort((a, b) => a.file.localeCompare(b.file));
        }
        
        await fs.writeFile(
            outputPath,
            JSON.stringify(this.tests, null, 2),
            'utf-8'
        );
        
        return outputPath;
    }

    printSummary() {
        let totalTests = 0;
        const categories = Object.keys(this.tests);
        
        console.log('\n📊 Test Discovery Summary:');
        console.log('─'.repeat(50));
        
        categories.sort().forEach(category => {
            const count = this.tests[category].length;
            totalTests += count;
            console.log(`📁 ${category}: ${count} test${count !== 1 ? 's' : ''}`);
        });
        
        console.log('─'.repeat(50));
        console.log(`✅ Total: ${totalTests} test${totalTests !== 1 ? 's' : ''} in ${categories.length} ${categories.length !== 1 ? 'categories' : 'category'}`);
    }
}

// Main execution
async function main() {
    const discovery = new TestDiscovery();
    
    try {
        await discovery.discover();
        const registryPath = await discovery.saveRegistry();
        discovery.printSummary();
        console.log(`\n💾 Test registry saved to: ${registryPath}`);
    } catch (error) {
        console.error('❌ Error during test discovery:', error);
        process.exit(1);
    }
}

// Run if executed directly
if (require.main === module) {
    main();
}

module.exports = TestDiscovery;