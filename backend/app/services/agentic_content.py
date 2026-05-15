"""
Agentic Content Generation Service

Implements intelligent content generation and updating using CrewAI framework.
Monitors knowledge graph changes and automatically generates/updates wiki articles
based on knowledge card templates and vector store content.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio
from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from app.services.vector_store import vector_store_service
from app.services.knowledge_graph import knowledge_graph
from app.services.wiki.block_assembler import assemble_blocks_for_card
from app.core.config import settings


class AgenticContentGenerator:
    """Agentic content generation and updating system"""
    
    def __init__(self):
        self.kg_service = knowledge_graph
        self.vector_service = vector_store_service
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )
        
        # Initialize CrewAI agents
        self._initialize_agents()
        
        # Knowledge graph change monitoring
        self.last_checked = datetime.utcnow()
        self.monitoring_interval = 60  # seconds
    
    def _initialize_agents(self):
        """Initialize CrewAI agents for content generation"""
        
        # Researcher Agent - Gathers information from knowledge graph and vector store
        self.researcher = Agent(
            role='Researcher',
            goal='Gather comprehensive information from knowledge graph and vector store',
            backstory='''An expert researcher who can query both structured knowledge graphs
            and semantic vector stores to find relevant information for content generation.''',
            verbose=True,
            allow_delegation=False
        )
        
        # Analyst Agent - Analyzes information and identifies key insights
        self.analyst = Agent(
            role='Analyst',
            goal='Analyze gathered information and identify key insights and patterns',
            backstory='''A data analysis expert who can process complex information,
            identify patterns, and extract meaningful insights for content creation.''',
            verbose=True,
            allow_delegation=True
        )
        
        # Writer Agent - Generates coherent content based on templates
        self.writer = Agent(
            role='Writer',
            goal='Generate high-quality wiki content based on knowledge card templates',
            backstory='''A professional writer who can transform structured data and insights
            into well-written, informative wiki articles following established templates.''',
            verbose=True,
            allow_delegation=False
        )
        
        # Editor Agent - Reviews and improves generated content
        self.editor = Agent(
            role='Editor',
            goal='Review, refine, and ensure quality of generated content',
            backstory='''An experienced editor who ensures content meets quality standards,
            follows best practices, and is properly formatted for wiki publication.''',
            verbose=True,
            allow_delegation=False
        )
        
        # Coordinator Agent - Manages the content generation workflow
        self.coordinator = Agent(
            role='Coordinator',
            goal='Orchestrate the content generation process and manage agent collaboration',
            backstory='''A workflow manager who ensures smooth collaboration between agents,
            manages task delegation, and oversees the entire content generation process.''',
            verbose=True,
            allow_delegation=True
        )
    
    def _create_content_generation_crew(self) -> Crew:
        """Create a crew for content generation tasks"""
        return Crew(
            agents=[self.researcher, self.analyst, self.writer, self.editor, self.coordinator],
            process=Process.sequential,
            verbose=2,
            memory=True,
            embedder=self.embedding_model
        )
    
    async def monitor_knowledge_graph_changes(self):
        """Continuously monitor knowledge graph for changes"""
        while True:
            try:
                # Check for recent changes
                changes = self._detect_knowledge_changes()
                
                if changes:
                    print(f"🔍 Detected {len(changes)} knowledge graph changes")
                    
                    # Process each change
                    for change in changes:
                        await self.process_knowledge_change(change)
                
                # Wait for next check
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"❌ Error monitoring knowledge graph: {e}")
                await asyncio.sleep(10)  # Wait before retry
    
    def _detect_knowledge_changes(self) -> List[Dict[str, Any]]:
        """Detect recent changes in the knowledge graph"""
        try:
            # Get recent changes (last 24 hours)
            recent_changes = self.kg_service.get_recent_changes(hours=24)
            
            # Filter for significant changes (new entities, updated relationships)
            significant_changes = []
            
            for change in recent_changes:
                if change['change_type'] in ['ENTITY_CREATED', 'RELATIONSHIP_UPDATED', 'PROPERTY_CHANGED']:
                    if change['confidence'] > 0.8:  # High confidence changes
                        significant_changes.append(change)
            
            return significant_changes
            
        except Exception as e:
            print(f"❌ Error detecting knowledge changes: {e}")
            return []
    
    async def process_knowledge_change(self, change: Dict[str, Any]):
        """Process a knowledge graph change and generate/update content"""
        try:
            print(f"📝 Processing change: {change['change_type']} - {change['entity_id']}")
            
            # Determine if this change affects existing content
            affected_cards = self._find_affected_knowledge_cards(change)
            
            if affected_cards:
                # Update existing content
                for card_id in affected_cards:
                    await self.update_knowledge_card_content(card_id, change)
            else:
                # Generate new content
                await self.generate_new_content_from_change(change)
                
        except Exception as e:
            print(f"❌ Error processing knowledge change: {e}")
    
    def _find_affected_knowledge_cards(self, change: Dict[str, Any]) -> List[str]:
        """Find knowledge cards affected by a knowledge graph change"""
        try:
            entity_id = change['entity_id']
            
            # Search for knowledge cards that reference this entity
            cards = self.kg_service.search_related_entities(entity_id)
            
            return [card['card_id'] for card in cards if card.get('status') == 'APPROVED']
            
        except Exception as e:
            print(f"❌ Error finding affected knowledge cards: {e}")
            return []
    
    async def update_knowledge_card_content(self, card_id: str, change: Dict[str, Any]):
        """Update existing knowledge card content based on changes"""
        try:
            print(f"🔄 Updating knowledge card {card_id} with new information")
            
            # Get current card content
            current_card = self.kg_service.get_knowledge_card(card_id)
            
            # Create content generation crew
            crew = self._create_content_generation_crew()
            
            # Define tasks for updating content
            research_task = Task(
                description=f"""Research updates related to {change['entity_id']} 
                and how they affect knowledge card {card_id}.
                Focus on: {change['change_description']}""",
                agent=self.researcher,
                expected_output='Detailed analysis of how the change affects the knowledge card content'
            )
            
            analysis_task = Task(
                description="""Analyze the research findings and determine 
                what sections of the knowledge card need to be updated.
                Provide specific recommendations for each section.""",
                agent=self.analyst,
                expected_output='Section-by-section update recommendations with rationale'
            )
            
            writing_task = Task(
                description="""Update the knowledge card content based on the analysis.
                Follow the existing card template and structure.
                Ensure all updates are clearly marked and maintain consistency.""",
                agent=self.writer,
                expected_output='Updated knowledge card content in markdown format'
            )
            
            editing_task = Task(
                description="""Review the updated content for quality, accuracy, 
                and completeness. Ensure it follows wiki standards and is 
                properly formatted.""",
                agent=self.editor,
                expected_output='Final reviewed and approved updated content'
            )
            
            # Execute the crew tasks
            result = crew.kickoff(inputs={'card_id': card_id, 'change': change})
            
            # Update the knowledge card in the database
            updated_content = result.raw_output
            self.kg_service.update_knowledge_card_content(card_id, updated_content)
            
            print(f"✅ Successfully updated knowledge card {card_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating knowledge card content: {e}")
            return False
    
    async def generate_new_content_from_change(self, change: Dict[str, Any]):
        """Generate new knowledge card content from a knowledge graph change"""
        try:
            print(f"✨ Generating new content from change: {change['entity_id']}")
            
            # Determine the best knowledge card template for this entity type
            entity_type = change.get('entity_type', 'unknown')
            card_template = self._select_card_template(entity_type)
            
            if not card_template:
                print(f"⚠️ No suitable template found for entity type: {entity_type}")
                return False
            
            # Create content generation crew
            crew = self._create_content_generation_crew()
            
            # Define tasks for new content generation
            research_task = Task(
                description=f"""Research comprehensive information about {change['entity_id']} 
                (type: {entity_type}) using both knowledge graph and vector store.
                Gather all relevant facts, relationships, and context.""",
                agent=self.researcher,
                expected_output='Comprehensive research report with structured information'
            )
            
            analysis_task = Task(
                description="""Analyze the research findings and organize them 
                according to the knowledge card template structure.
                Identify key sections and their content requirements.""",
                agent=self.analyst,
                expected_output='Structured content outline following the card template'
            )
            
            writing_task = Task(
                description=f"""Generate complete knowledge card content using template {card_template.card_id}.
                Follow the template structure exactly and ensure all required sections are included.
                Write in a clear, professional style suitable for wiki publication.""",
                agent=self.writer,
                expected_output='Complete knowledge card content in markdown format'
            )
            
            editing_task = Task(
                description="""Review the generated content for completeness, accuracy, 
                and adherence to template requirements. Ensure proper formatting, 
                citations, and quality standards.""",
                agent=self.editor,
                expected_output='Final reviewed content ready for publication'
            )
            
            # Execute the crew tasks
            result = crew.kickoff(inputs={'change': change, 'template': card_template})
            
            # Create new knowledge card
            new_card_content = result.raw_output
            new_card_id = self.kg_service.create_knowledge_card(
                card_type=card_template.card_id,
                content=new_card_content,
                source_entity=change['entity_id'],
                status='DRAFT'  # Start as draft for human review
            )
            
            print(f"✅ Successfully generated new knowledge card {new_card_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating new content: {e}")
            return False
    
    def _select_card_template(self, entity_type: str) -> Optional[Any]:
        """Select the appropriate knowledge card template for an entity type"""
        try:
            # Map entity types to appropriate card templates
            template_mapping = {
                'Donor': 'KC-1',
                'Organization': 'KC-1',
                'Region': 'KC-2',
                'PopulationGroup': 'KC-2',
                'Evaluation': 'KC-3',
                'InterventionType': 'KC-3',
                'ImplementingPartner': 'KC-4',
                'Operation': 'KC-5',
                'Crisis': 'KC-6',
                'ConflictEvent': 'KC-6'
            }
            
            template_id = template_mapping.get(entity_type, 'KC-1')  # Default to KC-1
            
            # Get the template definition
            from app.services.wiki.card_templates import (
                KC1DonorCard, KC2FieldContextCard, KC3OutcomeEvidenceCard,
                KC4PartnerCapacityCard, KC5TrackRecordCard, KC6CrisisCard
            )
            
            templates = {
                'KC-1': KC1DonorCard,
                'KC-2': KC2FieldContextCard,
                'KC-3': KC3OutcomeEvidenceCard,
                'KC-4': KC4PartnerCapacityCard,
                'KC-5': KC5TrackRecordCard,
                'KC-6': KC6CrisisCard
            }
            
            return templates[template_id]()
            
        except Exception as e:
            print(f"❌ Error selecting card template: {e}")
            return None
    
    async def generate_content_from_query(self, query: str, card_template_id: str = 'KC-1') -> Dict[str, Any]:
        """Generate content based on a natural language query"""
        try:
            print(f"🎯 Generating content from query: {query}")
            
            # Step 1: Semantic search in vector store
            query_embedding = self.embedding_model.embed_query(query)
            vector_results = self.vector_service.semantic_search_documents(
                query_embedding=query_embedding,
                limit=5
            )
            
            # Step 2: Knowledge graph search
            kg_results = self.kg_service.search_entities(query)
            
            # Step 3: Combine results
            combined_context = {
                'vector_results': vector_results,
                'kg_results': kg_results,
                'query': query
            }
            
            # Create content generation crew
            crew = self._create_content_generation_crew()
            
            # Define content generation task
            content_task = Task(
                description=f"""Generate comprehensive content based on the query: '{query}'
                Use the provided context from both vector store and knowledge graph.
                Follow knowledge card template {card_template_id} structure.
                Ensure the content is well-organized, informative, and professionally written.""",
                agent=self.writer,
                expected_output='Complete content in markdown format following the specified template'
            )
            
            # Execute the task
            result = crew.kickoff(inputs=combined_context)
            
            return {
                'success': True,
                'content': result.raw_output,
                'sources': {
                    'vector': vector_results,
                    'knowledge_graph': kg_results
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating content from query: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def start_monitoring(self):
        """Start the knowledge graph monitoring process"""
        print("🚀 Starting agentic content generation monitoring...")
        await self.monitor_knowledge_graph_changes()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            'agents': {
                'researcher': {'status': 'ready', 'role': self.researcher.role},
                'analyst': {'status': 'ready', 'role': self.analyst.role},
                'writer': {'status': 'ready', 'role': self.writer.role},
                'editor': {'status': 'ready', 'role': self.editor.role},
                'coordinator': {'status': 'ready', 'role': self.coordinator.role}
            },
            'monitoring': 'active' if hasattr(self, 'monitoring_task') else 'inactive',
            'last_checked': self.last_checked.isoformat() if self.last_checked else None
        }


# Singleton instance
agentic_content_generator = AgenticContentGenerator()
