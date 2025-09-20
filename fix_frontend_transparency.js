/**
 * 🎯 SOLUCIÓN GARANTIZADA: Transparencia Total del Frontend
 * Este script se ejecuta inmediatamente y asegura transparencia completa
 */

(function() {
    'use strict';
    
    console.log('🎯 INICIANDO SOLUCIÓN DE TRANSPARENCIA GARANTIZADA');
    
    // 1. INTERCEPTAR Y CORREGIR TODAS LAS RESPUESTAS
    const originalFetch = window.fetch;
    window.fetch = async function(url, options) {
        console.log('🔍 Interceptando fetch:', url);
        
        // Hacer la request original
        const response = await originalFetch(url, options);
        
        // Si es request de música, interceptar y corregir la respuesta
        if (url.includes('/api/music/') || url.includes('generate')) {
            console.log('🎵 Interceptando respuesta de música');
            
            const originalJson = response.json;
            response.json = async function() {
                const data = await originalJson.call(this);
                console.log('📥 Respuesta original:', data);
                
                // CORREGIR RESPUESTA PARA SER TRANSPARENTE
                const correctedData = makeResponseTransparent(data);
                console.log('✅ Respuesta corregida:', correctedData);
                
                return correctedData;
            };
        }
        
        return response;
    };
    
    // 2. FUNCIÓN PARA HACER RESPUESTA TRANSPARENTE
    function makeResponseTransparent(data) {
        if (!data) return data;
        
        // Crear copia para no modificar original
        const transparent = JSON.parse(JSON.stringify(data));
        
        // CORREGIR JOB ID
        if (transparent.job_id) {
            transparent.job_id = transparent.job_id.replace(/suno/gi, 'son1k');
            console.log('🔧 Job ID corregido:', transparent.job_id);
        }
        
        // CORREGIR TRACKS
        if (transparent.tracks && Array.isArray(transparent.tracks)) {
            transparent.tracks = transparent.tracks.map((track, index) => {
                const correctedTrack = { ...track };
                
                // Generar nombre dinámico basado en lyrics
                if (track.lyrics_preview || data.lyrics) {
                    const lyrics = track.lyrics_preview || data.lyrics || '';
                    correctedTrack.title = generateDynamicName(lyrics, index);
                    correctedTrack.filename = `${correctedTrack.title.replace(/[^a-zA-Z0-9]/g, '_')}.mp3`;
                }
                
                // Asegurar provider transparente
                correctedTrack.provider = 'Son1k';
                
                // Corregir cualquier referencia a suno
                if (correctedTrack.job_id) {
                    correctedTrack.job_id = correctedTrack.job_id.replace(/suno/gi, 'son1k');
                }
                
                console.log(`✨ Track ${index + 1} corregido:`, correctedTrack.title);
                return correctedTrack;
            });
        }
        
        // LIMPIAR CUALQUIER REFERENCIA A SUNO EN TODO EL OBJETO
        cleanSunoReferences(transparent);
        
        return transparent;
    }
    
    // 3. GENERAR NOMBRE DINÁMICO DESDE LYRICS
    function generateDynamicName(lyrics, index = 0) {
        if (!lyrics || !lyrics.trim()) {
            return `Instrumental_${Date.now()}`;
        }
        
        // Tomar primera línea significativa
        const lines = lyrics.split('\n');
        let firstLine = '';
        
        for (const line of lines) {
            const cleaned = line.trim();
            if (cleaned.length > 3 && !cleaned.match(/^[^\w]*$/)) {
                firstLine = cleaned;
                break;
            }
        }
        
        if (!firstLine) {
            // Usar primeras palabras
            const words = lyrics.trim().split(/\s+/).slice(0, 4);
            firstLine = words.join(' ') || 'Sin Título';
        }
        
        // Limpiar y capitalizar
        let cleanName = firstLine
            .replace(/[<>:"/\\|?*]/g, '')
            .replace(/\s+/g, ' ')
            .trim();
        
        // Capitalizar cada palabra
        cleanName = cleanName.split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
        
        // Limitar longitud
        if (cleanName.length > 50) {
            cleanName = cleanName.substring(0, 47) + '...';
        }
        
        // Agregar variación si hay múltiples tracks
        if (index > 0) {
            cleanName += ` - Parte ${index + 1}`;
        }
        
        return cleanName || `Composición_${Date.now()}`;
    }
    
    // 4. LIMPIAR REFERENCIAS A SUNO EN TODO EL OBJETO
    function cleanSunoReferences(obj) {
        if (typeof obj === 'object' && obj !== null) {
            for (const [key, value] of Object.entries(obj)) {
                if (typeof value === 'string') {
                    obj[key] = value.replace(/suno/gi, 'son1k');
                } else if (typeof value === 'object') {
                    cleanSunoReferences(value);
                }
            }
        }
    }
    
    // 5. INTERCEPTAR LOGS Y MOSTRAR TRANSPARENCIA
    const originalConsoleLog = console.log;
    console.log = function(...args) {
        // Interceptar logs que muestren job IDs
        const message = args.join(' ');
        if (message.includes('job_id') || message.includes('Job ID')) {
            const correctedMessage = message.replace(/suno/gi, 'son1k');
            originalConsoleLog('🎯 [TRANSPARENTE]', correctedMessage);
            
            // También mostrar en UI si existe
            if (window.addLog) {
                window.addLog(`🎯 ${correctedMessage}`);
            }
        } else {
            originalConsoleLog(...args);
        }
    };
    
    // 6. INTERCEPTAR FUNCIÓN showToast PARA CORREGIR MENSAJES
    if (window.showToast) {
        const originalShowToast = window.showToast;
        window.showToast = function(message, type) {
            const correctedMessage = message.replace(/suno/gi, 'son1k');
            return originalShowToast(correctedMessage, type);
        };
    }
    
    // 7. SOBRESCRIBIR FUNCIÓN DE GENERACIÓN ORIGINAL
    window.addEventListener('DOMContentLoaded', function() {
        // Esperar un poco para asegurar que todo esté cargado
        setTimeout(() => {
            console.log('🔧 Aplicando parches de transparencia...');
            
            // Parche para mostrar job IDs transparentes
            const originalAddLog = window.addLog;
            if (originalAddLog) {
                window.addLog = function(message, type) {
                    const correctedMessage = message.replace(/suno/gi, 'son1k');
                    return originalAddLog(correctedMessage, type);
                };
            }
            
            console.log('✅ Parches de transparencia aplicados');
        }, 1000);
    });
    
    // 8. FUNCIÓN PARA VERIFICAR QUE TODO FUNCIONA
    function verifyTransparency() {
        console.log('🧪 Verificando transparencia...');
        
        // Test básico
        const testData = {
            job_id: 'suno_job_12345',
            tracks: [{
                title: 'suno_track_1',
                job_id: 'suno_job_12345',
                provider: 'Suno',
                lyrics_preview: 'Walking down the street tonight'
            }]
        };
        
        const corrected = makeResponseTransparent(testData);
        
        console.log('📊 Test de transparencia:');
        console.log('  Job ID:', corrected.job_id);
        console.log('  Track title:', corrected.tracks[0].title);
        console.log('  Provider:', corrected.tracks[0].provider);
        
        const isTransparent = 
            !corrected.job_id.includes('suno') &&
            !corrected.tracks[0].title.includes('suno') &&
            corrected.tracks[0].provider === 'Son1k';
        
        console.log(isTransparent ? '✅ TRANSPARENCIA VERIFICADA' : '❌ TRANSPARENCIA FALLIDA');
        
        return isTransparent;
    }
    
    // 9. EJECUTAR VERIFICACIÓN AL CARGAR
    window.addEventListener('load', () => {
        setTimeout(verifyTransparency, 2000);
    });
    
    console.log('🎯 SOLUCIÓN DE TRANSPARENCIA GARANTIZADA INSTALADA');
    console.log('✅ Todas las respuestas serán automáticamente transparentes');
    console.log('🚫 No más referencias a "suno" en el frontend');
    console.log('✨ Nombres dinámicos basados en lyrics garantizados');
    
})();