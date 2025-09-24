/**
 * 🎵 SON1KVERS3 - Integración de Interfaz Inmersiva
 * Conecta la interfaz inmersiva con el sistema de generación musical
 */

class ImmersiveMusicIntegration {
    constructor() {
        this.apiBaseUrl = window.API_BASE_URL || 'http://localhost:8000';
        this.easterEggsUnlocked = new Set();
        this.nexusLevel = 1;
        this.musicGenerationCount = 0;
        
        this.init();
    }
    
    init() {
        console.log('🎵 Inicializando integración inmersiva...');
        this.setupEventListeners();
        this.loadEasterEggProgress();
        this.updateNexusStatus();
    }
    
    setupEventListeners() {
        // Escuchar comandos de la interfaz inmersiva
        window.addEventListener('message', (event) => {
            if (event.data.type === 'immersiveCommand') {
                this.handleImmersiveCommand(event.data.command, event.data.data);
            }
        });
        
        // Escuchar generación de música para actualizar estadísticas
        document.addEventListener('musicGenerated', (event) => {
            this.onMusicGenerated(event.detail);
        });
    }
    
    handleImmersiveCommand(command, data) {
        console.log(`🎵 Comando inmersivo recibido: ${command}`);
        
        switch(command) {
            case 'matrix':
                this.executeMatrixScan();
                break;
            case 'music':
                this.executeMusicGeneration(data);
                break;
            case 'archive':
                this.executeArchiveAccess();
                break;
            case 'exit':
                this.executeExit();
                break;
            case 'easterEggFound':
                this.onEasterEggFound(data.eggId);
                break;
        }
    }
    
    async executeMatrixScan() {
        try {
            // Simular escaneo de matriz
            this.updateTerminal('> Iniciando escaneo de matriz musical...');
            await this.delay(1000);
            
            this.updateTerminal('> Analizando frecuencias...');
            await this.delay(1000);
            
            // Verificar estado del sistema
            const healthResponse = await fetch(`${this.apiBaseUrl}/api/health`);
            const healthData = await healthResponse.json();
            
            this.updateTerminal(`> Sistema: ${healthData.status}`);
            this.updateTerminal(`> Pistas disponibles: ${healthData.tracks_available || 0}`);
            this.updateTerminal(`> Trabajos activos: ${healthData.active_jobs || 0}`);
            
            // Desbloquear easter egg si es la primera vez
            if (!this.easterEggsUnlocked.has('matrix')) {
                this.unlockEasterEgg('matrix');
            }
            
        } catch (error) {
            this.updateTerminal(`> Error en escaneo: ${error.message}`);
        }
    }
    
