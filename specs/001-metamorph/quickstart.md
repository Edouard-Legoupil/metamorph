# Quickstart Guide: Metamorph Website-to-Knowledge System

**Version**: 3.0 | **Date**: 2026-05-12

This guide provides step-by-step instructions for setting up, running, and using the Metamorph system for website-to-knowledge extraction.

---

## 🚀 Getting Started

### Prerequisites

**System Requirements**:
- **Operating System**: Linux (Ubuntu 22.04 LTS recommended)
- **CPU**: 4+ cores
- **RAM**: 16GB+ (32GB recommended for large websites)
- **Disk**: 100GB+ SSD (depends on document volume)
- **Docker**: 20.10+ with Docker Compose
- **Python**: 3.11+
- **Node.js**: 18.x+ (for frontend development)

**Required Tools**:
```bash
# Install dependencies on Ubuntu
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl

# Install Docker
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Install Node.js (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Install Python dependencies
pip install poetry
```

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/metamorph.git
cd metamorph
git checkout 001-metamorph
```

### 2. Set Up Backend

```bash
cd backend

# Install Python dependencies
poetry install

# Create .env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Example `.env` file**:
```env
# Database configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password
NEO4J_DB=metamorph

# API configuration
API_HOST=0.0.0.0
API_PORT=8000
API_VERSION=v1
API_TITLE=Metamorph API
API_DESCRIPTION=Website-to-Knowledge Intelligence System

# Crawling configuration
MAX_CONCURRENT_CRAWLS=5
REQUEST_TIMEOUT=30
USER_AGENT=Metamorph/3.0 (+https://metamorph.example.com)
RESPECT_ROBOTS_TXT=true
CRAWL_DELAY=1000
MAX_DEPTH=5

# File processing
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,docx,xlsx,pptx,html,txt
TEMP_DIR=/tmp/metamorph

# Security
JWT_SECRET=your_very_secure_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/metamorph/api.log
```

### 3. Set Up Frontend

```bash
cd ../frontend

# Install Node.js dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Example frontend `.env` file**:
```env
# API endpoint
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1

# Application configuration
REACT_APP_APP_NAME=Metamorph
REACT_APP_VERSION=3.0.0
REACT_APP_ENV=development

# Feature flags
REACT_APP_FEATURE_WEBSITE_CRAWLING=true
REACT_APP_FEATURE_FILE_SELECTION=true
REACT_APP_FEATURE_INGESTION=true
REACT_APP_FEATURE_CURATION=true
REACT_APP_FEATURE_PROPOSAL_DRAFTING=true

# Analytics (optional)
REACT_APP_GA_TRACKING_ID=UA-XXXXXX-X
```

### 4. Set Up Docker Services

```bash
cd ../

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  neo4j:
    image: neo4j:5.13.0-enterprise
    container_name: metamorph_neo4j
    ports:
      - "7474:7474"  # Browser interface
      - "7687:7687"  # Bolt protocol
    environment:
      - NEO4J_AUTH=neo4j/your_secure_password
      - NEO4J_dbms_memory_heap_max__size=8G
      - NEO4J_dbms_memory_pagecache_size=4G
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins
    networks:
      - metamorph_network
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "your_secure_password", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7.0-alpine
    container_name: metamorph_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - metamorph_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: metamorph_backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=your_secure_password
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      neo4j:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - /tmp/metamorph:/tmp/metamorph
    networks:
      - metamorph_network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: metamorph_frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - metamorph_network
    restart: unless-stopped

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  neo4j_plugins:
  redis_data:

networks:
  metamorph_network:
    driver: bridge
EOF
```

### 5. Build and Start Services

```bash
# Build and start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## 🌐 Using Metamorph

### 1. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (username: neo4j, password: your_secure_password)

### 2. Website Scraping Workflow

#### Step 1: Define a Website to Scrape

1. **Navigate** to the Website Management page
2. **Click** "Add New Website"
3. **Enter** the website URL (e.g., `https://unhcr.org`)
4. **Select** scrape frequency (manual, daily, weekly, monthly)
5. **Click** "Start Scraping"

**API Example**:
```bash
curl -X POST http://localhost:8000/api/v1/websites \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "url": "https://unhcr.org",
    "scrape_frequency": "manual",
    "title": "UNHCR - The UN Refugee Agency",
    "description": "Official website of the UN Refugee Agency"
  }'
```

#### Step 2: Review Discovered Files

