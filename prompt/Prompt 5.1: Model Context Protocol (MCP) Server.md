Implement the MCP server from Pipeline Blueprint Section 6.3 for agentic access.

Create mcp/server.py:

1. MCP server setup:
   - Use FastAPI + SSE for transport
   - Implement MCP protocol specification
   - Authentication via API keys
   - Rate limiting per client

2. Required tools (per 6.3):
   @mcp.tool
   def get_entity(entity_id: str = None, name: str = None, label: str = None) -> dict:
       """Retrieve a node and all its edges by entity ID or name."""
       # Return node properties + all connected edges
   
   @mcp.tool
   def search_knowledge(query: str, limit: int = 20, verified_only: bool = True) -> list:
       """Semantic search over verified wiki blocks."""
       # Use vector embeddings + metadata filters
   
   @mcp.tool
   def get_conflicts(status: str = "UNRESOLVED", severity: str = None) -> list:
       """Retrieve all ConflictRecords matching criteria."""
       # Return conflicts with current and proposed values
   
   @mcp.tool
   def get_document_triplets(document_id: str) -> list:
       """Return all triplets extracted from a given document."""
       # Include extraction confidence and page references
   
   @mcp.tool
   def get_wiki_page(page_id: str = None, slug: str = None) -> dict:
       """Return rendered Markdown for a wiki page with metadata."""
       # Include verification status per block
   
   @mcp.tool
   def get_knowledge_card(card_id: str, include_sections: list = None) -> dict:
       """Retrieve a complete knowledge card with all sections."""
       # Return card with rendered sections from graph
   

3. Resource endpoints:
   @mcp.resource("knowledge://{country}/{crisis_type}")
   def get_context_resources(country: str, crisis_type: str) -> list:
       """List available knowledge cards for context."""
   
   @mcp.resource("evidence://{outcome_code}")
   def get_evidence_resources(outcome_code: str) -> list:
       """List evidence findings for UNHCR outcome OA1-OA16."""


Ensure that the platform
-  Securely allow agents/bots (with MCP API key) to retrieve entities, knowledge cards, blocks, wiki pages, conflicts, and more.
- Deliver streaming agentic updates with SSE (ready for web/agent/CLI clients).

Add  an agent SDK, webhook integration, and audit logging support