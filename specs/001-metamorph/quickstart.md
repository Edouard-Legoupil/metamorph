# Metamorph Quick Start Guide

**Spec ID:** 001-metamorph  
**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-04-12

---

## 🚀 Getting Started with Metamorph

This guide will help you set up and start using the Metamorph knowledge pipeline system. Whether you're a developer, curator, or end-user, this guide provides the essential steps to begin.

---

## 📋 Prerequisites

### For Developers
- **Python** 3.10+ (recommended: 3.11 or 3.12)
- **Node.js** 18+ (for frontend development)
- **Git**
- **Docker** (optional, for containerized deployment)
- **Neo4j** 5.x (or Neo4j Aura for managed service)
- **Redis** (optional, for caching)

### For Curators
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Internet connection
- UN/NGO email account (for authentication)

### For Proposal Writers
- Modern web browser
- Access to approved knowledge cards
- Basic understanding of humanitarian operations

---

## 🛠️ Installation & Setup

### Option 1: Local Development Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd metamorph
```

#### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Set Up Neo4j
```bash
# Option A: Using Docker (recommended for development)
docker run \
  --name metamorph-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_dbms_memory_heap_max__size=2G \
  -v metamorph_neo4j_data:/data \
  -d neo4j:5-community

# Option B: Local installation
# Download from https://neo4j.com/download/
# Install and start Neo4j Desktop

# Verify Neo4j is running
curl http://localhost:7474
```

#### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor

# Required settings:
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
SECRET_KEY=your-secret-key-here
DEBUG=true
```

#### 5. Initialize Database
```bash
# Run database initialization script
python scripts/init_db.py

# This will:
# - Create required indexes
# - Set up constraints
# - Load initial schema
```

#### 6. Start Backend Server
```bash
# From backend directory
cd backend
uvicorn app.main:app --reload --port 8000

# The API will be available at: http://localhost:8000
```

#### 7. Start Frontend (Optional)
```bash
# From frontend directory
cd frontend
npm install
npm run dev

# The UI will be available at: http://localhost:3000
```

---

### Option 2: Docker Compose Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd metamorph
```

#### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env as needed
```

#### 3. Start All Services
```bash
docker-compose up -d

# This starts:
# - Neo4j database
# - Redis cache
# - Backend API
# - Frontend UI (optional)
```

#### 4. Verify Services
```bash
# Check all containers are running
docker-compose ps

# View logs
docker-compose logs -f
```

---

### Option 3: Production Deployment

#### 1. Prepare Infrastructure
- Set up server (Linux recommended)
- Install Docker and Docker Compose
- Configure domain and SSL certificates
- Set up database backups

#### 2. Configure for Production
```bash
# Edit docker-compose.prod.yml
nano docker-compose.prod.yml

# Update environment variables for production
cp .env.example .env.prod
nano .env.prod
```

#### 3. Deploy
```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d --build
```

#### 4. Set Up Monitoring
```bash
# Install monitoring tools
# Set up logging
# Configure alerts
```

---

## 🎯 First Steps for Different User Types

### For Developers

#### 1. Run Tests
```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/unit/test_extraction_services.py
pytest tests/integration/

# Run with coverage
pytest --cov=backend --cov-report=html
```

#### 2. Explore the API
```bash
# View API documentation (Swagger UI)
open http://localhost:8000/docs

# Test API endpoints
curl http://localhost:8000/api/v1/health

# Upload a test document
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_document.pdf" \
  http://localhost:8000/api/v1/documents/upload
```

#### 3. Work with the Graph
```bash
# Connect to Neo4j Browser
open http://localhost:7474

# Run sample queries
# Find all documents
MATCH (d:Document) RETURN d LIMIT 10

# Find entities by type
MATCH (e:Entity {type: "Organization"}) RETURN e LIMIT 10

# Find relationships
MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 10
```

---

### For Curators

#### 1. Access the System
1. Open your web browser
2. Navigate to the Metamorph URL (provided by your administrator)
3. Log in using your UN/NGO credentials

