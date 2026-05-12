# Metamorph Quick Start Guide (v3.0 - Website-First)

**Spec ID:** 001-metamorph  
**Version:** 3.0  
**Status:** Draft  
**Date:** 2026-05-12

---

## 🚀 Getting Started with Metamorph v3.0

Metamorph v3.0 introduces a **website-first workflow**. Instead of manually uploading documents, you now:
1. **Define a website URL** to scrape
2. **Let the system automatically explore** and identify all scrapable files
3. **Select which files** you want to ingest (all or specific subset)
4. **Ingestion starts automatically** upon confirmation

This guide will help you set up and start using the new website-to-knowledge pipeline.

---

## 📋 Prerequisites

### For Developers
- **Python** 3.10+ (recommended: 3.11 or 3.12)
- **Node.js** 18+ (optional, for Playwright/JS sites)
- **Git**
- **Docker** (optional, for containerized deployment)
- **Neo4j** 5.x (or Neo4j Aura for managed service)
- **Redis** (optional, for caching previews)

### For Users (Website Scrapers)
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Internet connection
- Websites to scrape (URLs)

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

# Additional packages for crawling
pip install requests beautifulsoup4 lxml urllib3
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

#### 4. Set Up Redis (Optional for Preview Caching)
```bash
# Using Docker
docker run \
  --name metamorph-redis \
  -p 6379:6379 \
  -d redis:alpine
```

#### 5. Configure Environment
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
REDIS_URL=redis://localhost:6379/0  # Optional

# Crawling settings (configurable):
CRAWLER_MAX_DEPTH=3
CRAWLER_MAX_PAGES=1000
CRAWLER_DELAY=1.0  # seconds between requests
CRAWLER_USER_AGENT=MetamorphBot/1.0
```

#### 6. Initialize Database
```bash
# Run database initialization script
python scripts/init_db.py

# This will:
# - Create Website, DiscoveredFile, ScrapeSession, IngestionJob, Document nodes
# - Set up indexes for crawling entities
# - Load initial schema
```

#### 7. Start Backend Server
```bash
# From backend directory
cd backend
uvicorn app.main:app --reload --port 8000

# The API will be available at: http://localhost:8000
```

#### 8. Start Frontend (Optional)
```bash
# From frontend directory
cd frontend
npm install
npm run dev

# The UI will be available at: http://localhost:3000
```

---

## 🎯 First Steps for Different User Types

### For Website Scrapers (NEW - Primary Role)

#### Step 1: Access the System
1. Open your web browser
2. Navigate to the Metamorph URL (e.g., http://localhost:3000)
3. Log in (or create an account if first time)

#### Step 2: Start a New Scraping Job
1. Click **"New Scrape Job"** or **"Add Website"** button
2. Enter the website URL you want to scrape (e.g., `https://www.unhcr.org`)
3. Click **"Start Discovery"**

#### Step 3: System Automatically Explores the Website
- The system will:
  - Check if the website is accessible
  - Parse `robots.txt` to check scraping permissions
  - Look for `sitemap.xml` and parse it
  - Crawl the website starting from the provided URL
  - Follow internal links within the same domain
  - Identify all scrapable files (PDFs, Word docs, Excel, etc.)

- You'll see a progress indicator showing:
  - Pages crawled
  - Files discovered
  - Estimated time remaining

#### Step 4: Review Discovered Files
Once crawling is complete, you'll see a list of all discovered files with:
- **File name** (e.g., `Global_Trends_2024.pdf`)
- **File type** (e.g., PDF, Word, Excel)
- **File size** (e.g., 2.5 MB)
- **Last modified** date
- **URL** (full path to the file)

Files are grouped by type for easier browsing:
- 📄 **PDF Documents**
- 📝 **Word Documents**
- 📊 **Spreadsheets**
- 📑 **Presentations**
- 🌐 **Web Pages**
- 📋 **Other Files**

#### Step 5: Preview Files (Optional)
- Click on any file to see a preview
- For text files: First 500 characters
- For PDFs: First page text
- For Word/Excel: Extracted text preview
- For HTML: Clean text extraction

