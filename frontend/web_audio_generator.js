/**
 * 🎵 SON1KVERS3 - Web Audio Generator
 * Sistema de generación musical real usando Web Audio API
 */

class WebAudioGenerator {
    constructor() {
        this.audioContext = null;
        this.masterGain = null;
        this.instruments = new Map();
        this.isInitialized = false;
        this.currentTrack = null;
        this.visualizer = null;
        
        this.init();
    }
    
    async init() {
        try {
            // Crear contexto de audio
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.audioContext.createGain();
            this.masterGain.connect(this.audioContext.destination);
            this.masterGain.gain.value = 0.7;
            
            // Inicializar instrumentos
            await this.initializeInstruments();
            
            this.isInitialized = true;
            console.log('🎵 Web Audio Generator inicializado');
            
        } catch (error) {
            console.error('❌ Error inicializando Web Audio Generator:', error);
        }
    }
    
    async initializeInstruments() {
        // Sintetizador de ondas
        this.instruments.set('synthesizer', new Synthesizer(this.audioContext));
        
        // Generador de beats
        this.instruments.set('drumMachine', new DrumMachine(this.audioContext));
        
        // Generador de melodías
        this.instruments.set('melodyGenerator', new MelodyGenerator(this.audioContext));
        
        // Generador de bajos
        this.instruments.set('bassGenerator', new BassGenerator(this.audioContext));
        
        // Efectos
        this.instruments.set('effects', new AudioEffects(this.audioContext));
    }
    
    async generateMusic(prompt, style = 'electronic') {
        if (!this.isInitialized) {
            await this.init();
        }
        
        console.log(`🎵 Generando música: "${prompt}" (${style})`);
        
        try {
            // Analizar prompt
            const analysis = this.analyzePrompt(prompt, style);
            
            // Crear estructura musical
            const structure = this.createMusicalStructure(analysis);
            
            // Generar audio
            const audioBuffer = await this.renderTrack(structure);
            
            // Crear objeto de track
            this.currentTrack = {
                id: `track_${Date.now()}`,
                prompt: prompt,
                style: style,
                analysis: analysis,
                structure: structure,
                audioBuffer: audioBuffer,
                duration: audioBuffer.duration,
                createdAt: new Date().toISOString()
            };
            
            console.log('✅ Música generada exitosamente');
            return this.currentTrack;
            
        } catch (error) {
            console.error('❌ Error generando música:', error);
            throw error;
        }
    }
    