#### 2. Understand the Dashboard
- **Validation Queue:** Shows pending validation cards needing your review
- **Recent Activity:** Shows recent changes and updates
- **My Tasks:** Shows tasks assigned to you
- **Search:** Search for specific topics, entities, or cards

#### 3. Process a Validation Card
1. Click on a validation card in the queue
2. Review the **Current Value** vs **Proposed Value**
3. Check the **Diff** to see exactly what changed
4. Review **Evidence** and **Provenance**
5. Check the **Confidence Score** and **Sensitivity Classification**
6. Take action:
   - **Approve:** If the change is accurate and well-sourced
   - **Reject:** If the change is incorrect or poorly sourced
   - **Merge/Edit:** If the change needs modification
   - **Escalate:** If you're unsure or it's sensitive
   - **Open Discussion:** If it needs community input

#### 4. Create a Knowledge Card
1. Navigate to **Knowledge Cards**
2. Click **Create New Card**
3. Select the card type (KC-1 to KC-6)
4. Fill in the template sections
5. Add sources and citations
6. Submit for review

---

### For Proposal Writers

#### 1. Search for Knowledge Cards
1. Navigate to **Knowledge Library**
2. Use filters to narrow down:
   - Domain (Geographic, Crisis, etc.)
   - Card Type (KC-1 to KC-6)
   - Validity (ensure cards are not expired)
   - Date Range
3. Review search results

#### 2. Use Cards in Proposals
1. Select relevant cards for your proposal
2. Click **Add to Proposal**
3. Arrange cards in logical order
4. The system will:
   - Check all cards are valid (not expired)
   - Generate a draft proposal
   - Score interventions based on context
5. Review the generated draft
6. Make manual adjustments as needed

#### 3. Export Proposal
1. Review the final proposal
2. Click **Export**
3. Choose format (PDF, Word, HTML)
4. Download and use in your workflow

---

### For Reviewers

#### 1. Participate in Discussions
1. Navigate to **Discussion Forum**
2. Browse threads or use search
3. Click on a thread to view details
4. Read the discussion and evidence
5. Add your comment:
   - Cite your sources
   - Provide reasoning
   - Propose patches if applicable
6. Vote on consensus

#### 2. Watch Topics
1. Navigate to a topic of interest
2. Click **Watch** button
3. Configure notification preferences
4. You'll receive notifications when:
   - The topic is edited
   - A claim is disputed
   - A discussion is opened
   - A consensus decision is applied

---

## 📖 Understanding Knowledge Cards

### Card Types Overview

| Card Type | Purpose | Validity | Typical Use |
|-----------|---------|----------|-------------|
| **KC-1: Donor Intelligence** | Understand funder priorities | 12 months | Funding proposals |
| **KC-2: Field Context** | Describe situation, needs, risks | 6 months | Situation analysis |
| **KC-3: Outcome Evidence** | Summarize effective interventions | 12 months | Program design |
| **KC-4: Partner Capacity** | Assess partner ability to deliver | 6 months | Partner selection |
| **KC-5: Institutional Track Record** | Highlight UNHCR credibility | 24 months | Credibility statements |
| **KC-6: Crisis Political Economy** | Explain crisis strategic importance | 6 months | Strategic planning |

### Card Structure
Each card contains:
- **Header:** Card type, ID, validity period, approval status
- **Sections:** Organized content blocks (varies by card type)
- **Blocks:** Individual content units with:
  - Unique block_id
  - Section name
  - Word limit
  - Block type
  - Template for extraction
  - Verification status
  - Provenance tracking
- **Metadata:**
  - Created by
  - Created date
  - Last updated
  - Approved by
  - Approval date
  - Expiry date

---

## 🎨 Working with the Wiki Surface

