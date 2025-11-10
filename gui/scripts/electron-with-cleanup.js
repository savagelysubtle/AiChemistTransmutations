const { spawn } = require('child_process');
const path = require('path');

// Get the Electron executable path
const electronPath = require('electron');

// Get the GUI directory (parent of scripts directory)
const guiDir = path.join(__dirname, '..');

// Set NODE_ENV to development for dev mode
process.env.NODE_ENV = 'development';

console.log('🚀 Starting Electron in DEVELOPMENT mode...');
console.log(`📁 Project directory: ${guiDir}`);
console.log(`🔧 NODE_ENV: ${process.env.NODE_ENV}\n`);

// Spawn Electron process - pass only the GUI directory, no extra args
const electron = spawn(electronPath, [guiDir], {
  stdio: 'inherit',
  shell: false,  // Don't use shell to prevent double launching
  windowsHide: false,
  detached: false,  // Keep attached so we can track it
  env: {
    ...process.env,  // Pass all environment variables including NODE_ENV
    NODE_ENV: 'development'  // Explicitly set to development
  }
});

let isExiting = false;

// Handle Electron exit
electron.on('exit', (code, signal) => {
  if (isExiting) return;
  isExiting = true;

  console.log(`\n🛑 Electron process exited (code: ${code || 0}, signal: ${signal || 'none'})`);
  console.log('🔄 This will trigger concurrently to stop all watchers...\n');

  // Exit this process, which will trigger concurrently's --kill-others to stop other processes
  process.exit(code || 0);
});

// Handle errors
electron.on('error', (err) => {
  if (isExiting) return;
  isExiting = true;

  console.error('❌ Failed to start Electron:', err);
  process.exit(1);
});

// Handle Ctrl+C (SIGINT)
process.on('SIGINT', () => {
  if (isExiting) return;
  isExiting = true;

  console.log('\n🛑 Received SIGINT, shutting down gracefully...');
  if (electron.pid && !electron.killed) {
    try {
      electron.kill('SIGINT');
    } catch (e) {
      // Process might already be dead
    }
  }

  // Give Electron a moment to close, then exit
  setTimeout(() => {
    process.exit(0);
  }, 500);
});

// Handle SIGTERM
process.on('SIGTERM', () => {
  if (isExiting) return;
  isExiting = true;

  console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
  if (electron.pid && !electron.killed) {
    try {
      electron.kill('SIGTERM');
    } catch (e) {
      // Process might already be dead
    }
  }

  setTimeout(() => {
    process.exit(0);
  }, 500);
});

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  if (isExiting) return;
  isExiting = true;

  console.error('❌ Uncaught exception:', err);
  if (electron.pid && !electron.killed) {
    try {
      electron.kill();
    } catch (e) {
      // Process might already be dead
    }
  }
  process.exit(1);
});

// Keep process alive until Electron exits
electron.on('close', (code, signal) => {
  if (isExiting) return;
  isExiting = true;

  console.log(`\n🛑 Electron window closed (code: ${code || 0}, signal: ${signal || 'none'})`);
  console.log('🔄 Stopping all watchers...\n');
  process.exit(code || 0);
});

// Prevent Electron from spawning child processes that might duplicate
process.on('exit', () => {
  if (electron.pid && !electron.killed) {
    try {
      electron.kill();
    } catch (e) {
      // Ignore errors on exit
    }
  }
});
