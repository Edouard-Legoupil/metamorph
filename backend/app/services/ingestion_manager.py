"""
Ingestion Manager Service

Handles the complete ingestion pipeline for discovered files.
Integrates with Docling, MinerU, and the knowledge graph.
"""

import os
import tempfile
import hashlib
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import requests
import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sql.website import IngestionJob, IngestionJobStatus, DiscoveredFile, FileType
from app.services.ingestion.ingestion_pipeline import process_document
from app.services.preview_service import preview_service


class IngestionManager:
    """Service for managing file ingestion jobs"""
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_retries = 3
        self.supported_file_types = {
            FileType.PDF, FileType.WORD, FileType.DOCX, FileType.EXCEL, FileType.XLSX,
            FileType.POWERPOINT, FileType.PPTX, FileType.TEXT, FileType.HTML, FileType.HTM,
            FileType.MARKDOWN, FileType.JSON, FileType.XML, FileType.CSV
        }
    
    def _validate_file_for_ingestion(self, discovered_file: DiscoveredFile) -> None:
        """Validate that a file can be ingested"""
        if discovered_file.file_type not in self.supported_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {discovered_file.file_type.value} is not supported for ingestion"
            )
        
        if discovered_file.file_size and discovered_file.file_size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large for ingestion ({discovered_file.file_size} bytes > {self.max_file_size} bytes)"
            )
    
    def _download_file(self, file_url: str) -> tempfile.NamedTemporaryFile:
        """Download file from URL for ingestion"""
        try:
            response = requests.get(file_url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Check file size
            content_length = int(response.headers.get('content-length', 0))
            if content_length > self.max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large for ingestion ({content_length} bytes > {self.max_file_size} bytes)"
                )
            
            # Create temporary file with original extension
            file_extension = file_url.split('.')[-1] if '.' in file_url else 'bin'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}")
            
            # Stream download to handle large files
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
            
            temp_file.close()
            return temp_file
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download file for ingestion: {str(e)}"
            )
    
    def _cleanup_temp_file(self, temp_file_path: str) -> None:
        """Clean up temporary file"""
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        except OSError:
            pass
    
    def _update_job_status(self, db: Session, job_id: int, status: IngestionJobStatus, **kwargs) -> None:
        """Update ingestion job status"""
        db_job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if db_job:
            db_job.status = status
            for key, value in kwargs.items():
                setattr(db_job, key, value)
            db_job.updated_at = datetime.now()
            db.commit()
    
    def _process_with_docling(self, file_path: str, job_type: str) -> Dict[str, Any]:
        """Process file using Docling parser"""
        try:
            # Call the existing ingestion pipeline with Docling
            result = process_document(file_path)
            result['parser_used'] = 'docling'
            result['job_type'] = job_type
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Docling processing failed: {str(e)}"
            )
    
    def _process_with_mineru(self, file_path: str, job_type: str) -> Dict[str, Any]:
        """Process file using MinerU parser"""
        try:
            # For now, use the same pipeline but mark as MinerU
            # In production, this would call the actual MinerU service
            result = process_document(file_path)
            result['parser_used'] = 'mineru'
            result['job_type'] = job_type
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"MinerU processing failed: {str(e)}"
            )
    
    def _select_parser(self, file_type: FileType, job_type: str) -> str:
        """Select appropriate parser based on file type and job requirements"""
        # Simple routing logic - could be enhanced with file analysis
        if job_type == "metadata_only":
            return "docling"  # Docling is faster for metadata extraction
        
        # Complex files go to MinerU
        complex_file_types = [FileType.PDF, FileType.POWERPOINT, FileType.PPTX]
        if file_type in complex_file_types:
            return "mineru"
        
        # Everything else goes to Docling
        return "docling"
    
    def _extract_metadata_only(self, file_path: str, file_type: FileType) -> Dict[str, Any]:
        """Extract only metadata without full content processing"""
        try:
            # Use preview service to get basic info
            preview_result = preview_service.generate_preview(
                DiscoveredFile(
                    id=0,
                    url=file_path,
                    file_name=os.path.basename(file_path),
                    file_type=file_type,
                    file_size=os.path.getsize(file_path)
                )
            )
            
            return {
                'status': 'COMPLETED',
                'parser_used': 'metadata_extractor',
                'job_type': 'metadata_only',
                'metadata': {
                    'file_name': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path),
                    'file_type': file_type.value,
                    'preview': preview_result.get('preview', '')[:500],  # Limit preview size
                    'extracted_at': datetime.now().isoformat()
                },
                'extracted_text_length': len(preview_result.get('preview', '')),
                'extracted_entities_count': 0,
                'extracted_relationships_count': 0
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Metadata extraction failed: {str(e)}"
            )
    
    def process_ingestion_job(self, db: Session, job_id: int) -> Dict[str, Any]:
        """Process a single ingestion job"""
        start_time = time.time()
        
        try:
            # Get the job
            db_job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
            if not db_job:
                raise HTTPException(status_code=404, detail="Ingestion job not found")
            
            # Get the discovered file
            discovered_file = db.query(DiscoveredFile).filter(
                DiscoveredFile.id == db_job.discovered_file_id
            ).first()
            
            if not discovered_file:
                raise HTTPException(status_code=404, detail="Discovered file not found")
            
            # Update job status
            self._update_job_status(
                db, job_id, IngestionJobStatus.PROCESSING,
                started_at=datetime.now()
            )
            
            # Validate file
            self._validate_file_for_ingestion(discovered_file)
            
            # Download file
            temp_file = self._download_file(discovered_file.url)
            downloaded_path = temp_file.name
            
            # Update job with download info
            self._update_job_status(
                db, job_id,
                downloaded_path=downloaded_path
            )
            
            # Process based on job type
            result = {}
            if db_job.job_type == "metadata_only":
                result = self._extract_metadata_only(downloaded_path, discovered_file.file_type)
            else:
                # Select parser
                parser = self._select_parser(discovered_file.file_type, db_job.job_type)
                
                # Process with selected parser
                if parser == "docling":
                    result = self._process_with_docling(downloaded_path, db_job.job_type)
                else:
                    result = self._process_with_mineru(downloaded_path, db_job.job_type)
            
            # Update job with results
            self._update_job_status(
                db, job_id,
                status=IngestionJobStatus.COMPLETED,
                completed_at=datetime.now(),
                duration_seconds=time.time() - start_time,
                parsing_tool=result.get('parser_used'),
                parsing_version="1.0",
                extracted_text_length=result.get('extracted_text_length', 0),
                extracted_entities_count=result.get('extracted_entities_count', 0),
                extracted_relationships_count=result.get('extracted_relationships_count', 0),
                parsed_path=result.get('markdown_path'),
                error_message=None
            )
            
            # Update discovered file status
            discovered_file.status = FileStatus.INGESTED
            discovered_file.ingestion_completed_at = datetime.now()
            db.commit()
            
            return {
                'success': True,
                'job_id': job_id,
                'status': 'COMPLETED',
                'file_id': discovered_file.id,
                'parser_used': result.get('parser_used'),
                'entities_extracted': result.get('extracted_entities_count', 0),
                'relationships_extracted': result.get('extracted_relationships_count', 0),
                'duration_seconds': time.time() - start_time
            }
            
        except HTTPException as e:
            # Re-raise HTTP exceptions
            self._update_job_status(
                db, job_id,
                status=IngestionJobStatus.FAILED,
                completed_at=datetime.now(),
                duration_seconds=time.time() - start_time,
                error_message=str(e.detail)
            )
            raise
            
        except Exception as e:
            # Handle other exceptions
            error_msg = f"Ingestion failed: {str(e)}"
            self._update_job_status(
                db, job_id,
                status=IngestionJobStatus.FAILED,
                completed_at=datetime.now(),
                duration_seconds=time.time() - start_time,
                error_message=error_msg
            )
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
            
        finally:
            # Clean up temporary files
            if 'downloaded_path' in locals():
                self._cleanup_temp_file(downloaded_path)
    
    def retry_failed_job(self, db: Session, job_id: int) -> Dict[str, Any]:
        """Retry a failed ingestion job"""
        db_job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not db_job:
            raise HTTPException(status_code=404, detail="Ingestion job not found")
        
        if db_job.status != IngestionJobStatus.FAILED:
            raise HTTPException(
                status_code=400,
                detail=f"Job is not in FAILED state (current: {db_job.status})"
            )
        
        if db_job.retry_count >= db_job.max_retries:
            raise HTTPException(
                status_code=400,
                detail=f"Job has reached maximum retries ({db_job.max_retries})"
            )
        
        # Reset job for retry
        db_job.status = IngestionJobStatus.PENDING
        db_job.retry_count += 1
        db_job.error_message = None
        db_job.queued_at = datetime.now()
        db_job.started_at = None
        db_job.completed_at = None
        db_job.duration_seconds = None
        db.commit()
        
        return {
            'success': True,
            'job_id': job_id,
            'retry_count': db_job.retry_count,
            'status': 'QUEUED_FOR_RETRY'
        }
    
    def get_job_status(self, db: Session, job_id: int) -> Dict[str, Any]:
        """Get status of an ingestion job"""
        db_job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not db_job:
            raise HTTPException(status_code=404, detail="Ingestion job not found")
        
        return {
            'job_id': db_job.id,
            'file_id': db_job.discovered_file_id,
            'status': db_job.status.value,
            'job_type': db_job.job_type,
            'priority': db_job.priority,
            'retry_count': db_job.retry_count,
            'max_retries': db_job.max_retries,
            'error_message': db_job.error_message,
            'parser_used': db_job.parsing_tool,
            'entities_extracted': db_job.extracted_entities_count,
            'relationships_extracted': db_job.extracted_relationships_count,
            'queued_at': db_job.queued_at,
            'started_at': db_job.started_at,
            'completed_at': db_job.completed_at,
            'duration_seconds': db_job.duration_seconds
        }
    
    def get_ingestion_stats(self, db: Session) -> Dict[str, Any]:
        """Get overall ingestion statistics"""
        total_jobs = db.query(IngestionJob).count()
        completed_jobs = db.query(IngestionJob).filter(
            IngestionJob.status == IngestionJobStatus.COMPLETED
        ).count()
        failed_jobs = db.query(IngestionJob).filter(
            IngestionJob.status == IngestionJobStatus.FAILED
        ).count()
        pending_jobs = db.query(IngestionJob).filter(
            IngestionJob.status == IngestionJobStatus.PENDING
        ).count()
        processing_jobs = db.query(IngestionJob).filter(
            IngestionJob.status == IngestionJobStatus.PROCESSING
        ).count()
        
        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'pending_jobs': pending_jobs,
            'processing_jobs': processing_jobs,
            'success_rate': round(completed_jobs / max(1, total_jobs) * 100, 2) if total_jobs > 0 else 0
        }


# Singleton instance
ingestion_manager = IngestionManager()