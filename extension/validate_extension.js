#!/usr/bin/env node
/**
 * Validation script for Son1k ↔ Suno Bridge Chrome Extension
 * Checks for syntax errors, JSON validity, and common issues
 */

const fs = require('fs');
const path = require('path');

const EXTENSION_DIR = __dirname;

function log(message, type = 'info') {
  const prefix = {
    'info': '✅',
    'warn': '⚠️',
    'error': '❌',
    'check': '🔍'
  }[type] || 'ℹ️';
  
  console.log(`${prefix} ${message}`);
}

function validateJSON(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    JSON.parse(content);
    log(`JSON syntax válido: ${path.basename(filePath)}`, 'info');
    return true;
  } catch (error) {
    log(`JSON inválido en ${path.basename(filePath)}: ${error.message}`, 'error');
    return false;
  }
}

function validateJavaScript(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Check for common syntax issues
    if (content.includes('\0')) {
      log(`Caracteres nulos encontrados en ${path.basename(filePath)}`, 'error');
      return false;
    }
    
    // Check for BOM
    if (content.charCodeAt(0) === 0xFEFF) {
      log(`BOM detectado en ${path.basename(filePath)}`, 'warn');
    }
    
    // Basic syntax validation (this is simplified)
    try {
      new Function(content);
      log(`JavaScript syntax válido: ${path.basename(filePath)}`, 'info');
      return true;
    } catch (syntaxError) {
      log(`Syntax error en ${path.basename(filePath)}: ${syntaxError.message}`, 'error');
      return false;
    }
  } catch (error) {
    log(`Error leyendo ${path.basename(filePath)}: ${error.message}`, 'error');
    return false;
  }
}

function validateHTML(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Basic HTML validation
    if (!content.includes('<!doctype html>') && !content.includes('<!DOCTYPE html>')) {
      log(`DOCTYPE missing en ${path.basename(filePath)}`, 'warn');
    }
    
    // Check for script tags
    const scriptMatches = content.match(/<script[^>]*src="([^"]+)"/g);
    if (scriptMatches) {
      scriptMatches.forEach(match => {
        const src = match.match(/src="([^"]+)"/)[1];
        const scriptPath = path.join(EXTENSION_DIR, src);
        if (!fs.existsSync(scriptPath)) {
          log(`Script referenciado no existe: ${src}`, 'error');
        }
      });
    }
    
    log(`HTML structure válida: ${path.basename(filePath)}`, 'info');
    return true;
  } catch (error) {
    log(`Error validando HTML ${path.basename(filePath)}: ${error.message}`, 'error');
    return false;
  }
}

function validateManifest() {
  const manifestPath = path.join(EXTENSION_DIR, 'manifest.json');
  
  if (!fs.existsSync(manifestPath)) {
    log('manifest.json no encontrado', 'error');
    return false;
  }
  
  if (!validateJSON(manifestPath)) {
    return false;
  }
  
  try {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    
    // Check required fields
    const requiredFields = ['manifest_version', 'name', 'version'];
    for (const field of requiredFields) {
      if (!manifest[field]) {
        log(`Campo requerido faltante en manifest.json: ${field}`, 'error');
        return false;
      }
    }
    
    // Check manifest version
    if (manifest.manifest_version !== 3) {
      log('Esta extensión está configurada para Manifest V3', 'info');
    }
    
    // Check permissions
    if (manifest.permissions) {
      log(`Permisos: ${manifest.permissions.join(', ')}`, 'info');
    }
    
    // Check host permissions
    if (manifest.host_permissions) {
      log(`Host permissions: ${manifest.host_permissions.join(', ')}`, 'info');
    }
    
    // Validate referenced files
    if (manifest.background?.service_worker) {
      const bgPath = path.join(EXTENSION_DIR, manifest.background.service_worker);
      if (!fs.existsSync(bgPath)) {
        log(`Background script no existe: ${manifest.background.service_worker}`, 'error');
        return false;
      }
    }
    
    if (manifest.action?.default_popup) {
      const popupPath = path.join(EXTENSION_DIR, manifest.action.default_popup);
      if (!fs.existsSync(popupPath)) {
        log(`Popup HTML no existe: ${manifest.action.default_popup}`, 'error');
        return false;
      }
    }
    
    if (manifest.content_scripts) {
      for (const script of manifest.content_scripts) {
        for (const jsFile of script.js || []) {
          const jsPath = path.join(EXTENSION_DIR, jsFile);
          if (!fs.existsSync(jsPath)) {
            log(`Content script no existe: ${jsFile}`, 'error');
            return false;
          }
        }
      }
    }
    
    log('Manifest.json validado correctamente', 'info');
    return true;
  } catch (error) {
    log(`Error validando manifest: ${error.message}`, 'error');
    return false;
  }
}