### Viewing Curated Knowledge
1. Navigate to the **Curated Wiki**
2. Browse topics or use search
3. Click on a topic to view its page
4. Each page shows:
   - **Accepted knowledge** (currently verified)
   - **Verification badges** (✓ for accepted, ⚠️ for pending)
   - **Freshness indicators** (how recent the information is)
   - **Provenance** (click to see sources)
   - **Maintenance tags** (if any issues)
   - **Discussion links** (if disputed)

### In-Wiki Curation
Curators can perform actions directly on wiki blocks:
1. Hover over a block to see action buttons
2. Available actions:
   - **Verify:** Mark as verified/accepted
   - **Flag:** Flag for review
   - **Edit:** Edit the content
   - **Revert:** Revert to previous version
   - **Discuss:** Open discussion
   - **Resolve Conflict:** If the block was disputed
   - **Escalate:** Send to higher review tier
   - **Archive:** Remove from active view

---

## 🛡️ Trust Routing Explained

### How Knowledge is Processed

When new information is extracted or proposed:

```
Incoming Information
    ↓
┌─────────────────────┐
│  Trust Router        │
│                     │
│  if confidence >= 0.9│──── Auto-Accept ────▶ Curated Wiki
│     and trusted     │
│     and no conflict │
│                     │
│  if 0.7 <= confidence│── Pending/Review ──▶ Validation Queue
│     < 0.9           │
│     or needs check  │
│                     │
│  if confidence < 0.7│─── Escalation ────▶ Review Tier
│     or sensitive    │
└─────────────────────┘
```

### Confidence Factors
Your content's confidence score is based on:
1. **Parser Confidence:** How sure the system is about the extraction
2. **Source Reliability:** How trustworthy the source is
3. **Extraction Method:** Rule-based vs ML-based
4. **Corroboration:** How many sources agree
5. **Freshness:** How recent the information is

### Sensitivity Levels
- **Low:** Non-controversial, public information
  - Auto-accepted if confidence is high
- **Medium:** Potentially controversial
  - Requires review by Tier 1 (Field/Local)
- **High:** Highly sensitive
  - Escalated to Tier 3 (HQ/Thematic) for approval

---

## 🔍 Search Tips

### Basic Search
- Use the search bar at the top of any page
- Search across all topics, entities, and cards
- Results are ranked by relevance and recency

### Advanced Search
1. Click **Advanced Search** next to the search bar
2. Use filters:
   - **Type:** Documents, Entities, Cards, Discussions
   - **Domain:** Geographic, Crisis, Demographics, etc.
   - **Status:** Accepted, Pending, Disputed, Expired
   - **Date Range:** Filter by creation/modification date
   - **Source:** Filter by source organization
   - **Confidence:** Minimum confidence score

### Search Operators
| Operator | Example | Description |
|----------|---------|-------------|
| `AND` | `refugees AND food` | Both terms must be present |
| `OR` | `Syria OR Lebanon` | Either term can be present |
| `NOT` | `UNHCR NOT Syria` | Exclude documents with Syria |
| `" "` | `"World Food Programme"` | Exact phrase match |
| `*` | `refugee*` | Wildcard (refugee, refugees, etc.) |

---

## 📊 Verification States Explained

Each piece of knowledge goes through verification states:

```
                    ┌─────────────────┐
                    │     incoming     │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ↓                  ↓                  ↓
   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │  auto_accepted│   │    pending    │   │  escalated   │
   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
           │                  │                  │
           └──────────┬───────┴───────┬─────────┘
                      ↓               ↓
               ┌──────────────┐   ┌──────────────┐
               │   accepted    │   │   rejected    │
               └──────┬───────┘   └──────┬───────┘
                      │                  │
           ┌──────────┴──────────┬───────┴──────────┐
           ↓                     ↓                  ↓
    ┌──────────────┐      ┌──────────────┐   ┌──────────────┐
    │  superseded  │      │    merged     │   │no_consensus  │
    └──────────────┘      └──────────────┘   └──────────────┘
```

### State Descriptions

