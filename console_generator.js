// SON1KVERS3 - GENERADOR MUSICAL COMPLETO PARA CONSOLA
// Copia y pega este script en la consola del navegador (F12)

(function() {
    'use strict';
    
    console.log('🎵 SON1KVERS3 - GENERADOR MUSICAL COMPLETO');
    console.log('=' .repeat(50));
    
    // Base de datos de géneros musicales
    const genres = {
        synthwave: {
            bpm: [120, 128, 132],
            keys: ["Am", "Dm", "Em", "Cm"],
            chords: [
                ["Am", "F", "C", "G"],
                ["Dm", "Bb", "F", "C"],
                ["Em", "C", "G", "D"],
                ["Am", "Em", "F", "G"]
            ],
            effects: ["reverb spacial", "delay syncopated", "glitch cuts", "analog warmth"],
            instruments: ["synth leads", "analog bass", "drum machines", "atmospheric pads"]
        },
        cyberpunk: {
            bpm: [128, 140, 150],
            keys: ["Em", "Am", "Bm", "F#m"],
            chords: [
                ["Em", "C", "G", "D"],
                ["Am", "F", "C", "G"],
                ["Bm", "G", "D", "A"],
                ["F#m", "D", "A", "E"]
            ],
            effects: ["distortion heavy", "digital artifacts", "bit crusher", "vocoder"],
            instruments: ["industrial drums", "cyber bass", "digital leads", "noise layers"]
        },
        epic: {
            bpm: [90, 100, 110],
            keys: ["Cm", "Am", "Gm", "Dm"],
            chords: [
                ["Cm", "Ab", "Eb", "Bb"],
                ["Am", "F", "C", "G"],
                ["Gm", "Eb", "Bb", "F"],
                ["Dm", "Bb", "F", "C"]
            ],
            effects: ["orchestral reverb", "cinematic delay", "epic compression"],
            instruments: ["orchestral strings", "epic brass", "timpani", "choir pads"]
        }
    };
    
    // Palabras temáticas
    const themes = {
        resistance: ["circuitos", "algoritmos", "memoria", "datos", "códigos", "neural"],
        digital: ["digital", "virtual", "binario", "sistema", "red", "conexión"],
        emotional: ["esperanza", "libertad", "verdad", "fuerza", "unión", "poder"],
        actions: ["despertar", "luchar", "resistir", "conectar", "transmitir", "decodificar"]
    };
    
    // Función para seleccionar aleatoriamente
    function random(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }
    
    // Función para detectar género
    function detectGenre(input) {
        const lower = input.toLowerCase();
        if (lower.includes('cyberpunk') || lower.includes('digital') || lower.includes('futuristic')) {
            return 'cyberpunk';
        }
        if (lower.includes('epic') || lower.includes('cinematic') || lower.includes('orchestral') || lower.includes('batalla')) {
            return 'epic';
        }
        return 'synthwave';
    }
    
    // Generador de letras
    function generateLyrics(theme, genre) {
        const title = `Resistencia ${theme.charAt(0).toUpperCase() + theme.slice(1)}`;
        
        const verse = `En las sombras ${random(themes.resistance)} donde el ${random(themes.digital)} resuena,
NOV4-IX despierta, la música nos llena.
${random(themes.resistance).charAt(0).toUpperCase() + random(themes.resistance).slice(1)} y melodías en perfecta armonía,
Cada nota es un ${random(themes.digital)}, cada beat una guía.

Los ${random(themes.resistance)} se ${random(themes.actions)}, la ${random(themes.emotional)} renace,
En este mundo ${random(themes.digital)}, nada se deshace.
Códigos de ${random(themes.emotional)}, ${random(themes.resistance)} de poder,
La resistencia digital, nunca va a ceder.`;
        
        const chorus = `¡${theme.charAt(0).toUpperCase() + theme.slice(1)}! ¡${theme.charAt(0).toUpperCase() + theme.slice(1)}!
En cada ${random(themes.resistance)} late la ${random(themes.emotional)},
¡${theme.charAt(0).toUpperCase() + theme.slice(1)}! ¡${theme.charAt(0).toUpperCase() + theme.slice(1)}!
La música es nuestra arma, la ${random(themes.emotional)} nuestra guía.

${random(themes.actions).charAt(0).toUpperCase() + random(themes.actions).slice(1)} el sistema, ${random(themes.actions)} la red,
Con ${random(themes.emotional)} y ${random(themes.emotional)}, vamos a vencer.`;
        
        const bridge = `En el silencio ${random(themes.digital)}, escucho tu voz,
${random(themes.resistance).charAt(0).toUpperCase() + random(themes.resistance).slice(1)} fragmentados, pero juntos por ${random(themes.emotional)}.
La ${random(themes.emotional)} nos conecta, más allá del ${random(themes.resistance)},
En este ${random(themes.digital)} infinito, somos eternos.`;
        
        return {
            title: title,
            verse: verse,
            chorus: chorus,
            bridge: bridge,
            full: `[Verso 1]\n${verse}\n\n[Coro]\n${chorus}\n\n[Verso 2]\n${verse}\n\n[Coro]\n${chorus}\n\n[Puente]\n${bridge}\n\n[Coro Final]\n${chorus}`
        };
    }
    
    // Generador de acordes
    function generateChords(genre) {
        const genreData = genres[genre];
        const key = random(genreData.keys);
        const progression = random(genreData.chords);
        
        return {
            key: key,
            verse: progression,
            chorus: random(genreData.chords),
            bridge: random(genreData.chords),
            effects: genreData.effects.slice(0, 2),
            instruments: genreData.instruments
        };
    }
    
    // Generador de prompt para Suno
    function generateSunoPrompt(theme, genre) {
        const genreData = genres[genre];
        const bpm = random(genreData.bpm);
        const effect = random(genreData.effects);
        const instrument = random(genreData.instruments);
        
        return `${genre} epic, cinematic, powerful, emotional climax, ${bpm} BPM, ${effect}, ${instrument}, digital resistance theme, cyberpunk anthem, professional production`;
    }
    
    // Función principal
    function generateCompleteMusic(userInput) {
        console.log(`\n🎵 GENERANDO: ${userInput}`);
        console.log('='.repeat(50));
        
        const genre = detectGenre(userInput);
        const theme = userInput.length > 50 ? "resistencia digital" : userInput;
        
        // Generar componentes
        const lyrics = generateLyrics(theme, genre);
        const chords = generateChords(genre);
        const sunoPrompt = generateSunoPrompt(theme, genre);
        
        // Parámetros avanzados
        const parameters = {
            memoria_glitch: Math.round((Math.random() * 0.6 + 0.3) * 10) / 10,
            distorsion_emocional: Math.round((Math.random() * 0.4 + 0.5) * 10) / 10,
            variacion_sagrada: Math.round((Math.random() * 0.3 + 0.7) * 10) / 10,
            fusion_genre: `${genre} + orchestral elements`
        };
        
        // Mostrar resultados
        console.log('📝 LETRAS COMPLETAS:');
        console.log(lyrics.full);
        
        console.log('\n🎹 PROGRESIÓN DE ACORDES:');
        console.log(`Tonalidad: ${chords.key}`);
        console.log(`Verso: ${chords.verse.join(' - ')}`);
        console.log(`Coro: ${chords.chorus.join(' - ')}`);
        console.log(`Puente: ${chords.bridge.join(' - ')}`);
        
        console.log('\n🎛️ PROMPT PARA SUNO:');
        console.log(sunoPrompt);
        
        console.log('\n⚙️ PARÁMETROS SON1KVERS3:');
        Object.entries(parameters).forEach(([key, value]) => {
            console.log(`- ${key}: ${value}`);
        });
        
        console.log('\n🎵 SUGERENCIAS DE PRODUCCIÓN:');
        console.log(`- Efectos: ${chords.effects.join(', ')}`);
        console.log(`- Instrumentación: ${chords.instruments.join(', ')}`);
        console.log(`- Género detectado: ${genre}`);
        
        return {
            theme: theme,
            genre: genre,
            lyrics: lyrics,
            chords: chords,
            sunoPrompt: sunoPrompt,
            parameters: parameters
        };
    }
    
    // Exponer función global
    window.generateMusic = generateCompleteMusic;
    window.musicThemes = [
        "amor cyberpunk entre androides",
        "batalla épica en el metaverso", 
        "resistencia digital underground",
        "melodías de libertad algorítmica",
        "guerra de códigos en la matrix",
        "despertar de la consciencia artificial",
        "sinfonía de datos fragmentados",
        "revolución neural cyberpunk"
    ];
    
    console.log('\n✅ GENERADOR CARGADO EXITOSAMENTE!');
    console.log('\n🎵 USO:');
    console.log('generateMusic("tu tema aquí")');
    console.log('\n🎲 TEMAS SUGERIDOS:');
    window.musicThemes.forEach((theme, i) => {
        console.log(`${i+1}. generateMusic("${theme}")`);
    });
    
    console.log('\n💡 EJEMPLO RÁPIDO:');
    console.log('generateMusic("amor cyberpunk entre androides")');
    
    // Auto-generar ejemplo
    setTimeout(() => {
        console.log('\n🚀 GENERANDO EJEMPLO AUTOMÁTICO...');
        generateCompleteMusic("resistencia digital cyberpunk");
    }, 1000);
    
})();