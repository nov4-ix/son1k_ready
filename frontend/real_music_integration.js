/**
 * 🎵 SON1KVERS3 - Real Music Integration
 * Integración del generador Web Audio con el sistema existente
 */

class RealMusicIntegration {
    constructor() {
        this.webAudioGenerator = null;
        this.isInitialized = false;
        this.currentTrack = null;
        this.audioPlayer = null;
        this.visualizer = null;
        
        this.init();
    }
    
    async init() {
        try {
            // Inicializar generador Web Audio
            this.webAudioGenerator = new WebAudioGenerator();
            await this.webAudioGenerator.init();
            
            // Configurar visualizador
            this.setupVisualizer();
            
            // Configurar reproductor
            this.setupAudioPlayer();
            
            this.isInitialized = true;
            console.log('🎵 Real Music Integration inicializado');
            
            // Mostrar notificación de éxito
            this.showNotification('Sistema de generación musical real activado', 'success');
            
        } catch (error) {
            console.error('❌ Error inicializando Real Music Integration:', error);
            this.showNotification('Error inicializando generador musical', 'error');
        }
    }
    
    setupVisualizer() {
        // Crear canvas para visualización
        const canvas = document.createElement('canvas');
        canvas.id = 'musicVisualizer';
        canvas.width = 800;
        canvas.height = 200;
        canvas.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff88;
            border-radius: 10px;
            z-index: 1000;
            display: none;
        `;
        
        document.body.appendChild(canvas);
        this.visualizer = new MusicVisualizer(canvas);
    }
    
    setupAudioPlayer() {
        // Crear reproductor de audio personalizado
        this.audioPlayer = document.createElement('audio');
        this.audioPlayer.controls = true;
        this.audioPlayer.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 300px;
            z-index: 1000;
            display: none;
        `;
        
        document.body.appendChild(this.audioPlayer);
    }
    
    async generateMusic(prompt, style = 'electronic', lyrics = '') {
        if (!this.isInitialized) {
            await this.init();
        }
        
        try {
            // Mostrar indicador de carga
            this.showLoadingIndicator('Generando música real...');
            
            // Generar música usando Web Audio API
            const track = await this.webAudioGenerator.generateMusic(prompt, style);
            
            // Agregar letras si se proporcionan
            if (lyrics) {
                track.lyrics = lyrics;
            }
            
            // Guardar track actual
            this.currentTrack = track;
            
            // Crear URL de audio para reproducción
            const audioBlob = this.webAudioGenerator.export();
            const audioUrl = URL.createObjectURL(audioBlob);
            
            // Configurar reproductor
            this.audioPlayer.src = audioUrl;
            this.audioPlayer.style.display = 'block';
            
            // Mostrar visualizador
            this.visualizer.start();
            
            // Ocultar indicador de carga
            this.hideLoadingIndicator();
            
            // Mostrar notificación de éxito
            this.showNotification(`Música generada: ${track.duration.toFixed(2)}s`, 'success');
            
            // Disparar evento personalizado
            this.dispatchMusicGeneratedEvent(track);
            
            return track;
            
        } catch (error) {
            console.error('❌ Error generando música:', error);
            this.hideLoadingIndicator();
            this.showNotification('Error generando música', 'error');
            throw error;
        }
    }
    
    play() {
        if (this.currentTrack && this.audioPlayer) {
            this.audioPlayer.play();
            this.visualizer.start();
            console.log('🎵 Reproduciendo música generada');
        }
    }
    
    pause() {
        if (this.audioPlayer) {
            this.audioPlayer.pause();
            this.visualizer.stop();
            console.log('⏸️ Música pausada');
        }
    }
    
    stop() {
        if (this.audioPlayer) {
            this.audioPlayer.pause();
            this.audioPlayer.currentTime = 0;
            this.visualizer.stop();
            console.log('⏹️ Música detenida');
        }
    }
    
