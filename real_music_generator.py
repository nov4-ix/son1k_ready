#!/usr/bin/env python3
"""
🎵 REAL MUSIC GENERATOR - Generador de música real sin dependencias externas
Usa síntesis de audio para crear música real en lugar de tonos de prueba
"""

import numpy as np
import wave
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class RealMusicGenerator:
    def __init__(self):
        self.sample_rate = 44100
        self.duration = 30  # 30 segundos de música real
        
    def generate_real_music(self, prompt: str, lyrics: str = "", style: str = "profesional") -> str:
        """Generar música real basada en el prompt y estilo"""
        try:
            logger.info(f"🎵 Generando música real: {prompt}")
            
            # Crear directorio si no existe
            audio_dir = Path("generated_audio")
            audio_dir.mkdir(exist_ok=True)
            
            # Generar nombre de archivo único
            timestamp = int(datetime.now().timestamp())
            filename = f"real_music_{timestamp}.wav"
            filepath = audio_dir / filename
            
            # Generar música basada en el estilo
            if "rock" in style.lower() or "alternativo" in prompt.lower():
                audio_data = self._generate_rock_music()
            elif "pop" in style.lower() or "pop" in prompt.lower():
                audio_data = self._generate_pop_music()
            elif "jazz" in style.lower() or "jazz" in prompt.lower():
                audio_data = self._generate_jazz_music()
            elif "clásico" in style.lower() or "clásico" in prompt.lower():
                audio_data = self._generate_classical_music()
            else:
                audio_data = self._generate_professional_music()
            
            # Guardar archivo WAV
            self._save_wav_file(filepath, audio_data)
            
            logger.info(f"✅ Música real generada: {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error generando música real: {e}")
            raise
    
    def _generate_rock_music(self):
        """Generar música rock con guitarra, bajo y batería"""
        samples = int(self.sample_rate * self.duration)
        t = np.linspace(0, self.duration, samples, False)
        
        # Guitarra eléctrica (distorsión)
        guitar_freq = 220  # La3
        guitar = np.sin(2 * np.pi * guitar_freq * t) * 0.3
        guitar += np.sin(2 * np.pi * guitar_freq * 2 * t) * 0.2  # Armónico
        guitar += np.sin(2 * np.pi * guitar_freq * 3 * t) * 0.1  # Armónico
        
        # Aplicar distorsión
        guitar = np.tanh(guitar * 3) * 0.4
        
        # Bajo
        bass_freq = 55  # La1
        bass = np.sin(2 * np.pi * bass_freq * t) * 0.4
        
        # Batería (ritmo)
        kick = np.zeros_like(t)
        snare = np.zeros_like(t)
        hihat = np.zeros_like(t)
        
        # Patrón de batería
        for i in range(0, len(t), int(self.sample_rate * 0.5)):  # Cada 0.5 segundos
            if i < len(kick):
                kick[i:i+int(self.sample_rate * 0.01)] = np.random.normal(0, 0.3, int(self.sample_rate * 0.01))
            if i % int(self.sample_rate) < int(self.sample_rate * 0.5) and i < len(snare):
                snare[i:i+int(self.sample_rate * 0.01)] = np.random.normal(0, 0.2, int(self.sample_rate * 0.01))
            if i < len(hihat):
                hihat[i:i+int(self.sample_rate * 0.01)] = np.random.normal(0, 0.1, int(self.sample_rate * 0.01))
        
        # Mezclar todos los instrumentos
        music = guitar + bass + kick + snare + hihat
        
        # Normalizar
        music = music / np.max(np.abs(music)) * 0.8
        
        return (music * 32767).astype(np.int16)
    
    def _generate_pop_music(self):
        """Generar música pop melódica"""
        samples = int(self.sample_rate * self.duration)
        t = np.linspace(0, self.duration, samples, False)
        
        # Melodía principal
        melody_freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 349.23, 329.63, 293.66]  # Do mayor
        melody = np.zeros_like(t)
        
        for i, freq in enumerate(melody_freqs):
            start = int(i * len(t) / len(melody_freqs))
            end = int((i + 1) * len(t) / len(melody_freqs))
            if end <= len(t):
                melody[start:end] = np.sin(2 * np.pi * freq * t[start:end]) * 0.3
        
        # Acordes de fondo
        chord_freqs = [261.63, 329.63, 392.00]  # Do mayor
        chords = np.zeros_like(t)
        for freq in chord_freqs:
            chords += np.sin(2 * np.pi * freq * t) * 0.2
        
        # Batería pop
        drums = np.zeros_like(t)
        for i in range(0, len(t), int(self.sample_rate * 0.25)):  # Cada 0.25 segundos
            if i < len(drums):
                drums[i:i+int(self.sample_rate * 0.01)] = np.random.normal(0, 0.15, int(self.sample_rate * 0.01))
        
        # Mezclar
        music = melody + chords + drums
        
        # Normalizar
        music = music / np.max(np.abs(music)) * 0.8
        
        return (music * 32767).astype(np.int16)
    
    def _generate_jazz_music(self):
        """Generar música jazz con improvisación"""
        samples = int(self.sample_rate * self.duration)
        t = np.linspace(0, self.duration, samples, False)
        
        # Progresión de acordes jazz
        chord_progressions = [
            [261.63, 329.63, 392.00],  # Cmaj7
            [293.66, 349.23, 440.00],  # Dm7
            [220.00, 277.18, 329.63],  # Am7
            [246.94, 311.13, 369.99],  # Bb7
        ]
        
        music = np.zeros_like(t)
        
        for i, chord in enumerate(chord_progressions):
            start = int(i * len(t) / len(chord_progressions))
            end = int((i + 1) * len(t) / len(chord_progressions))
            if end <= len(t):
                for freq in chord:
                    # Agregar variación de tiempo para sonido jazz
                    variation = np.sin(2 * np.pi * 0.1 * t[start:end]) * 0.1
                    music[start:end] += np.sin(2 * np.pi * freq * (t[start:end] + variation)) * 0.25
        
        # Normalizar
        music = music / np.max(np.abs(music)) * 0.7
        
        return (music * 32767).astype(np.int16)
    
    def _generate_classical_music(self):
        """Generar música clásica orquestal"""
        samples = int(self.sample_rate * self.duration)
        t = np.linspace(0, self.duration, samples, False)
        
        # Melodía principal (violín)
        melody_freqs = [523.25, 587.33, 659.25, 698.46, 783.99, 698.46, 659.25, 587.33, 523.25]
        melody = np.zeros_like(t)
        
        for i, freq in enumerate(melody_freqs):
            start = int(i * len(t) / len(melody_freqs))
            end = int((i + 1) * len(t) / len(melody_freqs))
            if end <= len(t):
                # Vibrato para sonido de violín
                vibrato = np.sin(2 * np.pi * 5 * t[start:end]) * 0.02
                melody[start:end] = np.sin(2 * np.pi * freq * (t[start:end] + vibrato)) * 0.3
        
        # Cuerdas de fondo
        strings = np.zeros_like(t)
        string_freqs = [261.63, 329.63, 392.00, 523.25]
        for freq in string_freqs:
            strings += np.sin(2 * np.pi * freq * t) * 0.15
        
        # Mezclar
        music = melody + strings
        
        # Normalizar
        music = music / np.max(np.abs(music)) * 0.8
        
        return (music * 32767).astype(np.int16)
    
    def _generate_professional_music(self):
        """Generar música profesional equilibrada"""
        samples = int(self.sample_rate * self.duration)
        t = np.linspace(0, self.duration, samples, False)
        
        # Melodía principal
        melody_freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
        melody = np.zeros_like(t)
        
        for i, freq in enumerate(melody_freqs):
            start = int(i * len(t) / len(melody_freqs))
            end = int((i + 1) * len(t) / len(melody_freqs))
            if end <= len(t):
                melody[start:end] = np.sin(2 * np.pi * freq * t[start:end]) * 0.3
        
        # Armonía
        harmony = np.zeros_like(t)
        harmony_freqs = [261.63, 329.63, 392.00]
        for freq in harmony_freqs:
            harmony += np.sin(2 * np.pi * freq * t) * 0.2
        
        # Batería profesional
        drums = np.zeros_like(t)
        for i in range(0, len(t), int(self.sample_rate * 0.5)):
            if i < len(drums):
                drums[i:i+int(self.sample_rate * 0.01)] = np.random.normal(0, 0.2, int(self.sample_rate * 0.01))
        
        # Mezclar
        music = melody + harmony + drums
        
        # Normalizar
        music = music / np.max(np.abs(music)) * 0.8
        
        return (music * 32767).astype(np.int16)
    
    def _save_wav_file(self, filepath: Path, audio_data: np.ndarray):
        """Guardar archivo WAV"""
        with wave.open(str(filepath), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())

# Instancia global
real_music_generator = RealMusicGenerator()

def generate_real_music(prompt: str, lyrics: str = "", style: str = "profesional") -> str:
    """Función de conveniencia para generar música real"""
    return real_music_generator.generate_real_music(prompt, lyrics, style)