1. **Wait** for crawling to complete (check progress in UI)
2. **Navigate** to the File Discovery page for your website
3. **Browse** the list of discovered files with:
   - Filename, URL, file type, size, last modified date
   - Preview of file content
   - Grouping by file type

**API Example - List discovered files**:
```bash
curl -X GET http://localhost:8000/api/v1/websites/{website_id}/files \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Step 3: Select Files for Ingestion

1. **Use bulk selection** options:
   - Select all files
   - Select by file type (PDFs, Word docs, etc.)
   - Select by date range
   - Individual file selection

2. **Review** your selection (count shown in UI)
3. **Click** "Start Ingestion"

**API Example - Select files**:
```bash
curl -X POST http://localhost:8000/api/v1/websites/{website_id}/files/select \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "file_ids": ["file_id_1", "file_id_2", "file_id_3"]
  }'
```

#### Step 4: Monitor Ingestion Progress

1. **View** the ingestion dashboard:
   - Overall progress percentage
   - Individual file status (queued, processing, completed, error)
   - Real-time updates
   - Error panel for failed files

2. **Handle errors** if any:
   - Review error details in the error panel
   - Retry failed files individually or in bulk
   - Download error logs for support

**API Example - Start ingestion**:
```bash
curl -X POST http://localhost:8000/api/v1/websites/{website_id}/ingest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "notify_email": "user@example.com",
    "priority": "normal"
  }'
```

### 3. Knowledge Curation

#### Review Knowledge Cards

1. **Navigate** to the Knowledge Cards dashboard
2. **Filter** by:
   - Card type (KC-1 to KC-6)
   - Domain (geographic, crisis, demographics, etc.)
   - Status (draft, approved, expired, etc.)
   - Validity period

3. **View** card details:
   - Source website and file information
   - Provenance tracking
   - Verification state
   - Related entities and events

**API Example - List knowledge cards**:
```bash
curl -X GET http://localhost:8000/api/v1/cards \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Curate Wiki Blocks

1. **Select** a knowledge card
2. **Review** individual wiki blocks:
   - Content and formatting
   - Verification state
   - Provenance information
   - Maintenance tags

3. **Take curation actions**:
   - **Verify**: Mark as accepted
   - **Flag**: Mark as disputed or needing review
   - **Edit**: Modify content directly
   - **Discuss**: Open discussion thread
   - **View History**: See revision history
   - **Revert**: Roll back to previous version

**API Example - Update wiki block**:
```bash
curl -X PATCH http://localhost:8000/api/v1/cards/{card_id}/blocks/{block_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "verification_state": "accepted",
    "content": "Updated content with proper citations"
  }'
```

### 4. Validation Cards

#### Review Validation Queue

1. **Navigate** to the Validation Dashboard
2. **Filter** by:
   - Review tier (Tier 1, Tier 2, Tier 3)
   - Sensitivity level
   - Status (open, under_review, etc.)
   - Contradiction type

3. **Select** a validation card to review

#### Validation Card Interface

Each card shows:
- **Current Value**: Currently accepted value
- **Proposed Value**: New/proposed value
- **Diff**: Visual difference between values
- **Evidence**: Supporting documentation
- **Provenance**: Source website, file, extraction details
- **Confidence Score**: Automatic confidence assessment
- **Sensitivity**: Classification level

#### Available Actions

- **Approve**: Accept the proposed change
- **Reject**: Discard the proposed change
- **Merge/Edit**: Modify and accept
- **Escalate**: Send to higher review tier
- **Open Discussion**: Create discussion thread
- **Mark as Duplicate**: Identify as redundant
- **Mark as No Consensus**: Unable to reach agreement

**API Example - Resolve validation card**:
```bash
curl -X POST http://localhost:8000/api/v1/validation/cards/{card_id}/approve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "resolution": "Approved after reviewing evidence from source website",
    "assigned_tier": "tier_1"
  }'
```

### 5. Discussion Threads

#### Create Discussion Thread

1. **Navigate** to the Discussion Forum
2. **Click** "New Discussion"
3. **Select** context:
   - Linked to specific entity
   - Linked to wiki block
   - Linked to knowledge card
   - General discussion

4. **Provide** details:
   - Title and topic
   - Initial comment with evidence
   - Mention relevant users

**API Example - Create discussion**:
```bash
curl -X POST http://localhost:8000/api/v1/discussion/threads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Discrepancy in refugee numbers",
    "topic": "Data accuracy",
    "linked_entity_id": "entity_123",
    "content": "The reported refugee numbers conflict with UNHCR official statistics...",
    "evidence_quality": "high",
    "policy_compliance": true
  }'
```