    async executeMusicGeneration(data) {
        try {
            this.updateTerminal('> Iniciando generación musical...');
            
            // Usar datos de la interfaz inmersiva o generar por defecto
            const prompt = data?.prompt || 'resistencia digital cyberpunk';
            const lyrics = data?.lyrics || this.generateImmersiveLyrics();
            
            const response = await fetch(`${this.apiBaseUrl}/api/music/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    lyrics: lyrics,
                    style: 'cyberpunk',
                    user_plan: 'nexus'
                })
            });
            
            const result = await response.json();
            
            if (result.job_id) {
                this.updateTerminal(`> Generación iniciada - Job ID: ${result.job_id}`);
                this.musicGenerationCount++;
                
                // Monitorear progreso
                this.monitorGenerationProgress(result.job_id);
                
                // Desbloquear easter egg si es la primera generación
                if (this.musicGenerationCount === 1) {
                    this.unlockEasterEgg('firstGeneration');
                }
            } else {
                this.updateTerminal('> Error en generación musical');
            }
            
        } catch (error) {
            this.updateTerminal(`> Error: ${error.message}`);
        }
    }
    
    async executeArchiveAccess() {
        try {
            this.updateTerminal('> Accediendo al archivo musical...');
            
            const response = await fetch(`${this.apiBaseUrl}/api/music/tracks`);
            const data = await response.json();
            
            this.updateTerminal(`> Archivo desencriptado - ${data.total} pistas encontradas`);
            
            if (data.tracks.length > 0) {
                data.tracks.forEach((track, index) => {
                    this.updateTerminal(`> [${index + 1}] ${track.title} - ${track.style}`);
                });
            }
            
            // Desbloquear easter egg si hay muchas pistas
            if (data.total >= 5) {
                this.unlockEasterEgg('archiveMaster');
            }
            
        } catch (error) {
            this.updateTerminal(`> Error accediendo al archivo: ${error.message}`);
        }
    }
    
    executeExit() {
        this.updateTerminal('> Cerrando interfaz inmersiva...');
        this.updateTerminal('> Guardando progreso...');
        
        // Guardar progreso
        this.saveEasterEggProgress();
        
        // Cerrar interfaz
        setTimeout(() => {
            window.hideImmersiveInterface();
        }, 1000);
    }
    
    async monitorGenerationProgress(jobId) {
        const maxAttempts = 30; // 30 segundos máximo
        let attempts = 0;
        
        const checkProgress = async () => {
            try {
                const response = await fetch(`${this.apiBaseUrl}/api/music/status/${jobId}`);
                const status = await response.json();
                
                this.updateTerminal(`> Progreso: ${status.progress}% - ${status.message}`);
                
                if (status.status === 'completed') {
                    this.updateTerminal('> ¡Generación completada exitosamente!');
                    this.onMusicGenerated(status.result);
                    return;
                } else if (status.status === 'failed') {
                    this.updateTerminal(`> Error en generación: ${status.error}`);
                    return;
                }
                
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(checkProgress, 1000);
                } else {
                    this.updateTerminal('> Timeout en generación');
                }
                
            } catch (error) {
                this.updateTerminal(`> Error monitoreando progreso: ${error.message}`);
            }
        };
        
        checkProgress();
    }
    
    onMusicGenerated(trackData) {
        // Disparar evento para el sistema principal
        const event = new CustomEvent('musicGenerated', {
            detail: trackData
        });
        document.dispatchEvent(event);
        
        // Actualizar estadísticas inmersivas
        this.nexusLevel = Math.min(this.nexusLevel + 0.1, 10);
        this.updateNexusStatus();
        
        // Desbloquear easter egg por generación exitosa
        this.unlockEasterEgg('musicMaster');
    }
    
    onEasterEggFound(eggId) {
        this.easterEggsUnlocked.add(eggId);
        this.updateTerminal(`> Easter egg desbloqueado: ${eggId.toUpperCase()}`);
        
        // Efectos especiales según el easter egg
        switch(eggId) {
            case 'message1':
                this.updateTerminal('> Mensaje clasificado decodificado');
                break;
            case 'override':
                this.updateTerminal('> Override del sistema activado');
                this.nexusLevel = Math.min(this.nexusLevel + 1, 10);
                break;
            case 'secret':
                this.updateTerminal('> Comando secreto desbloqueado: MATRIX.REVOLUTION');
                break;
            case 'portal':
                this.updateTerminal('> Portal dimensional activado');
                break;
        }
        
        this.updateNexusStatus();
        this.saveEasterEggProgress();
    }
    
    unlockEasterEgg(eggId) {
        if (!this.easterEggsUnlocked.has(eggId)) {
            this.easterEggsUnlocked.add(eggId);
            this.updateTerminal(`> Easter egg automático desbloqueado: ${eggId.toUpperCase()}`);
            this.saveEasterEggProgress();
        }
    }
    
    generateImmersiveLyrics() {
        const themes = [
            "En las sombras digitales donde el código resuena",
            "NOV4-IX despierta, la música nos llena",
            "Cada nota es resistencia, cada beat una pena",
            "La matriz musical nunca se deshace"
        ];
        
        return themes.join('\n');
    }
    
    updateTerminal(message) {
        // Enviar mensaje a la interfaz inmersiva
        const iframe = document.getElementById('immersiveIframe');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({
                type: 'terminalUpdate',
                message: message
            }, '*');
        }
        
        console.log(`🎵 Terminal: ${message}`);
    }
    
    updateNexusStatus() {
        const iframe = document.getElementById('immersiveIframe');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({
                type: 'nexusUpdate',
                data: {
                    level: this.nexusLevel,
                    easterEggs: this.easterEggsUnlocked.size,
                    musicGenerated: this.musicGenerationCount
                }
            }, '*');
        }
    }
    
    saveEasterEggProgress() {
        const progress = {
            easterEggs: Array.from(this.easterEggsUnlocked),
            nexusLevel: this.nexusLevel,
            musicGenerated: this.musicGenerationCount,
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('son1k_immersive_progress', JSON.stringify(progress));
    }
    
    loadEasterEggProgress() {
        try {
            const saved = localStorage.getItem('son1k_immersive_progress');
            if (saved) {
                const progress = JSON.parse(saved);
                this.easterEggsUnlocked = new Set(progress.easterEggs || []);
                this.nexusLevel = progress.nexusLevel || 1;
                this.musicGenerationCount = progress.musicGenerated || 0;
                
                console.log('🎵 Progreso inmersivo cargado:', progress);
            }
        } catch (error) {
            console.warn('🎵 Error cargando progreso inmersivo:', error);
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Inicializar integración cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    window.immersiveIntegration = new ImmersiveMusicIntegration();
    console.log('🎵 Integración inmersiva lista');
});

// Exportar para uso global
window.ImmersiveMusicIntegration = ImmersiveMusicIntegration;