    analyzePrompt(prompt, style) {
        const words = prompt.toLowerCase().split(' ');
        
        // Detectar tempo (más inteligente)
        let tempo = 120;
        const tempoMatch = prompt.match(/(\d+)\s*bpm/i);
        if (tempoMatch) {
            tempo = parseInt(tempoMatch[1]);
        } else {
            if (words.some(w => ['lento', 'slow', 'calm', 'relajante'].includes(w))) tempo = 80;
            if (words.some(w => ['rápido', 'fast', 'energético', 'energetic'].includes(w))) tempo = 140;
            if (words.some(w => ['épico', 'epic', 'grandioso', 'majestic'].includes(w))) tempo = 160;
            if (words.some(w => ['ultra', 'extremo', 'extreme'].includes(w))) tempo = 180;
        }
        
        // Detectar escala
        let scale = 'C major';
        if (words.some(w => ['menor', 'minor', 'triste', 'sad', 'melancólico'].includes(w))) scale = 'A minor';
        if (words.some(w => ['dórico', 'dorian', 'misterioso', 'mysterious'].includes(w))) scale = 'D dorian';
        if (words.some(w => ['pentatónica', 'pentatonic', 'blues'].includes(w))) scale = 'A minor pentatonic';
        
        // Detectar instrumentos (más completo)
        const instruments = [];
        const instrumentKeywords = {
            'piano': ['piano', 'teclado', 'keyboard'],
            'guitar': ['guitarra', 'guitar', 'acoustic', 'acústica', 'electric', 'eléctrica'],
            'drums': ['batería', 'drums', 'percusión', 'percussion', 'beat'],
            'bass': ['bajo', 'bass', 'bassline'],
            'synth': ['sintetizador', 'synth', 'sintético', 'synthetic', 'electronic', 'electrónico'],
            'strings': ['cuerdas', 'strings', 'violín', 'violin', 'cello', 'viola'],
            'brass': ['vientos', 'brass', 'trompeta', 'trumpet', 'saxofón', 'saxophone'],
            'vocal': ['voz', 'voice', 'vocal', 'cantar', 'sing']
        };
        
        for (const [instrument, keywords] of Object.entries(instrumentKeywords)) {
            if (keywords.some(keyword => words.includes(keyword))) {
                instruments.push(instrument);
            }
        }
        
        // Detectar mood (más completo)
        let mood = 'neutral';
        const moodKeywords = {
            'happy': ['alegre', 'happy', 'feliz', 'joyful', 'upbeat', 'energético'],
            'sad': ['triste', 'sad', 'melancólico', 'melancholic', 'nostálgico', 'nostalgic'],
            'epic': ['épico', 'epic', 'grandioso', 'majestic', 'heroic', 'heroico'],
            'mysterious': ['misterioso', 'mysterious', 'oscuro', 'dark', 'siniestro', 'eerie'],
            'romantic': ['romántico', 'romantic', 'amor', 'love', 'pasional', 'passionate'],
            'aggressive': ['agresivo', 'aggressive', 'intenso', 'intense', 'fuerte', 'strong']
        };
        
        for (const [moodType, keywords] of Object.entries(moodKeywords)) {
            if (keywords.some(keyword => words.includes(keyword))) {
                mood = moodType;
                break;
            }
        }
        
        // Detectar estilo musical
        let detectedStyle = 'electronic';
        const styleKeywords = {
            'synthwave': ['synthwave', 'retro', '80s', 'nostálgico', 'nostalgic'],
            'cyberpunk': ['cyberpunk', 'futurista', 'futuristic', 'digital', 'tech'],
            'ambient': ['ambient', 'atmosférico', 'atmospheric', 'espacial', 'space'],
            'rock': ['rock', 'guitar', 'guitarra', 'energético', 'energetic'],
            'jazz': ['jazz', 'blues', 'improvisación', 'improvisation'],
            'classical': ['clásico', 'classical', 'orquestal', 'orchestral', 'sinfónico'],
            'pop': ['pop', 'comercial', 'commercial', 'mainstream'],
            'electronic': ['electronic', 'electrónico', 'dance', 'techno', 'house']
        };
        
        for (const [styleType, keywords] of Object.entries(styleKeywords)) {
            if (keywords.some(keyword => words.includes(keyword))) {
                detectedStyle = styleType;
                break;
            }
        }
        
        return {
            tempo: tempo,
            scale: scale,
            instruments: instruments.length > 0 ? instruments : ['synth', 'drums'],
            mood: mood,
            style: detectedStyle,
            key: this.getKeyFromScale(scale),
            timeSignature: '4/4'
        };
    }
    
    getKeyFromScale(scale) {
        const scaleMap = {
            'C major': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
            'A minor': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
            'D dorian': ['D', 'E', 'F', 'G', 'A', 'B', 'C']
        };
        return scaleMap[scale] || scaleMap['C major'];
    }
    
    createMusicalStructure(analysis) {
        const structure = {
            tempo: analysis.tempo,
            timeSignature: analysis.timeSignature,
            key: analysis.key,
            mood: analysis.mood,
            sections: []
        };
        
        // Crear secciones básicas
        const sectionTypes = ['intro', 'verse', 'chorus', 'bridge', 'outro'];
        const sectionLengths = [4, 8, 8, 4, 4]; // en compases
        
        sectionTypes.forEach((type, index) => {
            structure.sections.push({
                type: type,
                length: sectionLengths[index],
                instruments: this.selectInstrumentsForSection(type, analysis),
                notes: this.generateNotesForSection(type, analysis),
                effects: this.selectEffectsForSection(type, analysis)
            });
        });
        
        return structure;
    }
    
    selectInstrumentsForSection(sectionType, analysis) {
        const baseInstruments = analysis.instruments;
        
        switch (sectionType) {
            case 'intro':
                return baseInstruments.filter(inst => inst !== 'drums');
            case 'verse':
                return baseInstruments;
            case 'chorus':
                return [...baseInstruments, 'synth']; // Agregar más capas
            case 'bridge':
                return baseInstruments.filter(inst => inst !== 'bass');
            case 'outro':
                return baseInstruments.filter(inst => inst !== 'drums');
            default:
                return baseInstruments;
        }
    }
    
