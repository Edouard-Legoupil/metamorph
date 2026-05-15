"""
Analytics Service for Metamorph Platform

Provides comprehensive analytics and insights across the entire system including:
- Content quality metrics
- System usage statistics
- Operational performance
- User engagement analytics
- Validation and curation workflow metrics
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import statistics
from app.database import get_db
from app.models.sql.knowledge_card import KnowledgeCard, WikiBlock, ValidationCard, DiscussionThread, DiscussionComment
from app.models.sql.website import Website, DiscoveredFile, ScrapeSession, IngestionJob
from app.models.sql.user import User, Team, TeamMember
from app.models.sql.settings import Topic


class AnalyticsService:
    """Comprehensive analytics service for the Metamorph platform."""
    
    def __init__(self):
        """Initialize the analytics service."""
        pass
    
    # ========================
    # CONTENT QUALITY ANALYTICS
    # ========================
    
    def get_content_quality_metrics(self) -> Dict[str, Any]:
        """Get comprehensive content quality metrics across all knowledge cards."""
        try:
            db = next(get_db())
            
            # Get all knowledge cards
            cards = db.query(KnowledgeCard).all()
            
            if not cards:
                return {
                    "total_cards": 0,
                    "status_distribution": {},
                    "card_type_distribution": {},
                    "average_confidence_score": 0,
                    "confidence_distribution": {},
                    "source_quality_metrics": {},
                    "temporal_coverage": {}
                }
            
            # Status distribution
            status_dist = defaultdict(int)
            card_type_dist = defaultdict(int)
            confidence_scores = []
            source_counts = []
            creation_dates = []
            
            for card in cards:
                status_dist[card.status.value] += 1
                card_type_dist[card.card_type.value] += 1
                if card.confidence_score is not None:
                    confidence_scores.append(card.confidence_score)
                
                # Count sources
                source_count = (len(card.source_websites or []) + 
                               len(card.source_documents or []) + 
                               len(card.source_entities or []))
                source_counts.append(source_count)
                
                if card.created_at:
                    creation_dates.append(card.created_at)
            
            # Calculate metrics
            avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0
            median_confidence = statistics.median(confidence_scores) if confidence_scores else 0
            
            # Confidence distribution
            confidence_dist = {
                "high": sum(1 for s in confidence_scores if s >= 0.8),
                "medium": sum(1 for s in confidence_scores if 0.5 <= s < 0.8),
                "low": sum(1 for s in confidence_scores if s < 0.5)
            }
            
            # Source quality metrics
            avg_sources = statistics.mean(source_counts) if source_counts else 0
            source_dist = {
                "well_sourced": sum(1 for s in source_counts if s >= 5),
                "adequate": sum(1 for s in source_counts if 2 <= s < 5),
                "minimal": sum(1 for s in source_counts if s < 2)
            }
            
            # Temporal coverage
            if creation_dates:
                creation_dates.sort()
                oldest = creation_dates[0]
                newest = creation_dates[-1]
                time_span_days = (newest - oldest).days
                
                # Distribution by time periods
                now = datetime.now()
                recent = sum(1 for d in creation_dates if (now - d).days <= 30)
                last_quarter = sum(1 for d in creation_dates if 31 <= (now - d).days <= 90)
                older = sum(1 for d in creation_dates if (now - d).days > 90)
                
                temporal_coverage = {
                    "time_span_days": time_span_days,
                    "oldest_content": oldest.isoformat(),
                    "newest_content": newest.isoformat(),
                    "distribution": {
                        "recent_30_days": recent,
                        "last_quarter_31_90_days": last_quarter,
                        "older_than_90_days": older
                    }
                }
            else:
                temporal_coverage = {
                    "time_span_days": 0,
                    "oldest_content": None,
                    "newest_content": None,
                    "distribution": {
                        "recent_30_days": 0,
                        "last_quarter_31_90_days": 0,
                        "older_than_90_days": 0
                    }
                }
            
            return {
                "total_cards": len(cards),
                "status_distribution": dict(status_dist),
                "card_type_distribution": dict(card_type_dist),
                "average_confidence_score": avg_confidence,
                "median_confidence_score": median_confidence,
                "confidence_distribution": confidence_dist,
                "average_source_count": avg_sources,
                "source_distribution": source_dist,
                "temporal_coverage": temporal_coverage
            }
            
        except Exception as e:
            return {"error": f"Failed to get content quality metrics: {str(e)}"}
    
    def get_wiki_block_quality_metrics(self) -> Dict[str, Any]:
        """Get quality metrics for wiki blocks."""
        try:
            db = next(get_db())
            
            blocks = db.query(WikiBlock).all()
            
            if not blocks:
                return {
                    "total_blocks": 0,
                    "verification_distribution": {},
                    "block_type_distribution": {},
                    "average_confidence_score": 0,
                    "live_vs_draft": {}
                }
            
            verification_dist = defaultdict(int)
            block_type_dist = defaultdict(int)
            confidence_scores = []
            live_count = 0
            word_counts = []
            
            for block in blocks:
                verification_dist[block.verification_state.value] += 1
                block_type_dist[block.block_type.value] += 1
                if block.confidence_score is not None:
                    confidence_scores.append(block.confidence_score)
                if block.is_live:
                    live_count += 1
                word_counts.append(len(block.content.split()))
            
            avg_confidence = statistics.mean(confidence_score) if confidence_scores else 0
            avg_word_count = statistics.mean(word_counts) if word_counts else 0
            
            return {
                "total_blocks": len(blocks),
                "verification_distribution": dict(verification_dist),
                "block_type_distribution": dict(block_type_dist),
                "average_confidence_score": avg_confidence,
                "average_word_count": avg_word_count,
                "live_vs_draft": {
                    "live": live_count,
                    "draft": len(blocks) - live_count
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get wiki block metrics: {str(e)}"}
    
    # ========================
    # SYSTEM USAGE ANALYTICS
    # ========================
    
    def get_system_usage_stats(self) -> Dict[str, Any]:
        """Get overall system usage statistics."""
        try:
            db = next(get_db())
            
            # Count all major entities
            card_count = db.query(KnowledgeCard).count()
            block_count = db.query(WikiBlock).count()
            website_count = db.query(Website).count()
            file_count = db.query(DiscoveredFile).count()
            user_count = db.query(User).count()
            team_count = db.query(Team).count()
            
            # Validation and discussion metrics
            validation_count = db.query(ValidationCard).count()
            discussion_count = db.query(DiscussionThread).count()
            comment_count = db.query(DiscussionComment).count()
            
            # Website scraping stats
            active_websites = db.query(Website).filter(Website.status == "active").count()
            total_scrape_sessions = db.query(ScrapeSession).count()
            total_ingestion_jobs = db.query(IngestionJob).count()
            
            return {
                "content_stats": {
                    "knowledge_cards": card_count,
                    "wiki_blocks": block_count,
                    "websites": website_count,
                    "discovered_files": file_count
                },
                "user_stats": {
                    "total_users": user_count,
                    "total_teams": team_count
                },
                "collaboration_stats": {
                    "validation_cards": validation_count,
                    "discussion_threads": discussion_count,
                    "discussion_comments": comment_count
                },
                "ingestion_stats": {
                    "active_websites": active_websites,
                    "total_scrape_sessions": total_scrape_sessions,
                    "total_ingestion_jobs": total_ingestion_jobs
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get system usage stats: {str(e)}"}
    
    def get_validation_workflow_metrics(self) -> Dict[str, Any]:
        """Get metrics about the validation workflow."""
        try:
            db = next(get_db())
            
            validations = db.query(ValidationCard).all()
            
            if not validations:
                return {
                    "total_validations": 0,
                    "status_distribution": {},
                    "processing_times": {},
                    "validation_quality": {}
                }
            
            status_dist = defaultdict(int)
            processing_times = []
            confidence_changes = []
            
            for val in validations:
                status_dist[val.status.value] += 1
                
                # Calculate processing time if available
                if val.created_at and val.updated_at:
                    time_diff = (val.updated_at - val.created_at).total_seconds() / 3600  # hours
                    processing_times.append(time_diff)
                
                # Check if confidence improved (if we had original confidence)
                # This would require tracking original confidence, which we don't have yet
                
            avg_processing_time = statistics.mean(processing_times) if processing_times else 0
            median_processing_time = statistics.median(processing_times) if processing_times else 0
            
            return {
                "total_validations": len(validations),
                "status_distribution": dict(status_dist),
                "processing_times": {
                    "average_hours": avg_processing_time,
                    "median_hours": median_processing_time,
                    "total_validations_processed": len(processing_times)
                },
                "validation_quality": {
                    # Placeholder for quality metrics
                    "average_confidence_improvement": 0.0,  # Would need historical data
                    "validation_success_rate": status_dist.get("approved", 0) / len(validations) if validations else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get validation metrics: {str(e)}"}
    
    def get_discussion_activity_metrics(self) -> Dict[str, Any]:
        """Get metrics about discussion thread activity."""
        try:
            db = next(get_db())
            
            threads = db.query(DiscussionThread).all()
            comments = db.query(DiscussionComment).all()
            
            if not threads:
                return {
                    "total_threads": 0,
                    "total_comments": 0,
                    "activity_metrics": {},
                    "resolution_metrics": {}
                }
            
            # Activity metrics
            comments_per_thread = len(comments) / len(threads) if threads else 0
            
            # Temporal analysis
            now = datetime.now()
            recent_threads = sum(1 for t in threads if (now - t.created_at).days <= 30)
            active_threads = sum(1 for t in threads if t.updated_at and (now - t.updated_at).days <= 7)
            
            # Resolution metrics
            resolved_threads = sum(1 for t in threads if t.status == "resolved")
            open_threads = sum(1 for t in threads if t.status == "open")
            
            # Comment analysis
            comment_lengths = [len(c.content.split()) for c in comments] if comments else []
            avg_comment_length = statistics.mean(comment_lengths) if comment_lengths else 0
            
            return {
                "total_threads": len(threads),
                "total_comments": len(comments),
                "activity_metrics": {
                    "comments_per_thread": comments_per_thread,
                    "recent_threads_30_days": recent_threads,
                    "active_threads_7_days": active_threads
                },
                "resolution_metrics": {
                    "resolved_threads": resolved_threads,
                    "open_threads": open_threads,
                    "resolution_rate": resolved_threads / len(threads) if threads else 0
                },
                "comment_quality": {
                    "average_comment_length_words": avg_comment_length
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get discussion metrics: {str(e)}"}
    
    # ========================
    # INGESTION PIPELINE ANALYTICS
    # ========================
    
    def get_ingestion_pipeline_metrics(self) -> Dict[str, Any]:
        """Get metrics about the ingestion pipeline performance."""
        try:
            db = next(get_db())
            
            websites = db.query(Website).all()
            scrape_sessions = db.query(ScrapeSession).all()
            ingestion_jobs = db.query(IngestionJob).all()
            
            if not websites:
                return {
                    "website_stats": {},
                    "scraping_stats": {},
                    "ingestion_stats": {}
                }
            
            # Website statistics
            by_status = defaultdict(int)
            by_frequency = defaultdict(int)
            total_files = sum(w.total_files_discovered or 0 for w in websites)
            total_ingested = sum(w.total_files_ingested or 0 for w in websites)
            
            for website in websites:
                by_status[website.status.value] += 1
                by_frequency[website.scrape_frequency or "unknown"] += 1
            
            # Scraping statistics
            if scrape_sessions:
                successful_sessions = sum(1 for s in scrape_sessions if s.status == "completed")
                failed_sessions = sum(1 for s in scrape_sessions if s.status == "failed")
                
                session_durations = []
                for session in scrape_sessions:
                    if session.started_at and session.completed_at:
                        duration = (session.completed_at - session.started_at).total_seconds() / 60  # minutes
                        session_durations.append(duration)
                
                avg_duration = statistics.mean(session_durations) if session_durations else 0
                
                scraping_stats = {
                    "total_sessions": len(scrape_sessions),
                    "successful_sessions": successful_sessions,
                    "failed_sessions": failed_sessions,
                    "success_rate": successful_sessions / len(scrape_sessions) if scrape_sessions else 0,
                    "average_duration_minutes": avg_duration
                }
            else:
                scraping_stats = {
                    "total_sessions": 0,
                    "successful_sessions": 0,
                    "failed_sessions": 0,
                    "success_rate": 0,
                    "average_duration_minutes": 0
                }
            
            # Ingestion statistics
            if ingestion_jobs:
                successful_jobs = sum(1 for j in ingestion_jobs if j.status == "completed")
                failed_jobs = sum(1 for j in ingestion_jobs if j.status == "failed")
                
                job_durations = []
                for job in ingestion_jobs:
                    if job.started_at and job.completed_at:
                        duration = (job.completed_at - job.started_at).total_seconds() / 60  # minutes
                        job_durations.append(duration)
                
                avg_job_duration = statistics.mean(job_durations) if job_durations else 0
                
                ingestion_stats = {
                    "total_jobs": len(ingestion_jobs),
                    "successful_jobs": successful_jobs,
                    "failed_jobs": failed_jobs,
                    "success_rate": successful_jobs / len(ingestion_jobs) if ingestion_jobs else 0,
                    "average_duration_minutes": avg_job_duration,
                    "total_files_processed": sum(j.files_processed or 0 for j in ingestion_jobs)
                }
            else:
                ingestion_stats = {
                    "total_jobs": 0,
                    "successful_jobs": 0,
                    "failed_jobs": 0,
                    "success_rate": 0,
                    "average_duration_minutes": 0,
                    "total_files_processed": 0
                }
            
            return {
                "website_stats": {
                    "total_websites": len(websites),
                    "by_status": dict(by_status),
                    "by_scrape_frequency": dict(by_frequency),
                    "total_files_discovered": total_files,
                    "total_files_ingested": total_ingested,
                    "ingestion_rate": total_ingested / total_files if total_files else 0
                },
                "scraping_stats": scraping_stats,
                "ingestion_stats": ingestion_stats
            }
            
        except Exception as e:
            return {"error": f"Failed to get ingestion metrics: {str(e)}"}
    
    # ========================
    # TIME-SERIES ANALYTICS
    # ========================
    
    def get_content_growth_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get time-series data for content growth."""
        try:
            db = next(get_db())
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get content created in time range
            cards = db.query(KnowledgeCard) \
                .filter(KnowledgeCard.created_at >= start_date) \
                .order_by(KnowledgeCard.created_at) \
                .all()
            
            blocks = db.query(WikiBlock) \
                .filter(WikiBlock.created_at >= start_date) \
                .order_by(WikiBlock.created_at) \
                .all()
            
            # Group by day
            daily_cards = defaultdict(int)
            daily_blocks = defaultdict(int)
            
            for card in cards:
                day = card.created_at.date().isoformat()
                daily_cards[day] += 1
            
            for block in blocks:
                day = block.created_at.date().isoformat()
                daily_blocks[day] += 1
            
            # Fill in missing days
            all_days = {}
            current_day = start_date
            while current_day <= end_date:
                day_str = current_day.date().isoformat()
                all_days[day_str] = {
                    "date": day_str,
                    "knowledge_cards": daily_cards.get(day_str, 0),
                    "wiki_blocks": daily_blocks.get(day_str, 0),
                    "total_content": daily_cards.get(day_str, 0) + daily_blocks.get(day_str, 0)
                }
                current_day += timedelta(days=1)
            
            return {
                "time_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "daily_stats": list(all_days.values()),
                "totals": {
                    "total_knowledge_cards": len(cards),
                    "total_wiki_blocks": len(blocks),
                    "total_content_items": len(cards) + len(blocks),
                    "average_per_day": (len(cards) + len(blocks)) / days if days > 0 else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get content growth trends: {str(e)}"}
    
    def get_validation_activity_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get time-series data for validation activity."""
        try:
            db = next(get_db())
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get validation activity in time range
            validations = db.query(ValidationCard) \
                .filter(ValidationCard.created_at >= start_date) \
                .order_by(ValidationCard.created_at) \
                .all()
            
            # Group by day and status
            daily_activity = defaultdict(lambda: defaultdict(int))
            
            for val in validations:
                day = val.created_at.date().isoformat()
                daily_activity[day][val.status.value] += 1
                daily_activity[day]["total"] += 1
            
            # Fill in missing days
            all_days = {}
            current_day = start_date
            while current_day <= end_date:
                day_str = current_day.date().isoformat()
                day_data = daily_activity.get(day_str, {})
                all_days[day_str] = {
                    "date": day_str,
                    "created": day_data.get("created", 0),
                    "under_review": day_data.get("under_review", 0),
                    "approved": day_data.get("approved", 0),
                    "rejected": day_data.get("rejected", 0),
                    "total": day_data.get("total", 0)
                }
                current_day += timedelta(days=1)
            
            return {
                "time_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "daily_stats": list(all_days.values()),
                "totals": {
                    "total_validations": len(validations),
                    "average_per_day": len(validations) / days if days > 0 else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get validation trends: {str(e)}"}
    
    # ========================
    # COMPREHENSIVE DASHBOARD
    # ========================
    
    def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Get a comprehensive analytics dashboard with all key metrics."""
        try:
            # Gather all metrics
            content_quality = self.get_content_quality_metrics()
            wiki_quality = self.get_wiki_block_quality_metrics()
            system_usage = self.get_system_usage_stats()
            validation_metrics = self.get_validation_workflow_metrics()
            discussion_metrics = self.get_discussion_activity_metrics()
            ingestion_metrics = self.get_ingestion_pipeline_metrics()
            content_trends = self.get_content_growth_trends(30)
            validation_trends = self.get_validation_activity_trends(30)
            
            # Calculate overall health score (0-100)
            health_score = self._calculate_health_score(
                content_quality, validation_metrics, ingestion_metrics
            )
            
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_health_score": health_score,
                "content_quality": content_quality,
                "wiki_quality": wiki_quality,
                "system_usage": system_usage,
                "validation_workflow": validation_metrics,
                "discussion_activity": discussion_metrics,
                "ingestion_pipeline": ingestion_metrics,
                "trends": {
                    "content_growth": content_trends,
                    "validation_activity": validation_trends
                },
                "key_insights": self._generate_key_insights(
                    content_quality, validation_metrics, ingestion_metrics
                )
            }
            
        except Exception as e:
            return {"error": f"Failed to generate comprehensive dashboard: {str(e)}"}
    
    def _calculate_health_score(self, content_quality: Dict, validation_metrics: Dict, 
                               ingestion_metrics: Dict) -> float:
        """Calculate overall system health score (0-100)."""
        try:
            score = 0.0
            max_score = 0.0
            
            # Content quality factors (40% of total)
            if content_quality.get("total_cards", 0) > 0:
                score += content_quality.get("average_confidence_score", 0) * 20  # 0-20 points
                max_score += 20
                
                # Approval rate
                approved = content_quality.get("status_distribution", {}).get("approved", 0)
                total = content_quality.get("total_cards", 1)
                approval_rate = approved / total
                score += approval_rate * 20  # 0-20 points
                max_score += 20
            
            # Validation workflow factors (30% of total)
            if validation_metrics.get("total_validations", 0) > 0:
                success_rate = validation_metrics.get("validation_quality", {}).get("validation_success_rate", 0)
                score += success_rate * 15  # 0-15 points
                max_score += 15
                
                # Processing efficiency
                avg_time = validation_metrics.get("processing_times", {}).get("average_hours", 100)
                time_score = max(0, 1 - (avg_time / 24))  # Faster is better, cap at 24 hours
                score += time_score * 15  # 0-15 points
                max_score += 15
            
            # Ingestion pipeline factors (30% of total)
            if ingestion_metrics.get("website_stats", {}).get("total_websites", 0) > 0:
                ingestion_rate = ingestion_metrics.get("website_stats", {}).get("ingestion_rate", 0)
                score += ingestion_rate * 15  # 0-15 points
                max_score += 15
                
                scraping_success = ingestion_metrics.get("scraping_stats", {}).get("success_rate", 0)
                score += scraping_success * 15  # 0-15 points
                max_score += 15
            
            if max_score > 0:
                health_score = (score / max_score) * 100
                return round(health_score, 1)
            else:
                return 50.0  # Default score if no data
                
        except Exception as e:
            return 50.0  # Default score on error
    
    def _generate_key_insights(self, content_quality: Dict, validation_metrics: Dict, 
                              ingestion_metrics: Dict) -> List[str]:
        """Generate key insights from analytics data."""
        insights = []
        
        # Content quality insights
        total_cards = content_quality.get("total_cards", 0)
        if total_cards > 0:
            avg_confidence = content_quality.get("average_confidence_score", 0)
            if avg_confidence >= 0.8:
                insights.append("👍 Excellent content confidence scores across the knowledge base")
            elif avg_confidence >= 0.6:
                insights.append("📊 Good content confidence, but room for improvement in some areas")
            else:
                insights.append("⚠️ Content confidence scores are low - consider review and validation")
            
            approved_pct = (content_quality.get("status_distribution", {}).get("approved", 0) / total_cards) * 100
            if approved_pct >= 70:
                insights.append(f"🎯 {approved_pct:.1f}% of content is approved and ready for use")
            else:
                insights.append(f"📈 Only {approved_pct:.1f}% of content is approved - validation pipeline needs attention")
        else:
            insights.append("ℹ️ No knowledge cards found - content creation should be prioritized")
        
        # Validation workflow insights
        total_validations = validation_metrics.get("total_validations", 0)
        if total_validations > 0:
            success_rate = validation_metrics.get("validation_quality", {}).get("validation_success_rate", 0) * 100
            avg_time = validation_metrics.get("processing_times", {}).get("average_hours", 0)
            
            if success_rate >= 80:
                insights.append(f"🏆 High validation success rate: {success_rate:.1f}%")
            else:
                insights.append(f"🔍 Validation success rate could be improved: {success_rate:.1f}%")
                
            if avg_time < 2:
                insights.append("⚡ Fast validation processing - average under 2 hours")
            elif avg_time < 8:
                insights.append(f"⏱️ Reasonable validation time - average {avg_time:.1f} hours")
            else:
                insights.append(f"🐢 Slow validation processing - average {avg_time:.1f} hours")
        
        # Ingestion pipeline insights
        total_websites = ingestion_metrics.get("website_stats", {}).get("total_websites", 0)
        if total_websites > 0:
            ingestion_rate = ingestion_metrics.get("website_stats", {}).get("ingestion_rate", 0) * 100
            scraping_success = ingestion_metrics.get("scraping_stats", {}).get("success_rate", 0) * 100
            
            if ingestion_rate >= 80:
                insights.append(f"🔄 High ingestion rate: {ingestion_rate:.1f}% of discovered files processed")
            else:
                insights.append(f"📦 Ingestion rate could be improved: {ingestion_rate:.1f}% of discovered files processed")
                
            if scraping_success >= 90:
                insights.append(f"🌐 Excellent scraping success: {scraping_success:.1f}%")
            elif scraping_success >= 70:
                insights.append(f"🕸️ Good scraping success: {scraping_success:.1f}%")
            else:
                insights.append(f"❗ Scraping reliability needs improvement: {scraping_success:.1f}% success rate")
        
        return insights if insights else ["No significant insights available - more data needed"]