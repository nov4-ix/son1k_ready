"""
Audio serving router for Son1k system
Handles audio file downloads, streaming, and metadata
"""

import os
import mimetypes
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Response, Query
from fastapi.responses import FileResponse, StreamingResponse
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/audio", tags=["audio"])

# Audio storage directory
AUDIO_DIR = Path("generated_audio")
AUDIO_DIR.mkdir(exist_ok=True)

@router.get("/files")
async def list_audio_files():
    """List all available audio files"""
    try:
        files = []
        for file_path in AUDIO_DIR.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                file_info = {
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "created": file_path.stat().st_ctime,
                    "url": f"/api/audio/download/{file_path.name}"
                }
                files.append(file_info)
        
        files.sort(key=lambda x: x['created'], reverse=True)
        return {"files": files, "count": len(files)}
        
    except Exception as e:
        logger.error(f"Failed to list audio files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_audio_file(filename: str):
    """Download a specific audio file"""
    try:
        file_path = AUDIO_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid file")
        
        # Check file extension
        if file_path.suffix.lower() not in ['.mp3', '.wav', '.m4a']:
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        # Determine content type
        content_type = mimetypes.guess_type(str(file_path))[0] or "audio/mpeg"
        
        return FileResponse(
            path=str(file_path),
            media_type=content_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream/{filename}")
async def stream_audio_file(filename: str, range_header: Optional[str] = None):
    """Stream audio file with range support for HTML5 audio player"""
    try:
        file_path = AUDIO_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid file")
        
        if file_path.suffix.lower() not in ['.mp3', '.wav', '.m4a']:
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        file_size = file_path.stat().st_size
        content_type = mimetypes.guess_type(str(file_path))[0] or "audio/mpeg"
        
        # Handle range requests for streaming
        start = 0
        end = file_size - 1
        
        # Parse range header if present
        if range_header:
            range_match = range_header.replace('bytes=', '').split('-')
            if len(range_match) == 2:
                try:
                    start = int(range_match[0]) if range_match[0] else 0
                    end = int(range_match[1]) if range_match[1] else file_size - 1
                except ValueError:
                    pass
        
        # Create streaming response
        def generate_file_stream():
            with open(file_path, 'rb') as f:
                f.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        headers = {
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(end - start + 1),
            'Cache-Control': 'no-cache'
        }
        
        status_code = 206 if range_header else 200
        
        return StreamingResponse(
            generate_file_stream(),
            status_code=status_code,
            headers=headers,
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stream file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metadata/{filename}")
async def get_audio_metadata(filename: str):
    """Get metadata for an audio file"""
    try:
        file_path = AUDIO_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        stat = file_path.stat()
        
        metadata = {
            "filename": filename,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "extension": file_path.suffix.lower(),
            "content_type": mimetypes.guess_type(str(file_path))[0] or "audio/mpeg"
        }
        
        # Try to load additional metadata if available
        metadata_file = file_path.with_suffix('.json')
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    additional_metadata = json.load(f)
                    metadata.update(additional_metadata)
            except Exception as e:
                logger.warning(f"Failed to load metadata file for {filename}: {e}")
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metadata for {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{filename}")
async def delete_audio_file(filename: str):
    """Delete an audio file"""
    try:
        file_path = AUDIO_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Delete main file
        file_path.unlink()
        
        # Delete metadata file if exists
        metadata_file = file_path.with_suffix('.json')
        if metadata_file.exists():
            metadata_file.unlink()
        
        logger.info(f"Deleted audio file: {filename}")
        return {"message": f"Audio file {filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_files(max_files: int = Query(50, description="Maximum number of files to keep")):
    """Clean up old audio files, keeping only the most recent ones"""
    try:
        files = []
        for file_path in AUDIO_DIR.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                files.append((file_path, file_path.stat().st_ctime))
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x[1], reverse=True)
        
        deleted_count = 0
        if len(files) > max_files:
            # Delete oldest files
            for file_path, _ in files[max_files:]:
                try:
                    file_path.unlink()
                    
                    # Delete associated metadata
                    metadata_file = file_path.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    deleted_count += 1
                    logger.info(f"Cleaned up old file: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path.name}: {e}")
        
        return {
            "message": f"Cleanup completed. Deleted {deleted_count} old files.",
            "remaining_files": len(files) - deleted_count,
            "deleted_files": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))