#### Participate in Discussion

1. **View** thread details and history
2. **Add comments** with:
   - Supporting evidence
   - Source citations (including website URLs)
   - Policy references
   - Data analysis

3. **Take actions**:
   - Propose patches/solutions
   - Mention other reviewers
   - Vote on proposals
   - Mark thread status

---

## 🔧 Administration

### User Management

```bash
# Create admin user
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{
    "email": "admin@example.com",
    "password": "secure_password_123",
    "full_name": "System Administrator",
    "role": "admin",
    "is_active": true
  }'

# List users
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"

# Update user role
curl -X PATCH http://localhost:8000/api/v1/users/{user_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{
    "role": "curator",
    "review_tier": "tier_2"
  }'
```

### System Monitoring

```bash
# Check service health
docker-compose ps

# View backend logs
docker-compose logs backend -f

# View frontend logs  
docker-compose logs frontend -f

# Check Neo4j status
docker-compose exec neo4j cypher-shell -u neo4j -p your_secure_password "CALL dbms.listConnections()"

# Monitor API performance
curl http://localhost:8000/metrics
```

### Backup and Restore

```bash
# Backup Neo4j database
docker-compose exec neo4j neo4j-admin dump --database=metamorph --to=/backups/metamorph-backup.dump

# Restore Neo4j database (stop service first)
docker-compose stop neo4j
docker-compose exec neo4j neo4j-admin load --from=/backups/metamorph-backup.dump --database=metamorph --force
docker-compose start neo4j

# Backup application data
mkdir -p backups/$(date +%Y-%m-%d)
cp -r specs backups/$(date +%Y-%m-%d)/
docker-compose exec backend pg_dump -U postgres metamorph > backups/$(date +%Y-%m-%d)/postgres.sql
```

---

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
poetry run pytest tests/unit/ -v
poetry run pytest tests/integration/ -v
poetry run pytest tests/ --cov=app --cov-report=html

# Frontend tests
cd ../frontend
npm test
npm run test:coverage

# End-to-end tests
npm run test:e2e
```

### Building for Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Frontend production build
cd frontend
npm run build
```

### Debugging

```bash
# Access Python shell with app context
cd backend
poetry run python -c "
from app.main import app
from app.database import SessionLocal
print('Database connection successful')
"

# Access Neo4j console
docker-compose exec neo4j cypher-shell -u neo4j -p your_secure_password

# Profile API endpoints
poetry run python -m cProfile -s cumtime -m uvicorn app.main:app --reload
```

---

## 📖 API Reference

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "your_password"
  }'

# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token"
  }'
```

### Website Endpoints

```bash
# Create website
POST /api/v1/websites

# List websites
GET /api/v1/websites

# Get website details
GET /api/v1/websites/{id}

# Update website
PATCH /api/v1/websites/{id}

# Delete website
DELETE /api/v1/websites/{id}

# Start scraping
POST /api/v1/websites/{id}/scrape

# List discovered files
GET /api/v1/websites/{id}/files

# Select files for ingestion
POST /api/v1/websites/{id}/files/select

# Deselect files
POST /api/v1/websites/{id}/files/deselect

# Start ingestion
POST /api/v1/websites/{id}/ingest

# Get scrape status
GET /api/v1/websites/{id}/scrape-status
```

### Knowledge Card Endpoints

```bash
# List knowledge cards
GET /api/v1/cards

# Get specific card
GET /api/v1/cards/{id}

# Create knowledge card
POST /api/v1/cards

# Update knowledge card
PATCH /api/v1/cards/{id}

# List card blocks
GET /api/v1/cards/{id}/blocks

# Get specific block
GET /api/v1/cards/{id}/blocks/{block_id}

# Update block
PATCH /api/v1/cards/{id}/blocks/{block_id}

# Approve card
POST /api/v1/cards/{id}/approve

# Reject card
POST /api/v1/cards/{id}/reject
```

### Curation Endpoints

```bash
# List validation cards
GET /api/v1/validation/cards

# Get validation card
GET /api/v1/validation/cards/{id}

# Approve validation card
POST /api/v1/validation/cards/{id}/approve

# Reject validation card
POST /api/v1/validation/cards/{id}/reject

# Merge validation card
POST /api/v1/validation/cards/{id}/merge

# Escalate validation card
POST /api/v1/validation/cards/{id}/escalate

# List discussion threads
GET /api/v1/discussion/threads

# Create discussion thread
POST /api/v1/discussion/threads

