"""
Scheduling Service for Website Re-scraping

Handles scheduled scraping of websites with incremental updates.
Supports daily, weekly, monthly schedules with change detection.
"""

import os
import time
import hashlib
import tempfile
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sql.website import Website, WebsiteStatus, DiscoveredFile, FileStatus, ScrapeSession, ScrapeSessionStatus
from app.services.website_crawler.crawler import WebsiteCrawler
from app.core.config import settings


class SchedulingService:
    """Service for managing scheduled website scraping"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.crawler = WebsiteCrawler()
        self.max_concurrent_jobs = 3
        self.active_jobs = {}
        self.supported_frequencies = ['daily', 'weekly', 'monthly', 'hourly', 'manual']
    
    def _get_cron_trigger(self, frequency: str) -> CronTrigger:
        """Convert frequency to APScheduler cron trigger"""
        if frequency == 'hourly':
            return CronTrigger(hour='*')
        elif frequency == 'daily':
            return CronTrigger(day='*', hour='0')  # Midnight every day
        elif frequency == 'weekly':
            return CronTrigger(day_of_week='0', hour='0')  # Sunday midnight
        elif frequency == 'monthly':
            return CronTrigger(day='1', hour='0')  # First of month midnight
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")
    
    def _get_interval_trigger(self, frequency: str) -> IntervalTrigger:
        """Convert frequency to APScheduler interval trigger"""
        if frequency == 'hourly':
            return IntervalTrigger(hours=1)
        elif frequency == 'daily':
            return IntervalTrigger(days=1)
        elif frequency == 'weekly':
            return IntervalTrigger(weeks=1)
        elif frequency == 'monthly':
            return IntervalTrigger(days=30)  # Approximate month
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")
    
    def _calculate_next_scrape_time(self, frequency: str, last_scraped_at: Optional[datetime] = None) -> datetime:
        """Calculate next scrape time based on frequency"""
        now = datetime.now()
        
        if not last_scraped_at:
            # If never scraped, start immediately
            return now + timedelta(minutes=5)
        
        if frequency == 'hourly':
            next_time = last_scraped_at + timedelta(hours=1)
        elif frequency == 'daily':
            next_time = last_scraped_at + timedelta(days=1)
        elif frequency == 'weekly':
            next_time = last_scraped_at + timedelta(weeks=1)
        elif frequency == 'monthly':
            next_time = last_scraped_at + timedelta(days=30)
        else:
            return None
        
        # If next time is in the past, schedule for next occurrence
        if next_time < now:
            return self._calculate_next_scrape_time(frequency, now)
        
        return next_time
    
    def _validate_website_for_scheduling(self, website: Website) -> None:
        """Validate that a website can be scheduled"""
        if website.status not in [WebsiteStatus.ACTIVE, WebsiteStatus.PENDING]:
            raise HTTPException(
                status_code=400,
                detail=f"Website must be ACTIVE or PENDING to schedule (current: {website.status.value})"
            )
        
        if website.scrape_frequency not in self.supported_frequencies:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported scrape frequency: {website.scrape_frequency}"
            )
    
    def _create_scrape_session(self, db: Session, website_id: int, is_scheduled: bool = True) -> ScrapeSession:
        """Create a new scrape session record"""
        session = ScrapeSession(
            website_id=website_id,
            status=ScrapeSessionStatus.PENDING,
            is_scheduled=is_scheduled,
            started_at=datetime.now(),
            session_type='SCHEDULED' if is_scheduled else 'MANUAL'
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    def _update_website_schedule(self, db: Session, website_id: int, next_scrape_at: datetime) -> None:
        """Update website schedule information"""
        website = db.query(Website).filter(Website.id == website_id).first()
        if website:
            website.next_scrape_at = next_scrape_at
            website.status = WebsiteStatus.ACTIVE
            db.commit()
    
    def _detect_changes(self, db: Session, website_id: int, current_files: List[Dict]) -> Dict[str, Any]:
        """Detect new or changed files compared to previous scrape"""
        # Get previously discovered files
        previous_files = db.query(DiscoveredFile).filter(
            DiscoveredFile.website_id == website_id
        ).all()
        
        previous_urls = {f.url: f for f in previous_files}
        current_urls = {f['url']: f for f in current_files}
        
        # Find new files
        new_files = []
        for url, file_data in current_urls.items():
            if url not in previous_urls:
                new_files.append(file_data)
            else:
                # Check if file has changed (simple size check for now)
                previous_file = previous_urls[url]
                if previous_file.file_size != file_data.get('file_size'):
                    new_files.append(file_data)
        
        return {
            'new_files_count': len(new_files),
            'total_files_count': len(current_files),
            'previous_files_count': len(previous_files),
            'new_files': new_files
        }
    
    async def _perform_scheduled_scrape(self, db: Session, website_id: int, session_id: int) -> Dict[str, Any]:
        """Perform the actual scraping for a scheduled job"""
        try:
            # Get website
            website = db.query(Website).filter(Website.id == website_id).first()
            if not website:
                raise HTTPException(status_code=404, detail="Website not found")
            
            # Update session status
            session = db.query(ScrapeSession).filter(ScrapeSession.id == session_id).first()
            if session:
                session.status = ScrapeSessionStatus.RUNNING
                db.commit()
            
            # Perform crawling
            crawl_config = {
                'max_pages': website.max_pages,
                'max_depth': website.max_depth,
                'respect_robots': website.respect_robots,
                'crawl_delay': website.crawl_delay,
                'same_domain_only': website.same_domain_only
            }
            
            # Use the website crawler service
            crawl_result = await self.crawler.crawl_website(
                website.url,
                crawl_config,
                cf_config={
                    'cfAccessClientId': website.cf_access_client_id,
                    'cfAccessClientSecret': website.cf_access_client_secret,
                    'cfTokenUrl': website.cf_token_url
                } if website.cf_access_client_id else None
            )
            
            # Detect changes
            change_detection = self._detect_changes(db, website_id, crawl_result.get('discovered_files', []))
            
            # Update session with results
            if session:
                session.status = ScrapeSessionStatus.COMPLETED
                session.completed_at = datetime.now()
                session.files_discovered = len(crawl_result.get('discovered_files', []))
                session.files_new = change_detection['new_files_count']
                session.error_message = None
                db.commit()
            
            # Update website statistics
            website.total_files_discovered += change_detection['new_files_count']
            website.last_scraped_at = datetime.now()
            db.commit()
            
            # Calculate next scrape time
            next_scrape_time = self._calculate_next_scrape_time(website.scrape_frequency, website.last_scraped_at)
            self._update_website_schedule(db, website_id, next_scrape_time)
            
            return {
                'success': True,
                'website_id': website_id,
                'session_id': session_id,
                'files_discovered': len(crawl_result.get('discovered_files', [])),
                'new_files': change_detection['new_files_count'],
                'next_scrape_at': next_scrape_time,
                'status': 'COMPLETED'
            }
            
        except Exception as e:
            # Update session with error
            session = db.query(ScrapeSession).filter(ScrapeSession.id == session_id).first()
            if session:
                session.status = ScrapeSessionStatus.FAILED
                session.error_message = str(e)
                session.completed_at = datetime.now()
                db.commit()
            
            raise HTTPException(
                status_code=500,
                detail=f"Scheduled scrape failed: {str(e)}"
            )
        
        finally:
            # Remove from active jobs
            if website_id in self.active_jobs:
                del self.active_jobs[website_id]
    
    def schedule_website(self, db: Session, website_id: int) -> Dict[str, Any]:
        """Schedule a website for regular scraping"""
        # Get website
        website = db.query(Website).filter(Website.id == website_id).first()
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Validate website
        self._validate_website_for_scheduling(website)
        
        # Calculate next scrape time
        next_scrape_time = self._calculate_next_scrape_time(
            website.scrape_frequency,
            website.last_scraped_at
        )
        
        # Create scrape session
        session = self._create_scrape_session(db, website_id)
        
        # Update website schedule
        self._update_website_schedule(db, website_id, next_scrape_time)
        
        # Schedule the job
        job_id = f"website_{website_id}_scrape"
        
        # Use interval trigger for simplicity
        trigger = self._get_interval_trigger(website.scrape_frequency)
        
        self.scheduler.add_job(
            self._perform_scheduled_scrape,
            trigger=trigger,
            args=[db, website_id, session.id],
            id=job_id,
            replace_existing=True,
            max_instances=1
        )
        
        return {
            'success': True,
            'website_id': website_id,
            'schedule_frequency': website.scrape_frequency,
            'next_scrape_at': next_scrape_time,
            'session_id': session.id,
            'job_id': job_id
        }
    
    def update_website_schedule(self, db: Session, website_id: int, new_frequency: str) -> Dict[str, Any]:
        """Update the schedule frequency for a website"""
        # Get website
        website = db.query(Website).filter(Website.id == website_id).first()
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        if new_frequency not in self.supported_frequencies:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported frequency: {new_frequency}. Must be one of: {', '.join(self.supported_frequencies)}"
            )
        
        # Remove existing job
        job_id = f"website_{website_id}_scrape"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # Update website frequency
        website.scrape_frequency = new_frequency
        db.commit()
        
        # Re-schedule with new frequency
        return self.schedule_website(db, website_id)
    
    def cancel_website_schedule(self, website_id: int) -> Dict[str, Any]:
        """Cancel scheduled scraping for a website"""
        job_id = f"website_{website_id}_scrape"
        
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            return {'success': True, 'message': 'Schedule cancelled'}
        else:
            return {'success': True, 'message': 'No active schedule found'}
    
    def get_website_schedule(self, website_id: int) -> Dict[str, Any]:
        """Get schedule information for a website"""
        job_id = f"website_{website_id}_scrape"
        job = self.scheduler.get_job(job_id)
        
        if job:
            next_run = job.next_run_time
            return {
                'scheduled': True,
                'next_run_time': next_run,
                'job_id': job_id,
                'trigger': str(job.trigger)
            }
        else:
            return {
                'scheduled': False,
                'message': 'No active schedule found'
            }
    
    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """Get all scheduled scraping jobs"""
        jobs = self.scheduler.get_jobs()
        
        return [{
            'job_id': job.id,
            'next_run_time': job.next_run_time,
            'trigger': str(job.trigger),
            'pending': job.next_run_time is not None
        } for job in jobs]
    
    def trigger_immediate_scrape(self, db: Session, website_id: int) -> Dict[str, Any]:
        """Trigger an immediate scrape of a website (outside of schedule)"""
        # Create manual scrape session
        session = self._create_scrape_session(db, website_id, is_scheduled=False)
        
        # Perform scrape immediately
        return self._perform_scheduled_scrape(db, website_id, session.id)
    
    def pause_all_schedules(self) -> Dict[str, Any]:
        """Pause all scheduled scraping jobs"""
        self.scheduler.pause()
        return {'success': True, 'message': 'All schedules paused'}
    
    def resume_all_schedules(self) -> Dict[str, Any]:
        """Resume all scheduled scraping jobs"""
        self.scheduler.resume()
        return {'success': True, 'message': 'All schedules resumed'}
    
    def get_scheduling_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about scheduled scraping"""
        total_websites = db.query(Website).count()
        scheduled_websites = db.query(Website).filter(
            Website.scrape_frequency != 'manual',
            Website.scrape_frequency != None
        ).count()
        
        active_sessions = db.query(ScrapeSession).filter(
            ScrapeSession.is_scheduled == True,
            ScrapeSession.status.in_([ScrapeSessionStatus.PENDING, ScrapeSessionStatus.RUNNING])
        ).count()
        
        completed_sessions = db.query(ScrapeSession).filter(
            ScrapeSession.is_scheduled == True,
            ScrapeSession.status == ScrapeSessionStatus.COMPLETED
        ).count()
        
        return {
            'total_websites': total_websites,
            'scheduled_websites': scheduled_websites,
            'active_sessions': active_sessions,
            'completed_sessions': completed_sessions,
            'active_jobs': len(self.active_jobs),
            'scheduler_state': self.scheduler.state
        }
    
    def shutdown(self) -> None:
        """Shutdown the scheduler"""
        self.scheduler.shutdown()


# Singleton instance
scheduling_service = SchedulingService()