function checkFileEncoding(filePath) {
  try {
    const buffer = fs.readFileSync(filePath);
    const content = buffer.toString('utf8');
    
    // Check for BOM
    if (buffer[0] === 0xEF && buffer[1] === 0xBB && buffer[2] === 0xBF) {
      log(`BOM UTF-8 detectado en ${path.basename(filePath)} (recomendado sin BOM)`, 'warn');
    }
    
    // Check for non-printable characters (except normal whitespace)
    const nonPrintable = content.match(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]/g);
    if (nonPrintable && nonPrintable.length > 0) {
      log(`Caracteres no imprimibles en ${path.basename(filePath)}: ${nonPrintable.length} encontrados`, 'warn');
    }
    
    return true;
  } catch (error) {
    log(`Error checking encoding ${path.basename(filePath)}: ${error.message}`, 'error');
    return false;
  }
}

function main() {
  console.log('🚀 Validando extensión Son1k ↔ Suno Bridge\n');
  
  let allValid = true;
  
  // Check all files exist
  const requiredFiles = ['manifest.json', 'background.js', 'popup.html', 'popup.js', 'content.js'];
  
  log('Verificando archivos requeridos...', 'check');
  for (const file of requiredFiles) {
    const filePath = path.join(EXTENSION_DIR, file);
    if (fs.existsSync(filePath)) {
      log(`Archivo encontrado: ${file}`, 'info');
    } else {
      log(`Archivo faltante: ${file}`, 'error');
      allValid = false;
    }
  }
  
  console.log('');
  
  // Validate manifest
  log('Validando manifest.json...', 'check');
  if (!validateManifest()) {
    allValid = false;
  }
  
  console.log('');
  
  // Validate JavaScript files
  log('Validando archivos JavaScript...', 'check');
  const jsFiles = ['background.js', 'popup.js', 'content.js'];
  for (const file of jsFiles) {
    const filePath = path.join(EXTENSION_DIR, file);
    if (fs.existsSync(filePath)) {
      if (!validateJavaScript(filePath)) {
        allValid = false;
      }
      checkFileEncoding(filePath);
    }
  }
  
  console.log('');
  
  // Validate HTML files
  log('Validando archivos HTML...', 'check');
  const htmlFiles = ['popup.html'];
  for (const file of htmlFiles) {
    const filePath = path.join(EXTENSION_DIR, file);
    if (fs.existsSync(filePath)) {
      if (!validateHTML(filePath)) {
        allValid = false;
      }
      checkFileEncoding(filePath);
    }
  }
  
  console.log('');
  console.log('=' * 50);
  
  if (allValid) {
    log('🎉 VALIDACIÓN EXITOSA - La extensión debería cargar sin errores', 'info');
    console.log('\n📝 Próximos pasos:');
    console.log('1. Abrir Chrome y ir a chrome://extensions/');
    console.log('2. Activar "Modo de desarrollador"');
    console.log('3. Hacer clic en "Cargar extensión sin empaquetar"');
    console.log('4. Seleccionar la carpeta: ' + EXTENSION_DIR);
    console.log('5. Configurar backend URL en el popup');
    console.log('6. Probar en https://suno.com/create');
  } else {
    log('❌ VALIDACIÓN FALLIDA - Corrige los errores antes de cargar la extensión', 'error');
  }
  
  return allValid ? 0 : 1;
}

process.exit(main());