# Add comment to thread
POST /api/v1/discussion/threads/{id}/comments
```

---

## 🎯 Best Practices

### Website Crawling

1. **Start small**: Begin with a single website before scaling
2. **Respect robots.txt**: Always honor website policies
3. **Monitor performance**: Track crawl rates and adjust concurrency
4. **Handle errors gracefully**: Implement robust retry logic
5. **Validate URLs**: Ensure URLs are properly formatted before crawling

### File Selection

1. **Review carefully**: Check file previews before selection
2. **Use filters**: Leverage file type and date filters for efficiency
3. **Start with recent files**: Prioritize recently modified documents
4. **Monitor file sizes**: Be mindful of storage constraints
5. **Document decisions**: Keep records of selection criteria

### Knowledge Curation

1. **Verify provenance**: Always check source information
2. **Cross-reference**: Compare with multiple sources when possible
3. **Document disputes**: Use discussion threads for contested knowledge
4. **Regular reviews**: Schedule periodic knowledge validation
5. **Monitor expiry**: Track validity periods and update cards proactively

### System Maintenance

1. **Regular backups**: Automate daily backups with verification
2. **Monitor performance**: Track key metrics and set alerts
3. **Update dependencies**: Keep software current with security patches
4. **Test upgrades**: Validate changes in staging before production
5. **Document processes**: Maintain runbooks for common operations

---

## 🆘 Troubleshooting

### Common Issues

**Issue: Crawling fails with 403 errors**
- **Solution**: Check robots.txt compliance and user-agent settings
- **Command**: `curl -I https://example.com/robots.txt`

**Issue: File ingestion stalls**
- **Solution**: Check error panel for specific failures
- **Command**: `docker-compose logs backend | grep ERROR`

**Issue: Neo4j connection refused**
- **Solution**: Verify container health and credentials
- **Command**: `docker-compose ps neo4j`

**Issue: Frontend doesn't load**
- **Solution**: Check API connectivity and CORS settings
- **Command**: `curl -v http://localhost:8000/api/v1/health`

**Issue: Memory errors during parsing**
- **Solution**: Increase Docker memory limits and process files in batches
- **Command**: `docker stats`

### Debugging Commands

```bash
# Check container resource usage
docker stats

# Inspect container logs
docker-compose logs --tail=100 service_name

# Test database connection
docker-compose exec neo4j cypher-shell -u neo4j -p your_password "RETURN 'Connection successful'"

# Test API endpoint
curl -v http://localhost:8000/api/v1/health

# Check network connectivity
docker network inspect metamorph_network
```

---

## 📚 Resources

### Documentation

- **Official Docs**: [Metamorph Documentation](https://metamorph.example.com/docs)
- **API Reference**: [Swagger UI](http://localhost:8000/docs)
- **Architecture**: [System Architecture Guide](ARCHITECTURE.md)
- **Data Model**: [Data Model Reference](data-model.md)

### Support

- **GitHub Issues**: [https://github.com/your-org/metamorph/issues](https://github.com/your-org/metamorph/issues)
- **Community Forum**: [https://community.metamorph.example.com](https://community.metamorph.example.com)
- **Email Support**: support@metamorph.example.com

### Learning

- **Neo4j Documentation**: [https://neo4j.com/docs/](https://neo4j.com/docs/)
- **FastAPI Tutorial**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **React Documentation**: [https://react.dev/](https://react.dev/)
- **Web Crawling Guide**: [https://developers.google.com/search/docs/crawling-intro](https://developers.google.com/search/docs/crawling-intro)

---

## 🎉 Next Steps

Now that you have Metamorph up and running:

1. **Start small**: Begin with one website and a few files
2. **Explore features**: Try all the workflows (crawling, ingestion, curation)
3. **Provide feedback**: Report issues and suggest improvements
4. **Scale up**: Gradually increase the scope of your knowledge extraction
5. **Integrate**: Connect Metamorph with your proposal drafting systems

**Happy knowledge extraction!** 🚀

---

## 📝 Changelog

**v3.0.0** (2026-05-12):
- Initial release of Metamorph Website-to-Knowledge System
- Website crawling and file discovery features
- Automatic ingestion pipeline
- Knowledge graph storage with Neo4j
- Curation workflows and validation cards
- Six knowledge card types for proposal drafting

**v2.0.0** (2026-04-12):
- Previous version (manual document upload only)

---

## 📄 License

Metamorph is released under the [MIT License](LICENSE).

Copyright © 2026 UN and Humanitarian Organizations. All rights reserved.