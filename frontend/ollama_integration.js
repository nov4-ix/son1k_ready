/**
 * 🤖 SON1KVERS3 - Ollama Integration
 * Cliente JavaScript para integración con IA local
 */

class OllamaMusicAI {
    constructor(baseUrl = 'http://localhost:8001') {
        this.baseUrl = baseUrl;
        this.isAvailable = false;
        this.healthCheckInterval = null;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        this.init();
    }
    
    async init() {
        console.log('🤖 Inicializando Ollama Music AI...');
        
        // Verificar disponibilidad
        await this.checkHealth();
        
        // Configurar verificación periódica
        this.healthCheckInterval = setInterval(() => {
            this.checkHealth();
        }, 30000); // Cada 30 segundos
        
        console.log('🤖 Ollama Music AI inicializado');
    }
    
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                const data = await response.json();
                this.isAvailable = data.ollama_available;
                this.retryCount = 0;
                
                if (this.isAvailable) {
                    console.log('✅ Ollama Music AI disponible');
                } else {
                    console.log('⚠️ Ollama Music AI no disponible (modo fallback)');
                }
            } else {
                this.isAvailable = false;
                console.log('❌ Error verificando salud de Ollama Music AI');
            }
        } catch (error) {
            this.isAvailable = false;
            this.retryCount++;
            
            if (this.retryCount <= this.maxRetries) {
                console.log(`⚠️ Error conectando con Ollama (intento ${this.retryCount}/${this.maxRetries}):`, error.message);
            } else {
                console.log('❌ Ollama Music AI no disponible después de múltiples intentos');
            }
        }
    }
    
    async analyzeMusicPrompt(prompt) {
        if (!this.isAvailable) {
            console.log('⚠️ Ollama no disponible, usando análisis de fallback');
            return this.fallbackAnalysis(prompt);
        }
        
        try {
            console.log(`🤖 Analizando prompt con IA: "${prompt}"`);
            
            const response = await fetch(`${this.baseUrl}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Análisis musical completado:', data.analysis);
                return data.analysis;
            } else {
                throw new Error(`Error en análisis: ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Error analizando prompt con IA:', error);
            return this.fallbackAnalysis(prompt);
        }
    }
    
    async generateLyrics(prompt, style = 'electronic', language = 'es') {
        if (!this.isAvailable) {
            console.log('⚠️ Ollama no disponible, usando letras de fallback');
            return this.fallbackLyrics(prompt, style);
        }
        
        try {
            console.log(`🤖 Generando letras con IA: "${prompt}" (${style})`);
            
            const response = await fetch(`${this.baseUrl}/api/lyrics`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    prompt, 
                    style, 
                    language 
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Letras generadas:', data.lyrics.length, 'caracteres');
                return data.lyrics;
            } else {
                throw new Error(`Error generando letras: ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Error generando letras con IA:', error);
            return this.fallbackLyrics(prompt, style);
        }
    }
    
    async classifyMusicStyle(prompt) {
        if (!this.isAvailable) {
            console.log('⚠️ Ollama no disponible, usando clasificación de fallback');
            return this.fallbackStyleClassification(prompt);
        }
        
        try {
            console.log(`🤖 Clasificando estilo con IA: "${prompt}"`);
            
            const response = await fetch(`${this.baseUrl}/api/classify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Estilo clasificado:', data.classification);
                return data.classification;
            } else {
                throw new Error(`Error clasificando estilo: ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Error clasificando estilo con IA:', error);
            return this.fallbackStyleClassification(prompt);
        }
    }
    
    async optimizePrompt(originalPrompt) {
        if (!this.isAvailable) {
            console.log('⚠️ Ollama no disponible, usando optimización de fallback');
            return this.fallbackOptimization(originalPrompt);
        }
        
        try {
            console.log(`🤖 Optimizando prompt con IA: "${originalPrompt}"`);
            
            const response = await fetch(`${this.baseUrl}/api/optimize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: originalPrompt })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Prompt optimizado:', data.optimization);
                return data.optimization;
            } else {
                throw new Error(`Error optimizando prompt: ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Error optimizando prompt con IA:', error);
            return this.fallbackOptimization(originalPrompt);
        }
    }
    
    // Métodos de fallback
    fallbackAnalysis(prompt) {
        const words = prompt.toLowerCase().split();
        
        let tempo = 120;
        if (words.some(w => ['lento', 'slow', 'calm'].includes(w))) tempo = 80;
        if (words.some(w => ['rápido', 'fast', 'epic', 'épico'].includes(w))) tempo = 140;
        
        let scale = "C major";
        if (words.some(w => ['menor', 'minor', 'triste', 'sad'].includes(w))) scale = "A minor";
        
        const instruments = [];
        if (words.some(w => ['piano'].includes(w))) instruments.push('piano');
        if (words.some(w => ['guitarra', 'guitar'].includes(w))) instruments.push('guitar');
        if (words.some(w => ['batería', 'drums', 'beat'].includes(w))) instruments.push('drums');
        if (words.some(w => ['sintetizador', 'synth', 'electronic'].includes(w))) instruments.push('synth');
        
        let mood = "neutral";
        if (words.some(w => ['alegre', 'happy', 'upbeat'].includes(w))) mood = "happy";
        if (words.some(w => ['triste', 'sad', 'melancholic'].includes(w))) mood = "sad";
        if (words.some(w => ['épico', 'epic', 'grandioso'].includes(w))) mood = "epic";
        
        return {
            tempo,
            scale,
            instruments: instruments.length > 0 ? instruments : ['synth', 'drums'],
            mood,
            genre: "electronic",
            key_signature: "C",
            time_signature: "4/4",
            energy_level: 7,
            complexity: 5,
            style_characteristics: ["synthetic"],
            emotional_tone: "neutral",
            technical_notes: "Basic generation",
            fallback: true
        };
    }
    
    fallbackLyrics(prompt, style) {
        const themes = {
            'electronic': [
                "En el mundo digital donde todo es posible",
                "La música fluye como código en las venas",
                "Cada beat es un latido del futuro",
                "La tecnología nos conecta, nos une"
            ],
            'synthwave': [
                "Neon lights en la noche de la ciudad",
                "El pasado y futuro se encuentran aquí",
                "Sintetizadores suenan en la oscuridad",
                "La nostalgia nos lleva al mañana"
            ],
            'cyberpunk': [
                "En las calles de la matriz digital",
                "La resistencia nace en cada byte",
                "Hackeamos la realidad, creamos el futuro",
                "La música es nuestra arma, nuestro código"
            ]
        };
        
        return themes[style] ? themes[style].join('\n') : themes['electronic'].join('\n');
    }
    
    fallbackStyleClassification(prompt) {
        const words = prompt.toLowerCase().split();
        
        if (words.some(w => ['synthwave', 'retro', '80s', 'neon'].includes(w))) {
            return {
                primary_style: "synthwave",
                secondary_styles: ["electronic"],
                confidence: 0.8,
                characteristics: ["retro", "synthetic"],
                influences: ["80s"],
                target_audience: "young_adults",
                mood_tags: ["nostalgic"],
                fallback: true
            };
        } else if (words.some(w => ['cyberpunk', 'futuro', 'digital'].includes(w))) {
            return {
                primary_style: "cyberpunk",
                secondary_styles: ["electronic", "industrial"],
                confidence: 0.8,
                characteristics: ["dark", "futuristic"],
                influences: ["sci-fi"],
                target_audience: "adults",
                mood_tags: ["dark", "futuristic"],
                fallback: true
            };
        } else {
            return {
                primary_style: "electronic",
                secondary_styles: ["ambient"],
                confidence: 0.6,
                characteristics: ["synthetic"],
                influences: ["modern"],
                target_audience: "general",
                mood_tags: ["neutral"],
                fallback: true
            };
        }
    }
    
    fallbackOptimization(originalPrompt) {
        return {
            optimized_prompt: originalPrompt,
            original_prompt: originalPrompt,
            improvements: ["Análisis básico aplicado"],
            technical_suggestions: ["Usar tempo 120 BPM", "Agregar instrumentos sintéticos"],
            style_enhancements: ["Enfocar en melodía principal"],
            confidence: 0.5,
            fallback: true
        };
    }
    
    // Método para obtener estado
    getStatus() {
        return {
            available: this.isAvailable,
            baseUrl: this.baseUrl,
            retryCount: this.retryCount,
            maxRetries: this.maxRetries
        };
    }
    
    // Método para limpiar recursos
    destroy() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
    }
}

// Integración con el sistema de generación musical real
class EnhancedMusicGenerator {
    constructor() {
        this.ollamaAI = new OllamaMusicAI();
        this.webAudioGenerator = null;
        this.isInitialized = false;
        
        this.init();
    }
    
    async init() {
        console.log('🎵 Inicializando Enhanced Music Generator...');
        
        // Esperar a que Web Audio Generator esté disponible
        if (window.WebAudioGenerator) {
            this.webAudioGenerator = new WebAudioGenerator();
            await this.webAudioGenerator.init();
        }
        
        this.isInitialized = true;
        console.log('✅ Enhanced Music Generator inicializado');
    }
    
    async generateMusicWithAI(prompt, style = 'auto', lyrics = '') {
        if (!this.isInitialized) {
            await this.init();
        }
        
        try {
            console.log('🤖 Generando música con IA local...');
            
            // 1. Analizar prompt con IA (el estilo se extrae automáticamente)
            const analysis = await this.ollamaAI.analyzeMusicPrompt(prompt);
            console.log('📊 Análisis IA:', analysis);
            
            // 2. Clasificar estilo (si no se detectó automáticamente)
            let styleClassification = analysis.primary_style || 'electronic';
            if (style === 'auto') {
                styleClassification = await this.ollamaAI.classifyMusicStyle(prompt);
                console.log('🎨 Clasificación de estilo:', styleClassification);
            }
            
            // 3. Generar letras si no se proporcionan
            let generatedLyrics = lyrics;
            if (!lyrics && !analysis.fallback) {
                generatedLyrics = await this.ollamaAI.generateLyrics(prompt, styleClassification);
                console.log('📝 Letras generadas:', generatedLyrics);
            }
            
            // 4. Optimizar prompt
            const optimization = await this.ollamaAI.optimizePrompt(prompt);
            console.log('⚡ Optimización:', optimization);
            
            // 5. Generar música con análisis mejorado
            const enhancedAnalysis = {
                ...analysis,
                style_classification: styleClassification,
                optimization: optimization,
                ai_enhanced: true
            };
            
            // 6. Usar Web Audio Generator con análisis mejorado
            if (this.webAudioGenerator) {
                const track = await this.webAudioGenerator.generateMusic(
                    optimization.optimized_prompt || prompt,
                    styleClassification.primary_style || style
                );
                
                // Agregar metadatos de IA
                track.aiAnalysis = enhancedAnalysis;
                track.generatedLyrics = generatedLyrics;
                track.optimization = optimization;
                
                console.log('✅ Música generada con IA:', track);
                return track;
            } else {
                throw new Error('Web Audio Generator no disponible');
            }
            
        } catch (error) {
            console.error('❌ Error generando música con IA:', error);
            throw error;
        }
    }
    
    async getAISuggestions(prompt) {
        try {
            const analysis = await this.ollamaAI.analyzeMusicPrompt(prompt);
            const styleClassification = await this.ollamaAI.classifyMusicStyle(prompt);
            const optimization = await this.ollamaAI.optimizePrompt(prompt);
            
            return {
                analysis,
                styleClassification,
                optimization,
                suggestions: [
                    `Tempo recomendado: ${analysis.tempo} BPM`,
                    `Escala sugerida: ${analysis.scale}`,
                    `Instrumentos: ${analysis.instruments.join(', ')}`,
                    `Mood: ${analysis.mood}`,
                    `Estilo principal: ${styleClassification.primary_style}`,
                    `Mejoras: ${optimization.improvements.join(', ')}`
                ]
            };
        } catch (error) {
            console.error('❌ Error obteniendo sugerencias de IA:', error);
            return null;
        }
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para que otros scripts se carguen
    setTimeout(() => {
        window.ollamaMusicAI = new OllamaMusicAI();
        window.enhancedMusicGenerator = new EnhancedMusicGenerator();
        console.log('🤖 Ollama Integration cargado');
    }, 1000);
});

// Exportar para uso global
window.OllamaMusicAI = OllamaMusicAI;
window.EnhancedMusicGenerator = EnhancedMusicGenerator;
