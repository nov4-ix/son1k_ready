/**
 * 📊 SON1KVERS3 - Analytics Client
 * Cliente JavaScript para tracking de analytics
 */

class AnalyticsClient {
    constructor(baseUrl = 'http://localhost:8002') {
        this.baseUrl = baseUrl;
        this.sessionId = null;
        this.userId = null;
        this.isEnabled = true;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.eventQueue = [];
        this.isOnline = navigator.onLine;
        
        this.init();
    }
    
    async init() {
        console.log('📊 Inicializando Analytics Client...');
        
        // Generar ID de usuario único
        this.userId = this.generateUserId();
        
        // Iniciar sesión
        await this.startSession();
        
        // Configurar listeners
        this.setupEventListeners();
        
        // Configurar verificación de conexión
        this.setupConnectionMonitoring();
        
        // Procesar cola de eventos pendientes
        this.processEventQueue();
        
        console.log('✅ Analytics Client inicializado');
    }
    
    generateUserId() {
        // Generar ID de usuario persistente
        let userId = localStorage.getItem('son1k_user_id');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('son1k_user_id', userId);
        }
        return userId;
    }
    
    async startSession() {
        try {
            const response = await fetch(`${this.baseUrl}/api/session/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.sessionId = data.session_id;
                console.log('📊 Sesión de analytics iniciada:', this.sessionId);
            } else {
                console.warn('⚠️ Error iniciando sesión de analytics');
            }
        } catch (error) {
            console.warn('⚠️ Error conectando con analytics:', error.message);
        }
    }
    
    async endSession() {
        if (this.sessionId) {
            try {
                await fetch(`${this.baseUrl}/api/session/end`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: this.sessionId
                    })
                });
                console.log('📊 Sesión de analytics finalizada');
            } catch (error) {
                console.warn('⚠️ Error finalizando sesión:', error.message);
            }
        }
    }
    
    setupEventListeners() {
        // Escuchar eventos de generación musical
        document.addEventListener('realMusicGenerated', (event) => {
            this.trackMusicGeneration(event.detail);
        });
        
        // Escuchar eventos de interacción
        document.addEventListener('click', (event) => {
            this.trackInteraction('click', event.target);
        });
        
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                this.trackInteraction('keydown', event.target, 'Enter');
            }
        });
        
        // Escuchar cambios de página
        window.addEventListener('beforeunload', () => {
            this.endSession();
        });
        
        // Escuchar eventos de error
        window.addEventListener('error', (event) => {
            this.trackError(event.error);
        });
    }
    
    setupConnectionMonitoring() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.processEventQueue();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
        });
    }
    
    async trackMusicGeneration(trackData) {
        if (!this.isEnabled || !this.sessionId) return;
        
        const eventData = {
            session_id: this.sessionId,
            user_id: this.userId,
            prompt: trackData.prompt || 'N/A',
            style: trackData.style || 'N/A',
            duration: trackData.duration || 0,
            tempo: trackData.analysis?.tempo || 120,
            scale: trackData.analysis?.scale || 'C major',
            instruments: trackData.analysis?.instruments || [],
            mood: trackData.analysis?.mood || 'neutral',
            ai_enhanced: trackData.aiAnalysis ? true : false,
            generation_time: trackData.generation_time || 0,
            success: true,
            error_message: null
        };
        
        await this.sendEvent('/api/track/generation', eventData);
    }
    
    async trackInteraction(action, element, value = null) {
        if (!this.isEnabled || !this.sessionId) return;
        
        const eventData = {
            session_id: this.sessionId,
            user_id: this.userId,
            action: action,
            element: element.tagName + (element.id ? '#' + element.id : '') + (element.className ? '.' + element.className.split(' ').join('.') : ''),
            value: value,
            metadata: {
                timestamp: new Date().toISOString(),
                url: window.location.href,
                user_agent: navigator.userAgent
            }
        };
        
        await this.sendEvent('/api/track/interaction', eventData);
    }
    
    async trackError(error) {
        if (!this.isEnabled || !this.sessionId) return;
        
        const eventData = {
            session_id: this.sessionId,
            user_id: this.userId,
            action: 'error',
            element: 'window',
            value: error.message,
            metadata: {
                error_stack: error.stack,
                timestamp: new Date().toISOString(),
                url: window.location.href
            }
        };
        
        await this.sendEvent('/api/track/interaction', eventData);
    }
    
    async sendEvent(endpoint, data) {
        if (!this.isOnline) {
            // Agregar a cola si está offline
            this.eventQueue.push({ endpoint, data, timestamp: Date.now() });
            return;
        }
        
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.retryCount = 0;
                console.log('📊 Evento enviado:', endpoint);
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.warn('⚠️ Error enviando evento:', error.message);
            
            // Agregar a cola para reintento
            this.eventQueue.push({ endpoint, data, timestamp: Date.now() });
            
            // Reintentar después de un delay
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                setTimeout(() => this.processEventQueue(), 5000 * this.retryCount);
            }
        }
    }
    
    async processEventQueue() {
        if (this.eventQueue.length === 0 || !this.isOnline) return;
        
        const events = [...this.eventQueue];
        this.eventQueue = [];
        
        for (const event of events) {
            // Verificar que el evento no sea muy antiguo (máximo 1 hora)
            if (Date.now() - event.timestamp > 3600000) {
                continue;
            }
            
            try {
                const response = await fetch(`${this.baseUrl}${event.endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(event.data)
                });
                
                if (response.ok) {
                    console.log('📊 Evento de cola enviado:', event.endpoint);
                } else {
                    // Reagregar a cola si falla
                    this.eventQueue.push(event);
                }
            } catch (error) {
                // Reagregar a cola si falla
                this.eventQueue.push(event);
            }
        }
    }
    
    async getAnalytics(days = 7) {
        try {
            const response = await fetch(`${this.baseUrl}/api/analytics?days=${days}`);
            if (response.ok) {
                const data = await response.json();
                return data.data;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Error obteniendo analytics:', error);
            return null;
        }
    }
    
    async getHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`);
            if (response.ok) {
                const data = await response.json();
                return data;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Error verificando salud de analytics:', error);
            return null;
        }
    }
    
    enable() {
        this.isEnabled = true;
        console.log('📊 Analytics habilitado');
    }
    
    disable() {
        this.isEnabled = false;
        console.log('📊 Analytics deshabilitado');
    }
    
    getStatus() {
        return {
            enabled: this.isEnabled,
            sessionId: this.sessionId,
            userId: this.userId,
            isOnline: this.isOnline,
            queueLength: this.eventQueue.length,
            retryCount: this.retryCount
        };
    }
}

// Clase para mostrar analytics en tiempo real
class AnalyticsDashboard {
    constructor(analyticsClient) {
        this.client = analyticsClient;
        this.dashboard = null;
        this.isVisible = false;
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        this.createDashboard();
        this.setupKeyboardShortcuts();
        console.log('📊 Analytics Dashboard inicializado');
    }
    
    createDashboard() {
        this.dashboard = document.createElement('div');
        this.dashboard.id = 'analytics-dashboard';
        this.dashboard.style.cssText = `
            position: fixed;
            top: 0;
            right: -400px;
            width: 400px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.95);
            color: #00ff88;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            z-index: 10000;
            transition: right 0.3s ease;
            overflow-y: auto;
            padding: 20px;
            border-left: 2px solid #00ff88;
        `;
        
        this.dashboard.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0; color: #00ccff;">📊 ANALYTICS</h2>
                <button id="close-dashboard" style="background: #ff4444; color: white; border: none; padding: 5px 10px; cursor: pointer;">✕</button>
            </div>
            <div id="analytics-content">
                <div style="text-align: center; color: #ffaa00;">Cargando analytics...</div>
            </div>
        `;
        
        document.body.appendChild(this.dashboard);
        
        // Event listeners
        document.getElementById('close-dashboard').addEventListener('click', () => {
            this.hide();
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey && event.shiftKey && event.key === 'A') {
                event.preventDefault();
                this.toggle();
            }
        });
    }
    
    show() {
        this.dashboard.style.right = '0';
        this.isVisible = true;
        this.startUpdates();
        console.log('📊 Analytics Dashboard mostrado');
    }
    
    hide() {
        this.dashboard.style.right = '-400px';
        this.isVisible = false;
        this.stopUpdates();
        console.log('📊 Analytics Dashboard oculto');
    }
    
    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    startUpdates() {
        this.updateInterval = setInterval(() => {
            this.updateContent();
        }, 5000); // Actualizar cada 5 segundos
        this.updateContent();
    }
    
    stopUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    async updateContent() {
        try {
            const analytics = await this.client.getAnalytics(7);
            const health = await this.client.getHealth();
            const status = this.client.getStatus();
            
            if (analytics) {
                this.renderAnalytics(analytics, health, status);
            } else {
                this.renderError();
            }
        } catch (error) {
            console.error('❌ Error actualizando analytics:', error);
            this.renderError();
        }
    }
    
    renderAnalytics(analytics, health, status) {
        const content = document.getElementById('analytics-content');
        content.innerHTML = `
            <div style="margin-bottom: 20px;">
                <h3 style="color: #00ccff; margin-bottom: 10px;">📊 ESTADO DEL SISTEMA</h3>
                <div style="background: rgba(0, 255, 136, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <div><strong>Sesión:</strong> ${status.sessionId ? 'Activa' : 'Inactiva'}</div>
                    <div><strong>Usuario:</strong> ${status.userId}</div>
                    <div><strong>Online:</strong> ${status.isOnline ? 'Sí' : 'No'}</div>
                    <div><strong>Cola:</strong> ${status.queueLength} eventos</div>
                </div>
                <div style="background: rgba(0, 204, 255, 0.1); padding: 10px; border-radius: 5px;">
                    <div><strong>Servidor:</strong> ${health ? 'Conectado' : 'Desconectado'}</div>
                    <div><strong>Sesiones Activas:</strong> ${health ? health.active_sessions : 'N/A'}</div>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h3 style="color: #00ccff; margin-bottom: 10px;">🎵 GENERACIONES MUSICALES</h3>
                <div style="background: rgba(0, 255, 136, 0.1); padding: 10px; border-radius: 5px;">
                    <div><strong>Total:</strong> ${analytics.music_metrics.total_generations}</div>
                    <div><strong>Exitosas:</strong> ${analytics.music_metrics.successful_generations}</div>
                    <div><strong>Fallidas:</strong> ${analytics.music_metrics.failed_generations}</div>
                    <div><strong>Duración Promedio:</strong> ${analytics.music_metrics.avg_duration.toFixed(2)}s</div>
                    <div><strong>Tiempo Promedio:</strong> ${analytics.music_metrics.avg_generation_time.toFixed(2)}s</div>
                    <div><strong>Uso de IA:</strong> ${analytics.music_metrics.ai_usage_count}</div>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h3 style="color: #00ccff; margin-bottom: 10px;">👥 SESIONES</h3>
                <div style="background: rgba(0, 255, 136, 0.1); padding: 10px; border-radius: 5px;">
                    <div><strong>Total:</strong> ${analytics.session_metrics.total_sessions}</div>
                    <div><strong>Usuarios Únicos:</strong> ${analytics.session_metrics.unique_users}</div>
                    <div><strong>Duración Promedio:</strong> ${analytics.session_metrics.avg_session_duration.toFixed(2)}s</div>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h3 style="color: #00ccff; margin-bottom: 10px;">🎨 ESTILOS POPULARES</h3>
                <div style="background: rgba(0, 255, 136, 0.1); padding: 10px; border-radius: 5px;">
                    ${analytics.popular_styles.map(style => 
                        `<div>${style.style}: ${style.count}</div>`
                    ).join('')}
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h3 style="color: #00ccff; margin-bottom: 10px;">💬 PROMPTS POPULARES</h3>
                <div style="background: rgba(0, 255, 136, 0.1); padding: 10px; border-radius: 5px;">
                    ${analytics.popular_prompts.map(prompt => 
                        `<div title="${prompt.prompt}">${prompt.prompt.substring(0, 30)}...: ${prompt.count}</div>`
                    ).join('')}
                </div>
            </div>
            
            <div style="text-align: center; color: #ffaa00; font-size: 10px;">
                Actualizado: ${new Date().toLocaleTimeString()}
            </div>
        `;
    }
    
    renderError() {
        const content = document.getElementById('analytics-content');
        content.innerHTML = `
            <div style="text-align: center; color: #ff4444;">
                <h3>❌ Error cargando analytics</h3>
                <p>Verifica que el servidor de analytics esté corriendo</p>
            </div>
        `;
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para que otros scripts se carguen
    setTimeout(() => {
        window.analyticsClient = new AnalyticsClient();
        window.analyticsDashboard = new AnalyticsDashboard(window.analyticsClient);
        console.log('📊 Analytics Client cargado');
    }, 1000);
});

// Exportar para uso global
window.AnalyticsClient = AnalyticsClient;
window.AnalyticsDashboard = AnalyticsDashboard;