    download() {
        if (this.currentTrack) {
            const audioBlob = this.webAudioGenerator.export();
            const url = URL.createObjectURL(audioBlob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `son1k_${this.currentTrack.id}.wav`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log('💾 Música descargada');
        }
    }
    
    dispatchMusicGeneratedEvent(track) {
        const event = new CustomEvent('realMusicGenerated', {
            detail: {
                track: track,
                audioUrl: this.audioPlayer.src,
                duration: track.duration,
                style: track.style,
                prompt: track.prompt
            }
        });
        
        document.dispatchEvent(event);
    }
    
    showLoadingIndicator(message) {
        // Crear indicador de carga
        const loader = document.createElement('div');
        loader.id = 'realMusicLoader';
        loader.innerHTML = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0, 0, 0, 0.9);
                color: #00ff88;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #00ff88;
                z-index: 2000;
                text-align: center;
                font-family: monospace;
            ">
                <div style="margin-bottom: 10px;">🎵</div>
                <div>${message}</div>
                <div style="margin-top: 10px;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border: 3px solid #00ff88;
                        border-top: 3px solid transparent;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 0 auto;
                    "></div>
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        
        document.body.appendChild(loader);
    }
    
    hideLoadingIndicator() {
        const loader = document.getElementById('realMusicLoader');
        if (loader) {
            loader.remove();
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-family: monospace;
            z-index: 2000;
            max-width: 300px;
            word-wrap: break-word;
            background: ${type === 'success' ? '#00ff88' : type === 'error' ? '#ff4444' : '#00ccff'};
            color: ${type === 'success' ? '#000' : '#fff'};
            border: 1px solid ${type === 'success' ? '#00ff88' : type === 'error' ? '#ff4444' : '#00ccff'};
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Auto-remover después de 3 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
    
    getTrackInfo() {
        if (this.currentTrack) {
            return {
                id: this.currentTrack.id,
                prompt: this.currentTrack.prompt,
                style: this.currentTrack.style,
                duration: this.currentTrack.duration,
                analysis: this.currentTrack.analysis,
                structure: this.currentTrack.structure,
                createdAt: this.currentTrack.createdAt
            };
        }
        return null;
    }
    
    exportTrack(format = 'wav') {
        if (this.currentTrack) {
            switch (format) {
                case 'wav':
                    return this.webAudioGenerator.export();
                case 'mp3':
                    // Implementar conversión a MP3
                    return this.convertToMP3();
                default:
                    return this.webAudioGenerator.export();
            }
        }
        return null;
    }
    
    convertToMP3() {
        // Placeholder para conversión a MP3
        console.log('🔄 Conversión a MP3 no implementada aún');
        return this.webAudioGenerator.export();
    }
}

// Clase para visualización de música
class MusicVisualizer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.isRunning = false;
        this.animationId = null;
        
        this.setupCanvas();
    }
    
    setupCanvas() {
        this.canvas.width = 800;
        this.canvas.height = 200;
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.canvas.style.display = 'block';
            this.animate();
        }
    }
    
    stop() {
        this.isRunning = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.canvas.style.display = 'none';
    }
    
    animate() {
        if (!this.isRunning) return;
        
        // Limpiar canvas
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Dibujar visualización
        this.drawWaveform();
        this.drawSpectrum();
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    drawWaveform() {
        this.ctx.strokeStyle = '#00ff88';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        
        const centerY = this.canvas.height / 2;
        const amplitude = 50;
        
        for (let x = 0; x < this.canvas.width; x++) {
            const y = centerY + Math.sin(x * 0.02 + Date.now() * 0.005) * amplitude;
            
            if (x === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        
        this.ctx.stroke();
    }
    
    drawSpectrum() {
        const barWidth = this.canvas.width / 64;
        
        for (let i = 0; i < 64; i++) {
            const barHeight = Math.random() * 100;
            const x = i * barWidth;
            const y = this.canvas.height - barHeight;
            
            this.ctx.fillStyle = `hsl(${i * 5}, 100%, 50%)`;
            this.ctx.fillRect(x, y, barWidth - 2, barHeight);
        }
    }
}

// Inicializar integración cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para que otros scripts se carguen
    setTimeout(() => {
        window.realMusicIntegration = new RealMusicIntegration();
        console.log('🎵 Real Music Integration cargado');
    }, 1000);
});

// Exportar para uso global
window.RealMusicIntegration = RealMusicIntegration;
window.MusicVisualizer = MusicVisualizer;
