/**
 * 🎯 Frontend Transparent Interceptor
 * Intercepta y redirige requests para asegurar transparencia total
 */

// Interceptor que captura todas las requests de generación
class TransparentProductionInterceptor {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.initialize();
    }

    initialize() {
        console.log('🎯 Inicializando Interceptor de Producción Transparente');
        
        // Interceptar fetch requests
        this.interceptFetch();
        
        // Interceptar XMLHttpRequest
        this.interceptXHR();
        
        // Interceptar formularios de generación
        this.interceptGenerationForms();
    }

    interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = async (url, options = {}) => {
            // Interceptar requests que contengan 'suno' o generación
            if (this.shouldInterceptRequest(url, options)) {
                console.log('🔄 Interceptando request:', url);
                return this.handleTransparentRequest(url, options);
            }
            
            return originalFetch(url, options);
        };
    }

    interceptXHR() {
        const originalXHROpen = XMLHttpRequest.prototype.open;
        const originalXHRSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._url = url;
            this._method = method;
            return originalXHROpen.call(this, method, url, ...args);
        };
        
        XMLHttpRequest.prototype.send = function(data) {
            if (this.shouldInterceptRequest(this._url, { method: this._method, body: data })) {
                console.log('🔄 Interceptando XHR:', this._url);
                this.handleTransparentXHR(data);
                return;
            }
            
            return originalXHRSend.call(this, data);
        };
    }

    shouldInterceptRequest(url, options) {
        if (!url) return false;
        
        // Interceptar si contiene 'suno' o es request de generación
        return url.includes('suno') || 
               url.includes('generate') || 
               url.includes('music') ||
               (options.body && this.isGenerationRequest(options.body));
    }

    isGenerationRequest(body) {
        try {
            const data = typeof body === 'string' ? JSON.parse(body) : body;
            return data && (data.lyrics || data.prompt || data.style);
        } catch {
            return false;
        }
    }

    async handleTransparentRequest(url, options) {
        try {
            // Transformar request a formato transparente
            const transparentRequest = this.transformToTransparentRequest(options);
            
            // Hacer request al endpoint corregido
            const response = await fetch(`${this.apiBase}/api/music/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...transparentRequest.headers
                },
                body: JSON.stringify(transparentRequest.body)
            });

            const result = await response.json();
            
            // Transformar response para asegurar transparencia
            const transparentResult = this.ensureTransparentResponse(result);
            
            // Crear response object compatible
            return new Response(JSON.stringify(transparentResult), {
                status: response.status,
                statusText: response.statusText,
                headers: response.headers
            });
            
        } catch (error) {
            console.error('❌ Error en interceptor transparente:', error);
            throw error;
        }
    }

    transformToTransparentRequest(options) {
        let body = {};
        
        try {
            if (options.body) {
                body = typeof options.body === 'string' ? JSON.parse(options.body) : options.body;
            }
        } catch {
            // Si no se puede parsear, crear estructura básica
        }

        return {
            headers: {
                'Content-Type': 'application/json'
            },
            body: {
                lyrics: body.lyrics || body.text || '',
                prompt: body.prompt || body.style || body.description || 'electronic music',
                instrumental: body.instrumental || false,
                style: 'default'
            }
        };
    }

    ensureTransparentResponse(result) {
        // Asegurar que NO aparezca 'suno' en ninguna parte de la response
        const cleanResult = JSON.parse(JSON.stringify(result));
        
        // Limpiar job_id
        if (cleanResult.job_id) {
            cleanResult.job_id = cleanResult.job_id.replace(/suno/gi, 'son1k');
        }
        
        // Limpiar tracks
        if (cleanResult.tracks) {
            cleanResult.tracks = cleanResult.tracks.map(track => ({
                ...track,
                job_id: track.job_id ? track.job_id.replace(/suno/gi, 'son1k') : undefined,
                provider: 'Son1k',
                title: track.title || this.generateDynamicTitle(track.lyrics_preview || '')
            }));
        }
        
        // Limpiar cualquier string que contenga 'suno'
        this.cleanObjectFromSuno(cleanResult);
        
        return cleanResult;
    }

    cleanObjectFromSuno(obj) {
        if (typeof obj === 'object' && obj !== null) {
            for (const [key, value] of Object.entries(obj)) {
                if (typeof value === 'string') {
                    obj[key] = value.replace(/suno/gi, 'son1k');
                } else if (typeof value === 'object') {
                    this.cleanObjectFromSuno(value);
                }
            }
        }
    }

    generateDynamicTitle(lyrics) {
        if (!lyrics) return `Composición_${Date.now()}`;
        
        // Tomar primera línea significativa
        const lines = lyrics.split('\n');
        for (const line of lines) {
            const cleaned = line.trim();
            if (cleaned.length > 3) {
                return cleaned.split(' ').slice(0, 4).join(' ');
            }
        }
        
        return lyrics.split(' ').slice(0, 4).join(' ') || `Composición_${Date.now()}`;
    }

    interceptGenerationForms() {
        // Observar cambios en el DOM para interceptar formularios
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.checkAndInterceptForms(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    checkAndInterceptForms(element) {
        // Buscar formularios de generación
        const forms = element.querySelectorAll('form, [data-generation], .generation-form');
        
        forms.forEach(form => {
            if (!form.hasAttribute('data-intercepted')) {
                form.setAttribute('data-intercepted', 'true');
                
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleFormSubmission(form);
                });
            }
        });
    }

    async handleFormSubmission(form) {
        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Extraer datos de generación
            const lyrics = data.lyrics || data.text || '';
            const prompt = data.prompt || data.style || data.description || 'electronic music';
            
            console.log('🎵 Interceptando generación de formulario');
            console.log('📝 Lyrics:', lyrics.substring(0, 50) + '...');
            console.log('🎨 Prompt:', prompt);
            
            // Hacer request transparente
            const response = await fetch(`${this.apiBase}/api/music/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    lyrics,
                    prompt,
                    instrumental: data.instrumental === 'true' || data.instrumental === true
                })
            });
            
            const result = await response.json();
            console.log('✅ Generación transparente completada:', result);
            
            // Notificar al frontend original
            this.notifyGenerationComplete(result);
            
        } catch (error) {
            console.error('❌ Error en generación transparente:', error);
        }
    }

    notifyGenerationComplete(result) {
        // Disparar evento personalizado para notificar al frontend
        const event = new CustomEvent('transparentGenerationComplete', {
            detail: result
        });
        
        document.dispatchEvent(event);
    }
}

// Auto-inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.transparentInterceptor = new TransparentProductionInterceptor();
    });
} else {
    window.transparentInterceptor = new TransparentProductionInterceptor();
}

// Listener para eventos de generación transparente
document.addEventListener('transparentGenerationComplete', (event) => {
    console.log('🎯 Generación transparente completada:', event.detail);
    
    // Actualizar UI si es necesario
    if (window.updateGenerationUI) {
        window.updateGenerationUI(event.detail);
    }
});

console.log('🎯 Sistema de Interceptación Transparente Inicializado');
console.log('🚫 Todas las referencias a "suno" serán interceptadas y transformadas');
console.log('✨ Los archivos tendrán nombres dinámicos basados en lyrics');