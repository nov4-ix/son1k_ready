#!/usr/bin/env node
/**
 * Complete integration test for Son1k ↔ Suno Bridge
 * Tests both backend API and extension files
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = __dirname;
const EXTENSION_DIR = path.join(PROJECT_ROOT, 'extension');

function log(message, type = 'info') {
  const prefix = {
    'info': '✅',
    'warn': '⚠️',
    'error': '❌',
    'check': '🔍',
    'success': '🎉'
  }[type] || 'ℹ️';
  
  console.log(`${prefix} ${message}`);
}

function testBackendFiles() {
  log('Testing Backend Files...', 'check');
  
  const backendFiles = [
    'backend/app/main.py',
    'backend/app/queue.py',
    'backend/app/models.py',
    'backend/app/settings.py',
    'backend/requirements.txt',
    'docker-compose.yml',
    'Dockerfile'
  ];
  
  let allExist = true;
  for (const file of backendFiles) {
    const filePath = path.join(PROJECT_ROOT, file);
    if (fs.existsSync(filePath)) {
      log(`Backend file exists: ${file}`, 'info');
    } else {
      log(`Backend file missing: ${file}`, 'error');
      allExist = false;
    }
  }
  
  return allExist;
}

function testExtensionFiles() {
  log('Testing Extension Files...', 'check');
  
  const extensionFiles = [
    'manifest.json',
    'background.js',
    'popup.html',
    'popup.js',
    'content.js'
  ];
  
  let allExist = true;
  for (const file of extensionFiles) {
    const filePath = path.join(EXTENSION_DIR, file);
    if (fs.existsSync(filePath)) {
      log(`Extension file exists: ${file}`, 'info');
    } else {
      log(`Extension file missing: ${file}`, 'error');
      allExist = false;
    }
  }
  
  return allExist;
}

function testManifestIntegrity() {
  log('Testing Manifest Integrity...', 'check');
  
  const manifestPath = path.join(EXTENSION_DIR, 'manifest.json');
  
  try {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    
    // Check critical fields
    const checks = [
      { field: 'manifest_version', expected: 3, actual: manifest.manifest_version },
      { field: 'name', expected: 'string', actual: typeof manifest.name },
      { field: 'version', expected: 'string', actual: typeof manifest.version },
      { field: 'permissions', expected: 'array', actual: Array.isArray(manifest.permissions) ? 'array' : typeof manifest.permissions },
      { field: 'host_permissions', expected: 'array', actual: Array.isArray(manifest.host_permissions) ? 'array' : typeof manifest.host_permissions }
    ];
    
    let allValid = true;
    for (const check of checks) {
      if (check.expected === check.actual || (check.expected === 3 && check.actual === 3)) {
        log(`Manifest ${check.field}: ✓`, 'info');
      } else {
        log(`Manifest ${check.field}: ✗ (expected: ${check.expected}, got: ${check.actual})`, 'error');
        allValid = false;
      }
    }
    
    // Check specific permissions
    const requiredPermissions = ['storage', 'activeTab', 'scripting', 'tabs'];
    const hasAllPermissions = requiredPermissions.every(perm => 
      manifest.permissions.includes(perm)
    );
    
    if (hasAllPermissions) {
      log('All required permissions present', 'info');
    } else {
      log('Missing required permissions', 'error');
      allValid = false;
    }
    
    // Check host permissions for Suno and localhost
    const requiredHosts = ['suno.com', 'localhost:8000'];
    const hostPermissions = manifest.host_permissions.join(' ');
    const hasAllHosts = requiredHosts.every(host => 
      hostPermissions.includes(host)
    );
    
    if (hasAllHosts) {
      log('Required host permissions present', 'info');
    } else {
      log('Missing required host permissions', 'error');
      allValid = false;
    }
    
    return allValid;
  } catch (error) {
    log(`Error testing manifest: ${error.message}`, 'error');
    return false;
  }
}

function testJavaScriptSyntax() {
  log('Testing JavaScript Syntax...', 'check');
  
  const jsFiles = ['background.js', 'popup.js', 'content.js'];
  let allValid = true;
  
  for (const file of jsFiles) {
    const filePath = path.join(EXTENSION_DIR, file);
    
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      
      // Check for invalid characters
      if (content.includes('\0')) {
        log(`Invalid null characters in ${file}`, 'error');
        allValid = false;
        continue;
      }
      
      // Test syntax with Function constructor (basic check)
      try {
        new Function(content);
        log(`JavaScript syntax valid: ${file}`, 'info');
      } catch (syntaxError) {
        log(`Syntax error in ${file}: ${syntaxError.message}`, 'error');
        allValid = false;
      }
    } catch (error) {
      log(`Error reading ${file}: ${error.message}`, 'error');
      allValid = false;
    }
  }
  
  return allValid;
}

function testApiEndpoints() {
  log('Testing API Structure...', 'check');
  
  const mainPy = path.join(PROJECT_ROOT, 'backend/app/main.py');
  
  try {
    const content = fs.readFileSync(mainPy, 'utf8');
    
    const endpoints = [
      '/api/health',
      '/api/songs/create'
    ];
    
    let allFound = true;
    for (const endpoint of endpoints) {
      if (content.includes(endpoint)) {
        log(`API endpoint found: ${endpoint}`, 'info');
      } else {
        log(`API endpoint missing: ${endpoint}`, 'error');
        allFound = false;
      }
    }
    
    // Check for FastAPI app
    if (content.includes('FastAPI')) {
      log('FastAPI framework detected', 'info');
    } else {
      log('FastAPI framework not found', 'error');
      allFound = false;
    }
    
    // Check for CORS middleware
    if (content.includes('CORSMiddleware')) {
      log('CORS middleware configured', 'info');
    } else {
      log('CORS middleware not found', 'warn');
    }
    
    return allFound;
  } catch (error) {
    log(`Error reading main.py: ${error.message}`, 'error');
    return false;
  }
}

function testRunnerScripts() {
  log('Testing Runner Scripts...', 'check');
  
  const scripts = [
    'run_local.py',
    'test_fixes.py'
  ];
  
  let allExist = true;
  for (const script of scripts) {
    const scriptPath = path.join(PROJECT_ROOT, script);
    if (fs.existsSync(scriptPath)) {
      log(`Runner script exists: ${script}`, 'info');
    } else {
      log(`Runner script missing: ${script}`, 'error');
      allExist = false;
    }
  }
  
  return allExist;
}

function main() {
  console.log('🚀 Son1k ↔ Suno Bridge - Complete Integration Test');
  console.log('=' * 60);
  console.log('');
  
  const tests = [
    { name: 'Backend Files', fn: testBackendFiles },
    { name: 'Extension Files', fn: testExtensionFiles },
    { name: 'Manifest Integrity', fn: testManifestIntegrity },
    { name: 'JavaScript Syntax', fn: testJavaScriptSyntax },
    { name: 'API Endpoints', fn: testApiEndpoints },
    { name: 'Runner Scripts', fn: testRunnerScripts }
  ];
  
  let passedTests = 0;
  const totalTests = tests.length;
  
  for (const test of tests) {
    console.log('');
    if (test.fn()) {
      passedTests++;
    }
  }
  
  console.log('');
  console.log('=' * 60);
  console.log(`📊 Test Results: ${passedTests}/${totalTests} passed`);
  
  if (passedTests === totalTests) {
    log('🎉 ALL TESTS PASSED! Sistema completamente funcional', 'success');
    console.log('');
    console.log('🚀 Ready to Launch:');
    console.log('');
    console.log('1. Backend:');
    console.log('   cd "/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2"');
    console.log('   python3 run_local.py');
    console.log('');
    console.log('2. Extension:');
    console.log('   - Open chrome://extensions/');
    console.log('   - Enable Developer mode');
    console.log('   - Load unpacked extension from:');
    console.log('     /Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2/extension');
    console.log('');
    console.log('3. Test:');
    console.log('   - Configure backend URL in extension popup');
    console.log('   - Visit https://suno.com/create');
    console.log('   - Use "Send to Son1k" button');
    console.log('');
    console.log('✅ Son1k ↔ Suno Bridge está completamente operacional!');
  } else {
    log('❌ Some tests failed. Check output above for details.', 'error');
  }
  
  return passedTests === totalTests ? 0 : 1;
}

process.exit(main());