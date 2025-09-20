"""
Audio Processing and Storage Handler
Downloads, converts, and stores audio files from Suno generations
"""
import os
import time
import logging
import requests
import hashlib
from typing import Dict, List, Optional
from urllib.parse import urlparse
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioProcessor:
    """Handles audio file download, processing, and storage"""
    
    def __init__(self, storage_base_path: str = "/tmp/son1k_audio"):
        self.storage_path = Path(storage_base_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        
        # Configure session with headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def process_generation_results(self, generation_results: Dict) -> Dict:
        """
        Process generation results by downloading and storing audio files
        
        Args:
            generation_results: Results from Suno automation containing audio URLs
            
        Returns:
            Dictionary with processed file paths and metadata
        """
        if not generation_results.get("success"):
            return generation_results
            
        try:
            logger.info("🎵 Processing generation results...")
            
            audio_urls = generation_results.get("audio_urls", [])
            if not audio_urls:
                return {"success": False, "error": "No audio URLs to process"}
            
            processed_files = []
            generation_id = generation_results.get("generation_id", f"gen_{int(time.time())}")
            
            # Create generation-specific directory
            gen_dir = self.storage_path / generation_id
            gen_dir.mkdir(exist_ok=True)
            
            for i, audio_url in enumerate(audio_urls):
                logger.info(f"📥 Downloading audio {i+1}/{len(audio_urls)}: {audio_url}")
                
                # Download audio file
                download_result = self._download_audio_file(audio_url, gen_dir, f"track_{i+1}")
                
                if download_result["success"]:
                    processed_files.append(download_result)
                    logger.info(f"✅ Downloaded: {download_result['file_path']}")
                else:
                    logger.error(f"❌ Failed to download: {audio_url}")
            
            if processed_files:
                # Select primary file (usually the first one)
                primary_file = processed_files[0]
                
                return {
                    "success": True,
                    "generation_id": generation_id,
                    "primary_file": primary_file,
                    "all_files": processed_files,
                    "file_count": len(processed_files),
                    "metadata": generation_results.get("metadata", {}),
                    "storage_directory": str(gen_dir)
                }
            else:
                return {"success": False, "error": "Failed to download any audio files"}
                
        except Exception as e:
            logger.error(f"❌ Error processing generation results: {e}")
            return {"success": False, "error": str(e)}
    
    def _download_audio_file(self, url: str, output_dir: Path, filename_base: str) -> Dict:
        """Download audio file from URL"""
        try:
            # Parse URL to get file extension
            parsed_url = urlparse(url)
            original_ext = Path(parsed_url.path).suffix
            
            # Default to .mp3 if no extension found
            if not original_ext:
                original_ext = ".mp3"
            
            # Create filename
            filename = f"{filename_base}{original_ext}"
            file_path = output_dir / filename
            
            # Download with streaming to handle large files
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'audio' not in content_type and 'octet-stream' not in content_type:
                logger.warning(f"⚠️ Unexpected content type: {content_type}")
            
            # Download file
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
            
            # Verify download
            if not file_path.exists() or file_path.stat().st_size == 0:
                return {"success": False, "error": "Downloaded file is empty"}
            
            # Calculate file hash for integrity
            file_hash = self._calculate_file_hash(file_path)
            
            # Get file metadata
            file_size = file_path.stat().st_size
            
            logger.info(f"✅ Downloaded {file_size} bytes to {file_path}")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "filename": filename,
                "file_size": file_size,
                "file_hash": file_hash,
                "original_url": url,
                "content_type": content_type,
                "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except requests.RequestException as e:
            logger.error(f"❌ Network error downloading {url}: {e}")
            return {"success": False, "error": f"Network error: {e}"}
            
        except Exception as e:
            logger.error(f"❌ Error downloading {url}: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file for integrity verification"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"⚠️ Could not calculate hash for {file_path}: {e}")
            return ""
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """Clean up old audio files to save disk space"""
        try:
            logger.info(f"🧹 Cleaning up files older than {max_age_hours} hours...")
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            deleted_count = 0
            
            for item in self.storage_path.iterdir():
                if item.is_dir():
                    # Check directory age
                    dir_age = current_time - item.stat().st_mtime
                    if dir_age > max_age_seconds:
                        # Delete directory and all contents
                        self._delete_directory(item)
                        deleted_count += 1
                        logger.info(f"🗑️ Deleted old directory: {item}")
                elif item.is_file():
                    # Check file age
                    file_age = current_time - item.stat().st_mtime
                    if file_age > max_age_seconds:
                        item.unlink()
                        deleted_count += 1
                        logger.info(f"🗑️ Deleted old file: {item}")
            
            logger.info(f"✅ Cleanup completed, deleted {deleted_count} items")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0
    
    def _delete_directory(self, directory: Path):
        """Recursively delete directory and all contents"""
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    self._delete_directory(item)
                else:
                    item.unlink()
            directory.rmdir()
        except Exception as e:
            logger.warning(f"⚠️ Error deleting directory {directory}: {e}")
    
    def get_storage_stats(self) -> Dict:
        """Get storage usage statistics"""
        try:
            total_size = 0
            file_count = 0
            directory_count = 0
            
            for item in self.storage_path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
                elif item.is_dir():
                    directory_count += 1
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "directory_count": directory_count,
                "storage_path": str(self.storage_path)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting storage stats: {e}")
            return {"error": str(e)}
    
    def upload_to_backend(self, file_path: str, backend_url: str) -> Dict:
        """Upload processed audio file to backend storage"""
        try:
            logger.info(f"📤 Uploading to backend: {file_path}")
            
            if not os.path.exists(file_path):
                return {"success": False, "error": "File not found"}
            
            # Prepare file upload
            with open(file_path, 'rb') as f:
                files = {'audio_file': f}
                
                # Upload to backend
                response = self.session.post(
                    f"{backend_url}/api/audio/upload",
                    files=files,
                    timeout=60
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Upload successful: {result}")
                return {"success": True, "backend_response": result}
                
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    def convert_audio_format(self, input_path: str, output_format: str = "mp3") -> Dict:
        """Convert audio to different format (requires ffmpeg)"""
        try:
            # This would require ffmpeg installation
            # For now, just return the original file
            logger.info(f"🔄 Audio format conversion requested: {output_format}")
            logger.warning("⚠️ Audio conversion not implemented (requires ffmpeg)")
            
            return {
                "success": True,
                "converted_path": input_path,
                "original_format": Path(input_path).suffix,
                "target_format": output_format,
                "note": "Conversion not implemented, returning original file"
            }
            
        except Exception as e:
            logger.error(f"❌ Audio conversion failed: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_audio_file(self, file_path: str) -> Dict:
        """Validate that downloaded file is a valid audio file"""
        try:
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File not found"}
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {"valid": False, "error": "File is empty"}
            
            # Basic validation by file extension and size
            path = Path(file_path)
            audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
            
            if path.suffix.lower() not in audio_extensions:
                return {"valid": False, "error": f"Unsupported file extension: {path.suffix}"}
            
            # Minimum size check (1KB)
            if file_size < 1024:
                return {"valid": False, "error": "File too small to be valid audio"}
            
            return {
                "valid": True,
                "file_size": file_size,
                "extension": path.suffix,
                "filename": path.name
            }
            
        except Exception as e:
            logger.error(f"❌ Audio validation failed: {e}")
            return {"valid": False, "error": str(e)}