| State | Description | Can be Used? |
|-------|-------------|--------------|
| **incoming** | Newly extracted, not yet processed | ❌ No |
| **auto_accepted** | Automatically accepted (high confidence) | ✅ Yes |
| **pending** | Awaiting review | ⚠️ Limited (visible to reviewers) |
| **escalated** | Escalated to higher review tier | ❌ No |
| **accepted** | Reviewed and accepted | ✅ Yes |
| **rejected** | Reviewed and rejected | ❌ No |
| **merged** | Merged with existing knowledge | ✅ Yes (as merged) |
| **superseded** | Replaced by newer version | ❌ No (old version) |
| **no_consensus** | Unable to reach agreement | ❌ No |

---

## 🎯 Best Practices

### For Curators
1. **Always verify sources** - Don't accept claims without checking provenance
2. **Check for contradictions** - Use the conflict detection tools
3. **Add context** - When approving, add notes about why it's trustworthy
4. **Escalate when unsure** - Better to escalate than make a wrong decision
5. **Watch your domains** - Set up watches for areas you specialize in

### For Proposal Writers
1. **Always check validity** - Never use expired knowledge cards
2. **Review provenance** - Understand where the knowledge comes from
3. **Check for maintenance tags** - Be aware of potential issues
4. **Cite everything** - Ensure every claim can be traced back
5. **Acknowledge gaps** - If knowledge is incomplete, state this explicitly

### For Developers
1. **Follow TDD** - Write tests before implementation (NFR-006)
2. **Track provenance** - Every piece of data must be traceable (NFR-002)
3. **Handle edge cases** - Humanitarian data is often messy
4. **Optimize for curators** - Their workflow is the most important
5. **Prioritize reliability** - False positives are better than false negatives

---

## 🆘 Troubleshooting

### Common Issues

#### Documents Not Parsing
- **Symptom:** Document upload succeeds but no knowledge extracted
- **Solutions:**
  - Check document format is supported
  - Verify document is not password-protected
  - Try with a different document of same type
  - Check server logs for parsing errors

#### Low Confidence Scores
- **Symptom:** Extracted knowledge has low confidence scores
- **Solutions:**
  - Use higher quality source documents
  - Ensure documents are in good condition (not scanned PDFs)
  - Check if source is in source reliability list
  - Manually review and adjust confidence if appropriate

#### Graph Queries Slow
- **Symptom:** Database queries take a long time
- **Solutions:**
  - Add appropriate indexes
  - Check query complexity
  - Use EXPLAIN to analyze query plan
  - Consider query rewriting for better performance

#### Knowledge Cards Not Generating
- **Symptom:** Cards not appearing in library
- **Solutions:**
  - Check if required data exists in graph
  - Verify card generation job is running
  - Check for errors in card generation logs
  - Ensure templates are properly configured

### Getting Help
1. **Check Documentation:** This guide and the full spec.md
2. **Search Issues:** Look for similar issues in the issue tracker
3. **Ask in Chat:** Use the team chat channel
4. **Create Issue:** If it's a bug or feature request, create an issue
5. **Contact Admin:** For urgent production issues

---

## 📞 Support & Contact

| Issue Type | Contact | Response Time |
|------------|---------|---------------|
| Bug Report | Issue Tracker | 24 hours |
| Feature Request | Issue Tracker | 48 hours |
| Urgent Production Issue | Admin Team | 4 hours |
| General Question | Team Chat | 4 hours |
| Training Request | Training Team | 48 hours |

---

## 🔄 Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-04-12 | 1.0 | Initial quick start guide |

---

## 📚 Additional Resources

- [Full Specification (spec.md)](./spec.md) - Complete project specification
- [Implementation Plan (plan.md)](./plan.md) - Detailed implementation roadmap
- [Task List (tasks.md)](./tasks.md) - Development task tracking
- [Research Notes (research.md)](./research.md) - Technical research and decisions
- [API Documentation](../api/) - REST API reference
- [Developer Guide](../dev-guide.md) - Detailed development instructions

---

*Happy knowledge management! 🎉*