#### Step 6: Select Files for Ingestion
- Use the checkboxes to select files:
  - **Select All** - Check the box at the top
  - **Select by Type** - Use the type filter dropdown
  - **Select by Date Range** - Use the date filter
  - **Individual Selection** - Check specific files
- Selected count is displayed (e.g., "12 of 45 files selected")

#### Step 7: Start Ingestion
1. Click **"Start Ingestion"** button
2. Confirm your selection in the dialog
3. Ingestion starts **automatically**!

The system will:
- Queue all selected files
- Download files from URLs
- Parse them using Docling (standard) or MinerU (complex layouts)
- Extract knowledge and store in the graph database
- Track progress for each file

You'll see:
- Overall progress percentage
- Individual file status (queued, downloading, parsing, complete, error)
- Estimated time remaining
- Error messages for any failed files

#### Step 8: View Results
Once ingestion is complete:
- Knowledge is extracted and stored in the graph
- You can view the extracted knowledge in the Curated Wiki
- The system flags any conflicts or changes for review
- Validation cards are created for items needing your attention

---

### For Curators

The curation workflow is similar to v2.0, but now knowledge comes from websites:

#### 1. Access the System
1. Open your web browser
2. Navigate to the Metamorph URL
3. Log in using your credentials

#### 2. Understand the Dashboard
- **Validation Queue:** Shows pending validation cards from ingested website content
- **Recent Activity:** Shows recent scraping jobs and changes
- **Discovered Websites:** List of websites that have been scraped
- **My Tasks:** Shows tasks assigned to you
- **Search:** Search for specific topics, entities, or cards

#### 3. Process a Validation Card
1. Click on a validation card in the queue
2. Review the **Current Value** vs **Proposed Value** (from website)
3. Check the **Diff** to see exactly what changed
4. Review **Evidence** and **Provenance** (now includes source website and file URL)
5. Check the **Confidence Score** and **Sensitivity Classification**
6. Take action:
   - **Approve** - If the change is accurate and well-sourced
   - **Reject** - If the change is incorrect or poorly sourced
   - **Merge/Edit** - If the change needs modification
   - **Escalate** - If you're unsure or it's sensitive
   - **Open Discussion** - If it needs community input

#### 4. Monitor Website Scraping
- View the **Websites** section to see:
  - List of all scraped websites
  - Number of files discovered per website
  - Number of files ingested
  - Last scrape date
  - Scrape status (success, error, pending)

---

### For Proposal Writers

#### 1. Search for Knowledge Cards
1. Navigate to **Knowledge Library**
2. Use filters to narrow down:
   - Domain (Geographic, Crisis, etc.)
   - Card Type (KC-1 to KC-6)
   - Validity (ensure cards are not expired)
   - **Source Website** (NEW - filter by website)
   - Date Range
3. Review search results

#### 2. Check Source Information
- Each card now shows:
  - **Source Website** - Where the knowledge came from
  - **Source File** - The specific file that was ingested
  - **Ingestion Date** - When the file was processed
  - **Provenance Chain** - Full trace from website → file → knowledge

#### 3. Use Cards in Proposals
1. Select relevant cards for your proposal
2. Click **Add to Proposal**
3. Arrange cards in logical order
4. The system will:
   - Check all cards are valid (not expired)
   - Generate a draft proposal
   - Score interventions based on context
5. Review the generated draft
6. Make manual adjustments as needed

#### 4. Export Proposal
1. Review the final proposal
2. Click **Export**
3. Choose format (PDF, Word, HTML)
4. Download and use in your workflow

---

## 🌐 Website Scraping Workflow (v3.0)

### The New Workflow Explained