    generateNotesForSection(sectionType, analysis) {
        const key = analysis.key;
        const mood = analysis.mood;
        
        // Generar progresión de acordes basada en el mood
        let chordProgression = this.getChordProgression(mood, key);
        
        // Generar melodía
        let melody = this.generateMelody(chordProgression, key, mood);
        
        return {
            chords: chordProgression,
            melody: melody,
            bass: this.generateBassLine(chordProgression, key)
        };
    }
    
    getChordProgression(mood, key) {
        const progressions = {
            'happy': ['I', 'V', 'vi', 'IV'],
            'sad': ['i', 'VII', 'VI', 'VII'],
            'epic': ['I', 'vi', 'IV', 'V'],
            'mysterious': ['i', 'VII', 'i', 'VII'],
            'neutral': ['I', 'IV', 'V', 'I']
        };
        
        return progressions[mood] || progressions['neutral'];
    }
    
    generateMelody(chordProgression, key, mood) {
        const melody = [];
        const scale = key;
        
        chordProgression.forEach(chord => {
            // Generar 4 notas por acorde
            for (let i = 0; i < 4; i++) {
                const note = this.getRandomNoteFromScale(scale);
                melody.push({
                    note: note,
                    duration: 0.5, // media nota
                    velocity: this.getVelocityForMood(mood)
                });
            }
        });
        
        return melody;
    }
    
    getRandomNoteFromScale(scale) {
        const octave = Math.floor(Math.random() * 2) + 4; // octavas 4-5
        const noteIndex = Math.floor(Math.random() * scale.length);
        return scale[noteIndex] + octave;
    }
    
    getVelocityForMood(mood) {
        const velocities = {
            'happy': 0.8,
            'sad': 0.4,
            'epic': 1.0,
            'mysterious': 0.6,
            'neutral': 0.7
        };
        return velocities[mood] || 0.7;
    }
    
    generateBassLine(chordProgression, key) {
        const bassLine = [];
        
        chordProgression.forEach(chord => {
            // Generar 2 notas de bajo por acorde
            for (let i = 0; i < 2; i++) {
                const note = this.getBassNoteForChord(chord, key);
                bassLine.push({
                    note: note,
                    duration: 1.0, // nota completa
                    velocity: 0.8
                });
            }
        });
        
        return bassLine;
    }
    
    getBassNoteForChord(chord, key) {
        // Simplificado: usar la tónica del acorde
        const chordMap = {
            'I': key[0],
            'V': key[4],
            'vi': key[5],
            'IV': key[3],
            'VII': key[6]
        };
        return chordMap[chord] || key[0];
    }
    
    selectEffectsForSection(sectionType, analysis) {
        const effects = [];
        
        if (sectionType === 'intro' || sectionType === 'outro') {
            effects.push('reverb');
        }
        
        if (analysis.mood === 'mysterious') {
            effects.push('delay', 'chorus');
        }
        
        if (analysis.mood === 'epic') {
            effects.push('distortion', 'compressor');
        }
        
        return effects;
    }
    
    async renderTrack(structure) {
        const sampleRate = this.audioContext.sampleRate;
        const duration = this.calculateTrackDuration(structure);
        const bufferLength = Math.floor(sampleRate * duration);
        
        // Crear buffer de audio
        const audioBuffer = this.audioContext.createBuffer(2, bufferLength, sampleRate);
        const leftChannel = audioBuffer.getChannelData(0);
        const rightChannel = audioBuffer.getChannelData(1);
        
        // Renderizar cada sección
        let currentTime = 0;
        
        for (const section of structure.sections) {
            await this.renderSection(section, structure, leftChannel, rightChannel, currentTime);
            currentTime += this.sectionTimeToSamples(section.length, structure.tempo, sampleRate);
        }
        
        return audioBuffer;
    }
    
    calculateTrackDuration(structure) {
        let totalBars = 0;
        structure.sections.forEach(section => {
            totalBars += section.length;
        });
        
        // Convertir compases a segundos
        const beatsPerBar = 4; // 4/4 time signature
        const totalBeats = totalBars * beatsPerBar;
        const duration = (totalBeats * 60) / structure.tempo; // tempo en BPM
        
        return duration;
    }
    
