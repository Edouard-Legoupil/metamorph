"""
Ingestion Logs Service

Handles logging, storage, and retrieval of ingestion process logs.
Supports log downloading, filtering, and analysis for debugging and auditing.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sql.website import IngestionJob, IngestionJobStatus


class IngestionLog:
    """Represents a log entry for an ingestion job"""
    
    def __init__(self, 
                 job_id: int, 
                 timestamp: str, 
                 level: str, 
                 message: str, 
                 context: Dict[str, Any] = None):
        self.job_id = job_id
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log to dictionary"""
        return {
            "job_id": self.job_id,
            "timestamp": self.timestamp,
            "level": self.level,
            "message": self.message,
            "context": self.context
        }
    
    def to_json(self) -> str:
        """Convert log to JSON string"""
        return json.dumps(self.to_dict())


class IngestionLogsService:
    """Service for managing ingestion logs"""
    
    def __init__(self):
        self.logs_dir = Path("/tmp/ingestion_logs")
        self.logs_dir.mkdir(exist_ok=True)
        self.max_log_size = 10 * 1024 * 1024  # 10MB per log file
        
        # Configure logging
        self.logger = logging.getLogger("ingestion_logs")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = self.logs_dir / "ingestion.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s - %(context)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def _get_job_log_file(self, job_id: int) -> Path:
        """Get log file path for a specific job"""
        return self.logs_dir / f"job_{job_id}.log"
    
    def log_message(
        self, 
        job_id: int, 
        level: str, 
        message: str, 
        context: Dict[str, Any] = None
    ) -> IngestionLog:
        """Log a message for an ingestion job"""
        log_entry = IngestionLog(
            job_id=job_id,
            timestamp=datetime.utcnow().isoformat(),
            level=level,
            message=message,
            context=context or {}
        )
        
        # Log to file
        log_file = self._get_job_log_file(job_id)
        
        # Create log file if it doesn't exist
        if not log_file.exists():
            log_file.touch()
            # Write header
            with open(log_file, 'w') as f:
                f.write("# Ingestion Job Log\n")
                f.write(f"# Job ID: {job_id}\n")
                f.write(f"# Started: {datetime.utcnow().isoformat()}\n")
                f.write("# Format: [TIMESTAMP] [LEVEL] message - context\n\n")
        
        # Append log entry
        log_line = f"[{log_entry.timestamp}] [{log_entry.level}] {log_entry.message}"
        if log_entry.context:
            log_line += f" - {json.dumps(log_entry.context)}"
        log_line += "\n"
        
        with open(log_file, 'a') as f:
            f.write(log_line)
        
        # Also log using standard logging
        extra = {"context": log_entry.context, "job_id": job_id}
        if level == "INFO":
            self.logger.info(log_entry.message, extra=extra)
        elif level == "WARNING":
            self.logger.warning(log_entry.message, extra=extra)
        elif level == "ERROR":
            self.logger.error(log_entry.message, extra=extra)
        else:
            self.logger.debug(log_entry.message, extra=extra)
        
        return log_entry
    
    def get_job_logs(
        self, 
        job_id: int, 
        level: str = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get logs for a specific ingestion job"""
        log_file = self._get_job_log_file(job_id)
        
        if not log_file.exists():
            return []
        
        logs = []
        with open(log_file, 'r') as f:
            # Skip header lines
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                
                try:
                    # Parse log line
                    if " - " in line:
                        main_part, context_part = line.split(" - ", 1)
                    else:
                        main_part = line
                        context_part = "{}"
                    
                    # Extract timestamp and level
                    if main_part.startswith("["):
                        timestamp_end = main_part.find("]", 1)
                        if timestamp_end > 0:
                            timestamp = main_part[1:timestamp_end]
                            level_start = main_part.find("[", timestamp_end + 1)
                            level_end = main_part.find("]", level_start + 1)
                            if level_start > 0 and level_end > 0:
                                level = main_part[level_start + 1:level_end]
                                message = main_part[level_end + 1:].strip()
                                
                                # Filter by level if specified
                                if level and level != level:
                                    continue
                                
                                # Parse context
                                try:
                                    context = json.loads(context_part)
                                except json.JSONDecodeError:
                                    context = {"raw": context_part}
                                
                                logs.append({
                                    "job_id": job_id,
                                    "timestamp": timestamp,
                                    "level": level,
                                    "message": message,
                                    "context": context
                                })
                                
                                # Stop if we've reached the limit
                                if len(logs) >= limit:
                                    break
                except Exception as e:
                    print(f"Error parsing log line: {line}", e)
                    continue
        
        return logs
    
    def get_job_log_file_content(self, job_id: int) -> str:
        """Get the raw content of a job's log file"""
        log_file = self._get_job_log_file(job_id)
        
        if not log_file.exists():
            return f"# No logs found for job {job_id}\n"
        
        return log_file.read_text()
    
    def download_job_logs(self, job_id: int) -> Tuple[str, str]:
        """Download logs for a job as a file"""
        log_file = self._get_job_log_file(job_id)
        
        if not log_file.exists():
            raise HTTPException(
                status_code=404,
                detail="No logs found for this job"
            )
        
        # Return file path and suggested filename
        suggested_filename = f"ingestion_job_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        return str(log_file), suggested_filename
    
    def get_all_job_logs_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all job logs"""
        summary = []
        
        # List all log files
        for log_file in self.logs_dir.glob("job_*.log"):
            try:
                # Extract job ID from filename
                job_id = int(log_file.name.split("_")[1].split(".")[0])
                
                # Get file stats
                stat = log_file.stat()
                
                # Count lines (approx)
                line_count = 0
                with open(log_file, 'r') as f:
                    for line_count, _ in enumerate(f, 1):
                        pass
                
                summary.append({
                    "job_id": job_id,
                    "file_size": stat.st_size,
                    "line_count": line_count,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "file_path": str(log_file)
                })
            except Exception as e:
                print(f"Error processing log file {log_file}: {e}")
                continue
        
        return summary
    
    def clear_job_logs(self, job_id: int) -> Dict[str, Any]:
        """Clear logs for a specific job"""
        log_file = self._get_job_log_file(job_id)
        
        if log_file.exists():
            log_file.unlink()
            return {
                "success": True,
                "message": f"Logs cleared for job {job_id}"
            }
        else:
            return {
                "success": True,
                "message": f"No logs found for job {job_id}"
            }
    
    def get_logs_with_filter(
        self,
        job_id: int = None,
        level: str = None,
        start_time: str = None,
        end_time: str = None,
        search_query: str = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get logs with various filters"""
        all_logs = []
        
        # If job_id is specified, only get logs for that job
        if job_id:
            logs = self.get_job_logs(job_id, level, limit)
            all_logs.extend(logs)
        else:
            # Get logs for all jobs
            for log_file in self.logs_dir.glob("job_*.log"):
                try:
                    job_id = int(log_file.name.split("_")[1].split(".")[0])
                    logs = self.get_job_logs(job_id, level, limit)
                    all_logs.extend(logs)
                except Exception as e:
                    print(f"Error processing log file {log_file}: {e}")
                    continue
        
        # Apply time filter
        if start_time or end_time:
            filtered_logs = []
            for log in all_logs:
                log_time = datetime.fromisoformat(log["timestamp"])
                
                if start_time:
                    start_dt = datetime.fromisoformat(start_time)
                    if log_time < start_dt:
                        continue
                
                if end_time:
                    end_dt = datetime.fromisoformat(end_time)
                    if log_time > end_dt:
                        continue
                
                filtered_logs.append(log)
            all_logs = filtered_logs
        
        # Apply search query filter
        if search_query:
            query_lower = search_query.lower()
            filtered_logs = []
            for log in all_logs:
                if (query_lower in log["message"].lower() or
                    query_lower in str(log["context"]).lower()):
                    filtered_logs.append(log)
            all_logs = filtered_logs
        
        # Apply limit
        all_logs = all_logs[:limit]
        
        return all_logs
    
    def get_job_log_stats(self, job_id: int) -> Dict[str, Any]:
        """Get statistics about a job's logs"""
        logs = self.get_job_logs(job_id)
        
        if not logs:
            return {
                "job_id": job_id,
                "total_logs": 0,
                "levels": {},
                "start_time": None,
                "end_time": None
            }
        
        # Count by level
        level_counts = {}
        for log in logs:
            level = log["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Get time range
        timestamps = [log["timestamp"] for log in logs]
        start_time = min(timestamps)
        end_time = max(timestamps)
        
        return {
            "job_id": job_id,
            "total_logs": len(logs),
            "levels": level_counts,
            "start_time": start_time,
            "end_time": end_time,
            "error_count": level_counts.get("ERROR", 0),
            "warning_count": level_counts.get("WARNING", 0)
        }
    
    def export_logs_csv(
        self,
        job_id: int = None,
        level: str = None,
        start_time: str = None,
        end_time: str = None
    ) -> str:
        """Export logs as CSV"""
        logs = self.get_logs_with_filter(job_id, level, start_time, end_time)
        
        # Create CSV content
        csv_lines = ["timestamp,level,message,context,job_id"]
        
        for log in logs:
            context_str = json.dumps(log["context"])
            csv_line = f'"{log["timestamp"]}","{log["level"]}","{log["message"]}","{context_str}",{log["job_id"]}'
            csv_lines.append(csv_line)
        
        return "\n".join(csv_lines)
    
    def integrate_with_ingestion_manager(self, ingestion_manager):
        """Integrate with ingestion manager to automatically log events"""
        original_process = ingestion_manager.process_ingestion_job
        
        async def logged_process(db, job_id):
            # Log job started
            self.log_message(
                job_id,
                "INFO",
                "Ingestion job started",
                {"status": "PROCESSING"}
            )
            
            try:
                # Process the job
                result = await original_process(db, job_id)
                
                # Log job completed
                self.log_message(
                    job_id,
                    "INFO",
                    "Ingestion job completed",
                    {"status": "COMPLETED", "result": result}
                )
                
                return result
                
            except Exception as e:
                # Log job failed
                self.log_message(
                    job_id,
                    "ERROR",
                    "Ingestion job failed",
                    {"error": str(e), "status": "FAILED"}
                )
                raise
        
        # Replace the original method
        ingestion_manager.process_ingestion_job = logged_process
        
        return ingestion_manager


# Singleton instance
ingestion_logs_service = IngestionLogsService()