```
┌─────────────────────────────────────────────────────────────────┐
│                    METAMORPH v3.0 USER WORKFLOW                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  STEP 1: DEFINE WEBSITE                                           │
│  ┌─────────────────────────┐                                    │
│  │  Enter URL:              │                                    │
│  │  [https://_________]     │◄── User provides website URL      │
│  │                         │                                    │
│  │  [Start Discovery]      │                                    │
│  └─────────────────────────┘                                    │
│            │                                                      │
│            ▼                                                      │
│  STEP 2: AUTOMATIC EXPLORATION                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ✓ Checking robots.txt                                  │   │
│  │  ✓ Parsing sitemap.xml                                   │   │
│  │  ✓ Crawling website (0/45 pages)                         │   │
│  │  ✓ Found 12 PDFs, 8 Word docs, 5 Excel files              │   │
│  │  ┌─────────────────┐                                    │   │
│  │  │ Progress: 85%   │                                    │   │
│  │  └─────────────────┘                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│            │                                                      │
│            ▼                                                      │
│  STEP 3: REVIEW & SELECT FILES                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📁 Discovered Files (25 total)                           │   │
│  │                                                              │   │
│  │  📄 PDF DOCUMENTS (12)                                    │   │
│  │  ✓ [ ] Global_Trends_2024.pdf (2.5 MB, 2024-03-15)      │   │
│  │  ✓ [ ] Annual_Report_2023.pdf (5.1 MB, 2024-01-20)      │   │
│  │  ✗ [ ] Quarterly_Update.pdf (1.2 MB, 2024-04-01)        │   │
│  │                                                              │   │
│  │  📝 WORD DOCUMENTS (8)                                     │   │
│  │  ✓ [ ] Strategy_Document.docx (1.8 MB, 2024-02-10)     │   │
│  │  ✗ [ ] Meeting_Notes.docx (0.5 MB, 2024-04-15)         │   │
│  │                                                              │   │
│  │  Selected: 2 of 25 files                                    │   │
│  │                                                              │   │
│  │  [Select All] [Select by Type ▼] [Select by Date ▼]      │   │
│  │                                                              │   │
│  │  [Start Ingestion]                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│            │                                                      │
│            ▼                                                      │
│  STEP 4: AUTOMATIC INGESTION                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Ingestion Progress                                        │   │
│  │                                                              │   │
│  │  Global_Trends_2024.pdf    ████████████░░░░  80%         │   │
│  │  Strategy_Document.docx   ████████████████░░░░  95%         │   │
│  │                                                              │   │
│  │  Overall: 87% complete                                       │   │
│  │  Estimated time remaining: 32 seconds                     │   │
│  │                                                              │   │
│  │  [View Details] [Cancel]                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│            │                                                      │
│            ▼                                                      │
│  STEP 5: KNOWLEDGE READY!                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ✓ Ingestion Complete!                                    │   │
│  │                                                              │   │
│  │  2 files successfully ingested                            │   │
│  │  45 knowledge items extracted                              │   │
│  │  3 validation cards created for review                     │   │
│  │                                                              │   │
│  │  [View Knowledge Graph] [Review Validation Cards]         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features of v3.0

✅ **Automatic Discovery:** No need to manually find documents
✅ **File Selection:** Choose exactly what to ingest
✅ **Automatic Ingestion:** Starts immediately upon confirmation
✅ **Progress Tracking:** See exactly what's happening
✅ **Provenance Tracking:** Every piece of knowledge linked to source website and file

---

## 📖 Understanding the New Data Model

### Websites
- A website is the starting point for knowledge extraction
- Each website has:
  - URL (the root URL you provide)
  - Domain name
  - Discovery date
  - Last scrape date
  - Total files discovered
  - Total files ingested

### Discovered Files
- Files found during website crawling
- Each file has:
  - URL (full path to the file)
  - File type (PDF, Word, Excel, etc.)
  - File size
  - Last modified date
  - Status (discovered, selected, ingested, error)

### Scrape Sessions
- Each time you scrape a website, a session is created
- Tracks:
  - When the scrape started and completed
  - How many files were discovered
  - How many were selected
  - How many were ingested
  - Any errors that occurred

### Documents
- The actual parsed documents
- Each document has:
  - Original URL
  - Source website
  - Source file
  - Download date
  - Parse date
  - Parsing tool used (Docling or MinerU)
  - Extracted text and metadata

### Knowledge Graph
- Extracted knowledge is stored as:
  - **Entities** (people, organizations, locations, etc.)
  - **Relationships** (connections between entities)
  - **Properties** (attributes and metadata)
  - **Provenance** (traceability to source website and file)

---

## 🎨 Working with the Wiki Surface

### Viewing Curated Knowledge
1. Navigate to the **Curated Wiki**
2. Browse topics or use search
3. Click on a topic to view its page
4. Each page shows:
   - **Accepted knowledge** (currently verified)
   - **Source Information** (NEW - shows which website and file the knowledge came from)
   - **Verification badges** (✓ for accepted, ⚠️ for pending)
   - **Freshness indicators** (how recent the information is)
   - **Provenance** (click to see full source chain)
   - **Maintenance tags** (if any issues)
   - **Discussion links** (if disputed)

### In-Wiki Curation
Curators can perform actions directly on wiki blocks:
1. Hover over a block to see action buttons
2. Available actions:
   - **Verify** - Mark as verified/accepted
   - **Flag** - Flag for review
   - **Edit** - Edit the content
   - **Revert** - Revert to previous version
   - **Discuss** - Open discussion
   - **Resolve Conflict** - If the block was disputed
   - **Escalate** - Send to higher review tier
   - **Archive** - Remove from active view

---

## 🛡️ Trust Routing & Provenance

### How Knowledge is Processed

When new information is extracted from a website:

```
Discovered File
    ↓
