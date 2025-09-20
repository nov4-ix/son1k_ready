"""
Audio Post-Processing Pipeline
Professional audio enhancement and optimization for commercial deployment
"""
import os
import logging
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AudioPostProcessor:
    """Professional audio post-processing for commercial music generation"""
    
    def __init__(self):
        self.temp_dir = Path("/tmp/son1k_audio_processing")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Audio quality standards for different plans
        self.quality_presets = {
            'enterprise': {
                'sample_rate': 48000,
                'bit_depth': 24,
                'format': 'wav',
                'compression': False,
                'mastering': True,
                'eq_enhancement': True,
                'stereo_enhancement': True
            },
            'vip': {
                'sample_rate': 44100,
                'bit_depth': 24,
                'format': 'wav',
                'compression': True,
                'mastering': True,
                'eq_enhancement': True,
                'stereo_enhancement': False
            },
            'pro': {
                'sample_rate': 44100,
                'bit_depth': 16,
                'format': 'mp3',
                'compression': True,
                'mastering': False,
                'eq_enhancement': True,
                'stereo_enhancement': False
            },
            'free': {
                'sample_rate': 44100,
                'bit_depth': 16,
                'format': 'mp3',
                'compression': True,
                'mastering': False,
                'eq_enhancement': False,
                'stereo_enhancement': False
            }
        }
    
    def process_audio_files(self, job_id: str, audio_files: List[str], user_plan: str = 'free') -> Dict:
        """
        Process audio files with plan-specific quality settings
        
        Args:
            job_id: Job identifier
            audio_files: List of audio file paths
            user_plan: User plan (free, pro, vip, enterprise)
            
        Returns:
            Dictionary with processed files and metadata
        """
        logger.info(f"🎛️ Processing {len(audio_files)} audio files for {user_plan} plan...")
        
        try:
            preset = self.quality_presets.get(user_plan, self.quality_presets['free'])
            
            # Create processing directory
            processing_dir = self.temp_dir / f"job_{job_id}"
            processing_dir.mkdir(exist_ok=True)
            
            processed_files = []
            
            for idx, audio_file in enumerate(audio_files):
                if not os.path.exists(audio_file):
                    logger.warning(f"Audio file not found: {audio_file}")
                    continue
                
                logger.info(f"🎵 Processing file {idx + 1}/{len(audio_files)}: {Path(audio_file).name}")
                
                # Process individual file
                processed_file = self._process_single_file(
                    audio_file, 
                    processing_dir, 
                    f"track_{idx + 1}", 
                    preset
                )
                
                if processed_file:
                    processed_files.append(processed_file)
            
            # Generate playlist and metadata
            metadata = self._generate_metadata(job_id, processed_files, user_plan)
            
            logger.info(f"✅ Audio processing complete: {len(processed_files)} files processed")
            
            return {
                "success": True,
                "job_id": job_id,
                "user_plan": user_plan,
                "processed_files": processed_files,
                "file_count": len(processed_files),
                "total_duration": metadata.get("total_duration", 0),
                "metadata": metadata,
                "processing_quality": preset
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing audio files: {e}")
            return {
                "success": False,
                "error": str(e),
                "job_id": job_id
            }
    
    def _process_single_file(self, input_file: str, output_dir: Path, filename: str, preset: Dict) -> Optional[Dict]:
        """Process a single audio file with quality settings"""
        try:
            # Load audio with librosa
            y, sr = librosa.load(input_file, sr=preset['sample_rate'])
            duration = librosa.duration(y=y, sr=sr)
            
            # Apply audio enhancements based on preset
            if preset.get('eq_enhancement'):
                y = self._apply_eq_enhancement(y, sr)
            
            if preset.get('stereo_enhancement') and len(y.shape) == 1:
                y = self._apply_stereo_enhancement(y)
            
            if preset.get('mastering'):
                y = self._apply_mastering(y, sr)
            
            # Normalize audio
            y = librosa.util.normalize(y)
            
            # Save processed file
            output_format = preset['format']
            output_file = output_dir / f"{filename}.{output_format}"
            
            if output_format == 'wav':
                sf.write(
                    str(output_file), 
                    y, 
                    sr, 
                    subtype=f"PCM_{preset['bit_depth']}"
                )
            else:  # MP3
                # Convert to AudioSegment for MP3 export
                temp_wav = output_dir / f"{filename}_temp.wav"
                sf.write(str(temp_wav), y, sr)
                
                audio_segment = AudioSegment.from_wav(str(temp_wav))
                
                if preset.get('compression'):
                    audio_segment = normalize(audio_segment)
                    audio_segment = compress_dynamic_range(audio_segment)
                
                # Export as MP3 with quality settings
                bitrate = "320k" if preset.get('mastering') else "192k"
                audio_segment.export(
                    str(output_file),
                    format="mp3",
                    bitrate=bitrate,
                    parameters=["-q:a", "0"]  # Highest quality
                )
                
                # Clean up temp file
                temp_wav.unlink()
            
            # Generate file metadata
            file_info = {
                "file_path": str(output_file),
                "filename": output_file.name,
                "format": output_format,
                "duration": float(duration),
                "sample_rate": sr,
                "bit_depth": preset.get('bit_depth', 16),
                "file_size": output_file.stat().st_size,
                "processed_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Processed: {filename}.{output_format} ({duration:.1f}s)")
            return file_info
            
        except Exception as e:
            logger.error(f"❌ Error processing {filename}: {e}")
            return None
    
    def _apply_eq_enhancement(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Apply EQ enhancement to improve sound quality"""
        try:
            # Simple EQ: boost mids slightly, gentle high-end enhancement
            # This is a basic implementation - could be enhanced with actual EQ filters
            
            # Apply gentle high-pass filter to remove low-end rumble
            y_filtered = librosa.effects.preemphasis(y, coef=0.97)
            
            # Gentle compression-like effect using tanh
            y_enhanced = np.tanh(y_filtered * 1.2) * 0.9
            
            return y_enhanced
            
        except Exception as e:
            logger.warning(f"EQ enhancement failed: {e}")
            return y
    
    def _apply_stereo_enhancement(self, y: np.ndarray) -> np.ndarray:
        """Convert mono to enhanced stereo"""
        try:
            # Create stereo from mono with slight delay for width
            left = y
            right = np.roll(y, int(len(y) * 0.001))  # Very slight delay
            
            # Mix with original for natural sound
            left = 0.7 * y + 0.3 * left
            right = 0.7 * y + 0.3 * right
            
            return np.column_stack((left, right))
            
        except Exception as e:
            logger.warning(f"Stereo enhancement failed: {e}")
            return y
    
    def _apply_mastering(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Apply basic mastering effects"""
        try:
            # Gentle compression
            threshold = 0.8
            ratio = 4.0
            
            # Simple compression algorithm
            y_compressed = np.where(
                np.abs(y) > threshold,
                np.sign(y) * (threshold + (np.abs(y) - threshold) / ratio),
                y
            )
            
            # Gentle limiting to prevent clipping
            y_limited = np.tanh(y_compressed * 0.95)
            
            return y_limited
            
        except Exception as e:
            logger.warning(f"Mastering failed: {e}")
            return y
    
    def _generate_metadata(self, job_id: str, processed_files: List[Dict], user_plan: str) -> Dict:
        """Generate comprehensive metadata for processed audio"""
        try:
            total_duration = sum(file_info.get("duration", 0) for file_info in processed_files)
            total_size = sum(file_info.get("file_size", 0) for file_info in processed_files)
            
            metadata = {
                "job_id": job_id,
                "user_plan": user_plan,
                "processing_timestamp": datetime.now().isoformat(),
                "file_count": len(processed_files),
                "total_duration": round(total_duration, 2),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "quality_preset": self.quality_presets[user_plan],
                "files": processed_files
            }
            
            # Save metadata file
            metadata_file = self.temp_dir / f"job_{job_id}" / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error generating metadata: {e}")
            return {"error": str(e)}
    
    def create_audio_preview(self, file_path: str, duration: int = 30) -> Optional[str]:
        """Create a preview clip of the audio file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # Load audio
            y, sr = librosa.load(file_path, duration=duration)
            
            # Create preview file
            preview_path = file_path.replace('.', '_preview.')
            sf.write(preview_path, y, sr)
            
            logger.info(f"📻 Created preview: {Path(preview_path).name}")
            return preview_path
            
        except Exception as e:
            logger.error(f"Error creating preview: {e}")
            return None
    
    def cleanup_processing_files(self, job_id: str, keep_processed: bool = True):
        """Clean up temporary processing files"""
        try:
            processing_dir = self.temp_dir / f"job_{job_id}"
            
            if processing_dir.exists():
                if keep_processed:
                    # Only remove temp files, keep final processed files
                    for temp_file in processing_dir.glob("*_temp.*"):
                        temp_file.unlink()
                else:
                    # Remove entire processing directory
                    shutil.rmtree(processing_dir)
                
                logger.info(f"🧹 Cleaned up processing files for job {job_id}")
                
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
    
    def get_processing_stats(self) -> Dict:
        """Get audio processing statistics"""
        try:
            processing_dirs = list(self.temp_dir.glob("job_*"))
            
            stats = {
                "active_processing_jobs": len(processing_dirs),
                "temp_dir_size_mb": sum(
                    sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())
                    for dir_path in processing_dirs
                ) / (1024 * 1024),
                "supported_formats": ["wav", "mp3", "flac", "m4a"],
                "quality_presets": list(self.quality_presets.keys())
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {"error": str(e)}

# Global audio processor instance
audio_processor = AudioPostProcessor()

# Helper functions for easy import
def process_job_audio(job_id: str, audio_files: List[str], user_plan: str = 'free') -> Dict:
    """Process audio files for a job"""
    return audio_processor.process_audio_files(job_id, audio_files, user_plan)

def create_preview(file_path: str, duration: int = 30) -> Optional[str]:
    """Create audio preview"""
    return audio_processor.create_audio_preview(file_path, duration)

def cleanup_job_files(job_id: str, keep_processed: bool = True):
    """Clean up job processing files"""
    audio_processor.cleanup_processing_files(job_id, keep_processed)