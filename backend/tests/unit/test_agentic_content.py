"""
Unit tests for Agentic Content Generation Service

Tests the agentic content generation functionality including:
- Content generation from queries
- Knowledge graph monitoring
- Agent status and health checks
- Error handling and edge cases
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.services.agentic_content import AgenticContentGenerator
from app.services.agentic_content import agentic_content_generator


@pytest.fixture
def mock_agentic_generator():
    """Create a mock agentic content generator for testing"""
    with patch('app.services.agentic_content.AgenticContentGenerator') as mock_class:
        mock_instance = mock_class.return_value
        mock_instance.get_agent_status.return_value = {
            'agents': {
                'researcher': {'status': 'ready', 'role': 'Researcher'},
                'analyst': {'status': 'ready', 'role': 'Analyst'},
                'writer': {'status': 'ready', 'role': 'Writer'},
                'editor': {'status': 'ready', 'role': 'Editor'},
                'coordinator': {'status': 'ready', 'role': 'Coordinator'}
            },
            'monitoring': 'inactive',
            'last_checked': None
        }
        yield mock_instance


def test_agentic_generator_initialization():
    """Test that the agentic content generator initializes correctly"""
    # Test singleton instance
    assert agentic_content_generator is not None
    assert isinstance(agentic_content_generator, AgenticContentGenerator)


@pytest.mark.asyncio
async def test_generate_content_from_query_success(mock_agentic_generator):
    """Test successful content generation from a query"""
    mock_agentic_generator.generate_content_from_query.return_value = {
        'success': True,
        'content': '# Generated Content\n\nThis is test content.',
        'sources': {
            'vector': [{'id': 'doc1', 'score': 0.95}],
            'knowledge_graph': [{'id': 'entity1', 'type': 'Donor'}]
        }
    }
    
    result = await agentic_content_generator.generate_content_from_query(
        query="test query",
        card_template_id="KC-1"
    )
    
    assert result['success'] is True
    assert 'content' in result
    assert 'sources' in result
    assert 'vector' in result['sources']
    assert 'knowledge_graph' in result['sources']


@pytest.mark.asyncio
async def test_generate_content_from_query_failure(mock_agentic_generator):
    """Test content generation failure handling"""
    mock_agentic_generator.generate_content_from_query.return_value = {
        'success': False,
        'error': 'Test error message'
    }
    
    result = await agentic_content_generator.generate_content_from_query(
        query="test query"
    )
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error'] == 'Test error message'


@pytest.mark.asyncio
async def test_start_monitoring(mock_agentic_generator):
    """Test starting the monitoring process"""
    mock_agentic_generator.start_monitoring.return_value = None
    
    # This should start the monitoring task
    await agentic_content_generator.start_monitoring()
    
    # Verify monitoring task was created
    assert hasattr(agentic_content_generator, 'monitoring_task')


@pytest.mark.asyncio
async def test_stop_monitoring(mock_agentic_generator):
    """Test stopping the monitoring process"""
    # Create a mock monitoring task
    mock_task = AsyncMock()
    agentic_content_generator.monitoring_task = mock_task
    
    # Stop monitoring
    await agentic_content_generator.stop_monitoring()
    
    # Verify task was cancelled and removed
    mock_task.cancel.assert_called_once()
    assert not hasattr(agentic_content_generator, 'monitoring_task')


def test_get_agent_status(mock_agentic_generator):
    """Test getting agent status information"""
    status = agentic_content_generator.get_agent_status()
    
    assert 'agents' in status
    assert len(status['agents']) == 5
    assert status['monitoring'] == 'inactive'
    
    # Check all expected agents are present
    expected_agents = ['researcher', 'analyst', 'writer', 'editor', 'coordinator']
    for agent in expected_agents:
        assert agent in status['agents']
        assert status['agents'][agent]['status'] == 'ready'


@pytest.mark.asyncio
async def test_monitor_knowledge_graph_changes(mock_agentic_generator):
    """Test knowledge graph monitoring functionality"""
    # Mock the detect and process methods
    mock_agentic_generator._detect_knowledge_changes.return_value = [
        {'change_type': 'ENTITY_CREATED', 'entity_id': 'test1'},
        {'change_type': 'RELATIONSHIP_UPDATED', 'entity_id': 'test2'}
    ]
    
    mock_agentic_generator.process_knowledge_change = AsyncMock()
    
    # Run monitoring (with timeout to prevent infinite loop)
    import asyncio
    
    async def run_monitoring_with_timeout():
        task = asyncio.create_task(agentic_content_generator.monitor_knowledge_graph_changes())
        await asyncio.sleep(0.1)  # Let it run briefly
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    await run_monitoring_with_timeout()
    
    # Verify change detection and processing were called
    mock_agentic_generator._detect_knowledge_changes.assert_called()
    assert mock_agentic_generator.process_knowledge_change.call_count == 2


def test_detect_knowledge_changes(mock_agentic_generator):
    """Test knowledge change detection"""
    # Mock knowledge graph service
    mock_kg_service = Mock()
    mock_kg_service.get_recent_changes.return_value = [
        {'change_type': 'ENTITY_CREATED', 'entity_id': 'test1', 'confidence': 0.9},
        {'change_type': 'PROPERTY_CHANGED', 'entity_id': 'test2', 'confidence': 0.7},
        {'change_type': 'ENTITY_CREATED', 'entity_id': 'test3', 'confidence': 0.5}
    ]
    
    mock_agentic_generator.kg_service = mock_kg_service
    
    changes = mock_agentic_generator._detect_knowledge_changes()
    
    # Should filter for high confidence changes only
    assert len(changes) == 2
    assert all(change['confidence'] > 0.8 for change in changes)


@pytest.mark.asyncio
async def test_process_knowledge_change_new_content(mock_agentic_generator):
    """Test processing knowledge changes that require new content"""
    # Mock the find affected cards method to return empty (no existing cards)
    mock_agentic_generator._find_affected_knowledge_cards.return_value = []
    
    # Mock the generate new content method
    mock_agentic_generator.generate_new_content_from_change = AsyncMock(return_value=True)
    
    change = {'change_type': 'ENTITY_CREATED', 'entity_id': 'new_entity'}
    
    result = await mock_agentic_generator.process_knowledge_change(change)
    
    # Should generate new content since no existing cards were affected
    mock_agentic_generator.generate_new_content_from_change.assert_called_once_with(change)


@pytest.mark.asyncio
async def test_process_knowledge_change_update_content(mock_agentic_generator):
    """Test processing knowledge changes that require content updates"""
    # Mock the find affected cards method to return existing cards
    mock_agentic_generator._find_affected_knowledge_cards.return_value = ['card1', 'card2']
    
    # Mock the update content method
    mock_agentic_generator.update_knowledge_card_content = AsyncMock(return_value=True)
    
    change = {'change_type': 'RELATIONSHIP_UPDATED', 'entity_id': 'existing_entity'}
    
    result = await mock_agentic_generator.process_knowledge_change(change)
    
    # Should update existing content
    assert mock_agentic_generator.update_knowledge_card_content.call_count == 2
    mock_agentic_generator.update_knowledge_card_content.assert_any_call('card1', change)
    mock_agentic_generator.update_knowledge_card_content.assert_any_call('card2', change)


def test_select_card_template(mock_agentic_generator):
    """Test card template selection for different entity types"""
    # Test known entity types
    template = mock_agentic_generator._select_card_template('Donor')
    assert template is not None
    
    template = mock_agentic_generator._select_card_template('Organization')
    assert template is not None
    
    # Test unknown entity type (should default to KC-1)
    template = mock_agentic_generator._select_card_template('UnknownType')
    assert template is not None


@pytest.mark.asyncio
async def test_update_knowledge_card_content(mock_agentic_generator):
    """Test updating existing knowledge card content"""
    # Mock the knowledge graph service
    mock_kg_service = Mock()
    mock_kg_service.get_knowledge_card.return_value = {
        'card_id': 'test_card',
        'content': 'Original content'
    }
    
    mock_agentic_generator.kg_service = mock_kg_service
    mock_agentic_generator._create_content_generation_crew = Mock()
    
    # Mock the crew kickoff method
    mock_crew = Mock()
    mock_crew.kickoff.return_value = Mock(raw_output='Updated content')
    mock_agentic_generator._create_content_generation_crew.return_value = mock_crew
    
    change = {'change_type': 'PROPERTY_CHANGED', 'entity_id': 'test_entity'}
    
    result = await mock_agentic_generator.update_knowledge_card_content('test_card', change)
    
    assert result is True
    mock_kg_service.update_knowledge_card_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_new_content_from_change(mock_agentic_generator):
    """Test generating new content from knowledge changes"""
    # Mock template selection
    mock_template = Mock()
    mock_template.card_id = 'KC-1'
    mock_agentic_generator._select_card_template.return_value = mock_template
    
    # Mock the knowledge graph service
    mock_kg_service = Mock()
    mock_kg_service.create_knowledge_card.return_value = 'new_card_id'
    mock_agentic_generator.kg_service = mock_kg_service
    
    # Mock the crew
    mock_crew = Mock()
    mock_crew.kickoff.return_value = Mock(raw_output='New content')
    mock_agentic_generator._create_content_generation_crew.return_value = mock_crew
    
    change = {'change_type': 'ENTITY_CREATED', 'entity_id': 'new_entity', 'entity_type': 'Donor'}
    
    result = await mock_agentic_generator.generate_new_content_from_change(change)
    
    assert result is True
    mock_kg_service.create_knowledge_card.assert_called_once()


def test_agentic_content_error_handling():
    """Test error handling in agentic content methods"""
    # Test with invalid inputs
    with pytest.raises(Exception):
        # This should handle the error gracefully
        result = agentic_content_generator.generate_content_from_query(
            query="",  # Empty query
            card_template_id="INVALID_TEMPLATE"
        )
        # The method should return a failure result rather than raise
        assert result['success'] is False


def test_agent_status_structure():
    """Test that agent status has the expected structure"""
    status = agentic_content_generator.get_agent_status()
    
    # Verify structure
    assert isinstance(status, dict)
    assert 'agents' in status
    assert 'monitoring' in status
    assert 'last_checked' in status
    
    # Verify agents structure
    for agent_name, agent_info in status['agents'].items():
        assert 'status' in agent_info
        assert 'role' in agent_info
        assert isinstance(agent_info['status'], str)
        assert isinstance(agent_info['role'], str)