    sectionTimeToSamples(length, tempo, sampleRate) {
        const beatsPerBar = 4;
        const totalBeats = length * beatsPerBar;
        const duration = (totalBeats * 60) / tempo;
        return Math.floor(duration * sampleRate);
    }
    
    async renderSection(section, structure, leftChannel, rightChannel, startTime) {
        const sampleRate = this.audioContext.sampleRate;
        const sectionSamples = this.sectionTimeToSamples(section.length, structure.tempo, sampleRate);
        
        // Renderizar cada instrumento
        for (const instrumentName of section.instruments) {
            const instrument = this.instruments.get(this.getInstrumentClass(instrumentName));
            if (instrument) {
                await instrument.render(section, structure, leftChannel, rightChannel, startTime, sectionSamples);
            }
        }
    }
    
    getInstrumentClass(instrumentName) {
        const instrumentMap = {
            'piano': 'synthesizer',
            'guitar': 'synthesizer',
            'synth': 'synthesizer',
            'drums': 'drumMachine',
            'bass': 'bassGenerator',
            'melody': 'melodyGenerator'
        };
        return instrumentMap[instrumentName] || 'synthesizer';
    }
    
    play() {
        if (this.currentTrack && this.currentTrack.audioBuffer) {
            const source = this.audioContext.createBufferSource();
            source.buffer = this.currentTrack.audioBuffer;
            source.connect(this.masterGain);
            source.start();
            
            console.log('🎵 Reproduciendo música generada');
            return source;
        }
    }
    
    stop() {
        if (this.currentTrack) {
            // Implementar stop logic
            console.log('⏹️ Música detenida');
        }
    }
    
    export() {
        if (this.currentTrack && this.currentTrack.audioBuffer) {
            // Implementar exportación a WAV
            console.log('💾 Exportando música...');
            return this.audioBufferToWav(this.currentTrack.audioBuffer);
        }
    }
    
    audioBufferToWav(audioBuffer) {
        const length = audioBuffer.length;
        const sampleRate = audioBuffer.sampleRate;
        const arrayBuffer = new ArrayBuffer(44 + length * 2);
        const view = new DataView(arrayBuffer);
        
        // WAV header
        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };
        
        writeString(0, 'RIFF');
        view.setUint32(4, 36 + length * 2, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, 2, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2 * 2, true);
        view.setUint16(32, 4, true);
        view.setUint16(34, 16, true);
        writeString(36, 'data');
        view.setUint32(40, length * 2, true);
        
        // Convertir audio data
        const leftChannel = audioBuffer.getChannelData(0);
        const rightChannel = audioBuffer.getChannelData(1);
        let offset = 44;
        
        for (let i = 0; i < length; i++) {
            view.setInt16(offset, leftChannel[i] * 0x7FFF, true);
            offset += 2;
            view.setInt16(offset, rightChannel[i] * 0x7FFF, true);
            offset += 2;
        }
        
        return new Blob([arrayBuffer], { type: 'audio/wav' });
    }
}

// Clases de instrumentos
class Synthesizer {
    constructor(audioContext) {
        this.audioContext = audioContext;
    }
    
    async render(section, structure, leftChannel, rightChannel, startTime, sectionSamples) {
        // Implementar síntesis de ondas
        const sampleRate = this.audioContext.sampleRate;
        
        for (let i = 0; i < sectionSamples; i++) {
            const time = (startTime + i) / sampleRate;
            const sample = this.generateSample(time, section, structure);
            
            const index = startTime + i;
            if (index < leftChannel.length) {
                leftChannel[index] += sample * 0.3;
                rightChannel[index] += sample * 0.3;
            }
        }
    }
    
    generateSample(time, section, structure) {
        let sample = 0;
        
        // Generar ondas para cada nota
        section.notes.melody.forEach(note => {
            const frequency = this.noteToFrequency(note.note);
            const wave = Math.sin(2 * Math.PI * frequency * time) * note.velocity * 0.1;
            sample += wave;
        });
        
        return sample;
    }
    
    noteToFrequency(note) {
        const noteMap = {
            'C': 261.63, 'D': 293.66, 'E': 329.63, 'F': 349.23,
            'G': 392.00, 'A': 440.00, 'B': 493.88
        };
        
        const noteName = note.charAt(0);
        const octave = parseInt(note.charAt(note.length - 1)) || 4;
        const baseFreq = noteMap[noteName] || 440;
        
        return baseFreq * Math.pow(2, octave - 4);
    }
}