┌─────────────────────┐
│  Ingestion Pipeline  │
│                     │
│  - Download file    │
│  - Parse document    │
│  - Extract triplets  │
│  - Store in graph    │
└────────────┬────────┘
             │
     ┌───────▼───────┐
     │  Trust Router  │
     │               │
     │  if confidence ≥ 0.9 │──── Auto-Accept ────▶ Curated Wiki
     │     and trusted     │
     │     and no conflict │
     │                 │
     │  if 0.7 ≤ confidence│── Pending/Review ──▶ Validation Queue
     │     < 0.9           │
     │     or needs check  │
     │                 │
     │  if confidence < 0.7│─── Escalation ────▶ Review Tier
     │     or sensitive    │
     └─────────────────┘
```

### Confidence Factors (Updated for v3.0)

Your content's confidence score is based on:
1. **Parser Confidence:** How sure the system is about the extraction
2. **Source Reliability:** How trustworthy the source website is
3. **Extraction Method:** Rule-based vs ML-based
4. **Corroboration:** How many sources agree
5. **Freshness:** How recent the information is
6. **Website Domain:** Known/trusted domains score higher

### Website Domain Reliability

- **Trusted (0.95):** UN websites, government domains, academic institutions
- **Known (0.85):** Major news organizations, established NGOs
- **Unknown (0.70):** New domains, requires review
- **Untrusted (0.30):** Known problematic domains

---

## 🔍 Search Tips

### Basic Search
- Use the search bar at the top of any page
- Search across all topics, entities, cards, and **websites**
- Results are ranked by relevance and recency

### Advanced Search
1. Click **Advanced Search** next to the search bar
2. Use filters:
   - **Type:** Documents, Entities, Cards, Discussions, **Websites**
   - **Domain:** Geographic, Crisis, Demographics, etc.
   - **Source Website:** Filter by specific website
   - **Status:** Accepted, Pending, Disputed, Expired
   - **Date Range:** Filter by creation/modification date
   - **File Type:** PDF, Word, Excel, etc.

### Search Operators
| Operator | Example | Description |
|----------|---------|-------------|
| `AND` | `refugees AND food` | Both terms must be present |
| `OR` | `Syria OR Lebanon` | Either term can be present |
| `NOT` | `UNHCR NOT Syria` | Exclude documents with Syria |
| `" "` | `"World Food Programme"` | Exact phrase match |
| `*` | `refugee*` | Wildcard (refugee, refugees, etc.) |
| `website:` | `website:unhcr.org` | Filter by source website |

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
| **incoming** | Newly extracted from website, not yet processed | ❌ No |
| **auto_accepted** | Automatically accepted (high confidence) | ✅ Yes |
| **pending** | Awaiting review | ⚠️ Limited (visible to reviewers) |
| **escalated** | Escalated to higher review tier | ❌ No |
| **accepted** | Reviewed and accepted | ✅ Yes |
| **rejected** | Reviewed and rejected | ❌ No |
| **merged** | Merged with existing knowledge | ✅ Yes (as merged) |
| **superseded** | Replaced by newer version | ❌ No (old version) |
| **no_consensus** | Unable to reach agreement | ❌ No |

---

## 🎯 Best Practices (v3.0)

### For Website Scrapers
1. **Start with trusted websites** - UN, government, academic sites have high-quality content
2. **Use sitemap.xml when available** - Faster and more reliable than crawling
3. **Select files carefully** - Focus on relevant documents for your needs
4. **Monitor progress** - Check ingestion status and address any errors
5. **Respect website policies** - Don't scrape sites that block crawlers
6. **Schedule regular updates** - Set up re-scraping for websites that change frequently

### For Curators
1. **Check source website** - Verify the website is reliable before approving
2. **Review file context** - Understand where the knowledge came from
3. **Check for duplicates** - The same file might be on multiple websites
4. **Add context** - When approving, add notes about the source website
5. **Escalate when unsure** - Better to escalate than make a wrong decision

### For Proposal Writers
1. **Verify source websites** - Check the provenance of knowledge cards
2. **Check for freshness** - Ensure knowledge from websites is up to date
3. **Look for multiple sources** - Knowledge corroborated by multiple websites is more reliable
4. **Cite everything** - Include source website and file in citations
5. **Acknowledge limitations** - Note if knowledge comes from a single source

### For Developers
1. **Respect robots.txt** - Always check and honor website scraping policies
2. **Implement rate limiting** - Don't overwhelm websites with requests
3. **Handle errors gracefully** - Websites can be unreliable, expect failures
4. **Cache previews** - Preview generation can be resource-intensive
5. **Track provenance** - Every piece of data must be traceable to source
6. **Follow TDD** - Write tests before implementation (NFR-006)

---

## 🆘 Troubleshooting (v3.0)

### Common Issues

#### Website Not Accessible
- **Symptom:** Crawling fails immediately with "Website not accessible"
- **Solutions:**
  - Check the URL is correct
  - Verify the website is online
  - Check if the website blocks crawlers (robots.txt)
  - Try a different website

#### No Files Discovered
- **Symptom:** Crawling completes but no files found
- **Solutions:**
  - Check if the website has any scrapable files
  - Try increasing the crawl depth in settings
  - Try increasing the max pages limit
  - Check if the website uses JavaScript (may need Playwright)
  - Verify the website allows crawling

#### Crawling is Slow
- **Symptom:** Crawling takes a long time
- **Solutions:**
  - Check if the website has rate limiting
  - Increase the delay between requests
  - Reduce the crawl depth
  - Reduce the max pages limit
  - Check server resources (CPU, memory)

#### Ingestion Failures
- **Symptom:** Files fail to ingest
- **Solutions:**
  - Check the error message for specific issues
  - Try re-ingesting the failed files
  - Check if files are accessible (not 404)
  - Check if files are password-protected
  - Check if files are too large

#### Preview Not Available
- **Symptom:** Preview shows "Preview unavailable"
- **Solutions:**
  - File may be binary or unsupported format
  - File may be too large for preview
  - Preview generation may have timed out
  - Try opening the file directly in browser

### Getting Help
1. **Check Documentation:** This guide and the full spec.md v3.0
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
| Crawling Problem | Support Team | 4 hours |
| General Question | Team Chat | 4 hours |
| Training Request | Training Team | 48 hours |

---

## 🔄 Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-12 | 3.0 | Major update for website-first workflow. Rewrote entire guide to reflect new workflow: website URL input → automatic exploration → file selection → automatic ingestion. Added website scraper role, updated all sections for new data model (Website, DiscoveredFile, ScrapeSession, IngestionJob). Added troubleshooting for crawling issues. |
| 2026-04-12 | 1.0 | Initial quick start guide |

---

## 📚 Additional Resources

- [Full Specification (spec.md)](./spec.md) - Complete project specification with website-first workflow
- [Implementation Plan (plan.md)](./plan.md) - Detailed implementation roadmap for v3.0
- [Task List (tasks.md)](./tasks.md) - Development task tracking with new crawling tasks
- [Research Notes (research.md)](./research.md) - Technical research on website crawling and discovery
- [API Documentation](../api/) - REST API reference including website scraping endpoints
- [Developer Guide](../dev-guide.md) - Detailed development instructions

---

*Happy website scraping! 🌐🎉*