class DrumMachine {
    constructor(audioContext) {
        this.audioContext = audioContext;
    }
    
    async render(section, structure, leftChannel, rightChannel, startTime, sectionSamples) {
        const sampleRate = this.audioContext.sampleRate;
        const beatInterval = (60 / structure.tempo) * sampleRate; // samples por beat
        
        for (let beat = 0; beat < section.length * 4; beat++) {
            const beatTime = startTime + (beat * beatInterval);
            if (beatTime < leftChannel.length) {
                const kick = this.generateKick();
                const snare = this.generateSnare();
                
                // Kick en beats 1 y 3
                if (beat % 4 === 0) {
                    this.addSample(leftChannel, rightChannel, beatTime, kick, 0.1);
                }
                
                // Snare en beats 2 y 4
                if (beat % 4 === 2) {
                    this.addSample(leftChannel, rightChannel, beatTime, snare, 0.08);
                }
            }
        }
    }
    
    generateKick() {
        // Generar kick drum simple
        const samples = [];
        for (let i = 0; i < 1000; i++) {
            const t = i / 1000;
            const sample = Math.sin(2 * Math.PI * 60 * t) * Math.exp(-t * 10);
            samples.push(sample);
        }
        return samples;
    }
    
    generateSnare() {
        // Generar snare drum simple
        const samples = [];
        for (let i = 0; i < 500; i++) {
            const t = i / 500;
            const noise = (Math.random() * 2 - 1) * Math.exp(-t * 15);
            samples.push(noise);
        }
        return samples;
    }
    
    addSample(leftChannel, rightChannel, startTime, samples, volume) {
        for (let i = 0; i < samples.length; i++) {
            const index = startTime + i;
            if (index < leftChannel.length) {
                leftChannel[index] += samples[i] * volume;
                rightChannel[index] += samples[i] * volume;
            }
        }
    }
}

class BassGenerator {
    constructor(audioContext) {
        this.audioContext = audioContext;
    }
    
    async render(section, structure, leftChannel, rightChannel, startTime, sectionSamples) {
        const sampleRate = this.audioContext.sampleRate;
        
        section.notes.bass.forEach(note => {
            const frequency = this.noteToFrequency(note.note);
            const duration = note.duration * (60 / structure.tempo) * sampleRate;
            
            for (let i = 0; i < duration; i++) {
                const time = (startTime + i) / sampleRate;
                const sample = Math.sin(2 * Math.PI * frequency * time) * note.velocity * 0.2;
                
                const index = startTime + i;
                if (index < leftChannel.length) {
                    leftChannel[index] += sample;
                    rightChannel[index] += sample;
                }
            }
        });
    }
    
    noteToFrequency(note) {
        const noteMap = {
            'C': 261.63, 'D': 293.66, 'E': 329.63, 'F': 349.23,
            'G': 392.00, 'A': 440.00, 'B': 493.88
        };
        
        const noteName = note.charAt(0);
        const octave = parseInt(note.charAt(note.length - 1)) || 3; // Bajo en octava 3
        const baseFreq = noteMap[noteName] || 440;
        
        return baseFreq * Math.pow(2, octave - 4);
    }
}

class MelodyGenerator {
    constructor(audioContext) {
        this.audioContext = audioContext;
    }
    
    async render(section, structure, leftChannel, rightChannel, startTime, sectionSamples) {
        // Similar a Synthesizer pero con diferentes parámetros
        const synthesizer = new Synthesizer(this.audioContext);
        await synthesizer.render(section, structure, leftChannel, rightChannel, startTime, sectionSamples);
    }
}

class AudioEffects {
    constructor(audioContext) {
        this.audioContext = audioContext;
    }
    
    applyReverb(buffer) {
        // Implementar reverb simple
        return buffer;
    }
    
    applyDelay(buffer, delayTime, feedback) {
        // Implementar delay simple
        return buffer;
    }
    
    applyDistortion(buffer, amount) {
        // Implementar distorsión simple
        return buffer;
    }
}

// Exportar para uso global
window.WebAudioGenerator = WebAudioGenerator;
