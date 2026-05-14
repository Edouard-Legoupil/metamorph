# API Contracts: Metamorph Website-to-Knowledge System

**Version**: 3.0 | **Date**: 2026-05-12 | **Base Path**: `/api/v1`

This document defines the complete API contract for the Metamorph system, including all endpoints, request/response schemas, authentication requirements, and error handling.

---

## 🔐 Authentication

### JWT Authentication

**All endpoints** require JWT authentication unless specified as public.

**Authentication Header**:
```http
Authorization: Bearer {jwt_token}
```

**Token Acquisition**:
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**Successful Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "def50200...",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "curator",
    "review_tier": "tier_2"
  }
}
```

**Token Refresh**:
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "def50200..."
}
```

---

## 🌐 Website Management

### Create Website

**Endpoint**: `POST /api/v1/websites`

**Description**: Create a new website for scraping

**Request Body**:
```json
{
  "url": "https://unhcr.org",
  "scrape_frequency": "manual",
  "title": "UNHCR - The UN Refugee Agency",
  "description": "Official website of the UN Refugee Agency",
  "tags": ["humanitarian", "united_nations"]
}
```

**Response (201 Created)**:
```json
{
  "id": "website_abc123",
  "url": "https://unhcr.org",
  "domain": "unhcr.org",
  "title": "UNHCR - The UN Refugee Agency",
  "description": "Official website of the UN Refugee Agency",
  "scrape_frequency": "manual",
  "status": "active",
  "discovered_at": "2026-05-12T10:00:00Z",
  "last_scraped_at": null,
  "total_files_discovered": 0,
  "total_files_ingested": 0,
  "created_at": "2026-05-12T10:00:00Z",
  "created_by": "user_123",
  "tags": ["humanitarian", "united_nations"]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid URL format
- `409 Conflict`: Website already exists
- `401 Unauthorized`: Authentication required

---

### List Websites

**Endpoint**: `GET /api/v1/websites`

**Description**: List all websites with pagination and filtering

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `status`: Filter by status (active, paused, error)
- `search`: Search by URL, title, or description
- `sort`: Sort field (created_at, last_scraped_at, total_files)
- `order`: Sort order (asc, desc)

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "website_abc123",
      "url": "https://unhcr.org",
      "domain": "unhcr.org",
      "title": "UNHCR - The UN Refugee Agency",
      "status": "active",
      "scrape_frequency": "manual",
      "total_files_discovered": 42,
      "total_files_ingested": 15,
      "last_scraped_at": "2026-05-11T08:30:00Z",
      "created_at": "2026-05-10T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "has_more": false
}
```

---

### Get Website Details

**Endpoint**: `GET /api/v1/websites/{website_id}`

**Description**: Get detailed information about a specific website

**Response (200 OK)**:
```json
{
  "id": "website_abc123",
  "url": "https://unhcr.org",
  "domain": "unhcr.org",
  "title": "UNHCR - The UN Refugee Agency",
  "description": "Official website of the UN Refugee Agency",
  "scrape_frequency": "manual",
  "status": "active",
  "robots_txt_url": "https://unhcr.org/robots.txt",
  "sitemap_url": "https://unhcr.org/sitemap.xml",
  "discovered_at": "2026-05-10T10:00:00Z",
  "last_scraped_at": "2026-05-11T08:30:00Z",
  "last_successful_scrape": "2026-05-11T08:30:00Z",
  "total_files_discovered": 42,
  "total_files_ingested": 15,
  "error_message": null,
  "created_at": "2026-05-10T10:00:00Z",
  "created_by": "user_123",
  "updated_at": "2026-05-11T08:30:00Z",
  "updated_by": "system",
  "tags": ["humanitarian", "united_nations"]
}
```

**Error Responses**:
- `404 Not Found`: Website not found
- `401 Unauthorized`: Authentication required

---

### Update Website

**Endpoint**: `PATCH /api/v1/websites/{website_id}`

**Description**: Update website properties

**Request Body**:
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "scrape_frequency": "weekly",
  "status": "paused"
}
```

**Response (200 OK)**:
```json
{
  "id": "website_abc123",
  "url": "https://unhcr.org",
  "title": "Updated Title",
  "description": "Updated description",
  "scrape_frequency": "weekly",
  "status": "paused",
  "updated_at": "2026-05-12T11:00:00Z",
  "updated_by": "user_123"
}
```

---

### Delete Website

**Endpoint**: `DELETE /api/v1/websites/{website_id}`

**Description**: Delete a website and all associated data

**Query Parameters**:
- `force`: Boolean (default: false) - force delete even if has data

**Response (204 No Content)**: Empty response

**Error Responses**:
- `409 Conflict`: Website has associated data (use force=true to override)
- `404 Not Found`: Website not found

---

### Start Website Scraping

**Endpoint**: `POST /api/v1/websites/{website_id}/scrape`

**Description**: Initiate website crawling process

**Request Body**:
```json
{
  "max_depth": 3,
  "respect_robots_txt": true,
  "include_subdomains": false,
  "user_agent": "Metamorph/3.0 (+https://metamorph.example.com)",
  "custom_headers": {
    "Accept-Language": "en-US"
  }
}
```

**Response (202 Accepted)**:
```json
{
  "scrape_session_id": "session_xyz789",
  "website_id": "website_abc123",
  "status": "queued",
  "queued_at": "2026-05-12T11:15:00Z",
  "estimated_completion": "2026-05-12T11:20:00Z"
}
```

---

## 📁 File Discovery & Management

### List Discovered Files

**Endpoint**: `GET /api/v1/websites/{website_id}/files`

**Description**: List all files discovered from a website

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50, max: 200)
- `status`: Filter by status (pending, selected, processing, ingested, error)
- `file_type`: Filter by file type (pdf, docx, xlsx, pptx, html, txt)
- `search`: Search by filename or URL
- `sort`: Sort field (discovered_at, file_size, last_modified)
- `order`: Sort order (asc, desc)
- `min_size`: Minimum file size in bytes
- `max_size`: Maximum file size in bytes
- `since`: Only files discovered since date (ISO 8601)
- `until`: Only files discovered until date (ISO 8601)

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "file_def456",
      "website_id": "website_abc123",
      "url": "https://unhcr.org/document.pdf",
      "file_type": "pdf",
      "file_name": "document.pdf",
      "file_size": 1234567,
      "last_modified_date": "2026-05-10T09:00:00Z",
      "discovered_at": "2026-05-11T08:35:00Z",
      "status": "pending",
      "preview_text": "This document contains important information about...",
      "metadata": {
        "author": "UNHCR",
        "title": "Annual Report 2025",
        "page_count": 42
      }
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 50,
  "has_more": false
}
```

---

### Get File Details

**Endpoint**: `GET /api/v1/files/{file_id}`

**Description**: Get detailed information about a discovered file

**Response (200 OK)**:
```json
{
  "id": "file_def456",
  "website_id": "website_abc123",
  "url": "https://unhcr.org/document.pdf",
  "file_type": "pdf",
  "file_name": "document.pdf",
  "file_size": 1234567,
  "content_hash": "a1b2c3d4e5f6...",
  "last_modified_date": "2026-05-10T09:00:00Z",
  "discovered_at": "2026-05-11T08:35:00Z",
  "status": "pending",
  "error_message": null,
  "preview_text": "This document contains important information about refugee situations...",
  "metadata": {
    "author": "UNHCR",
    "title": "Annual Report 2025",
    "subject": "Humanitarian Aid",
    "keywords": ["refugees", "displacement", "humanitarian", "2025"],
    "page_count": 42,
    "language": "en"
  },
  "selected_at": null,
  "processed_at": null,
  "created_at": "2026-05-11T08:35:00Z"
}
```

---

### Get File Preview

**Endpoint**: `GET /api/v1/files/{file_id}/preview`

**Description**: Get extended preview of file content

**Query Parameters**:
- `length`: Number of characters to return (default: 2000, max: 10000)
- `format`: Format (text, html, markdown)

**Response (200 OK)**:
```json
{
  "file_id": "file_def456",
  "preview": "This document contains important information about refugee situations... [truncated after 2000 characters]",
  "format": "text",
  "truncated": true,
  "character_count": 2000,
  "total_characters": 45678
}
```

---

### Select Files for Ingestion

**Endpoint**: `POST /api/v1/websites/{website_id}/files/select`

**Description**: Select multiple files for ingestion

**Request Body**:
```json
{
  "file_ids": ["file_def456", "file_ghi789", "file_jkl012"],
  "notify_email": "user@example.com",
  "priority": "normal"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "selected_count": 3,
  "total_files": 42,
  "ingestion_queue_position": 1,
  "estimated_start_time": "2026-05-12T11:30:00Z"
}
```

---

### Deselect Files

**Endpoint**: `POST /api/v1/websites/{website_id}/files/deselect`

**Description**: Deselect files that were previously selected

**Request Body**:
```json
{
  "file_ids": ["file_def456", "file_ghi789"]
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "deselected_count": 2,
  "remaining_selected": 1
}
```

---

### Start File Ingestion

**Endpoint**: `POST /api/v1/websites/{website_id}/ingest`

**Description**: Start the ingestion process for selected files

**Request Body**:
```json
{
  "notify_email": "user@example.com",
  "priority": "high",
  "batch_size": 5,
  "parser_preference": "docling"
}
```

**Response (202 Accepted)**:
```json
{
  "ingestion_session_id": "ingest_abc123",
  "website_id": "website_abc123",
  "files_to_process": 15,
  "status": "queued",
  "queued_at": "2026-05-12T11:45:00Z",
  "estimated_completion": "2026-05-12T12:30:00Z"
}
```

---

### Get Ingestion Status

**Endpoint**: `GET /api/v1/websites/{website_id}/ingest-status`

**Description**: Get current ingestion status and progress

**Response (200 OK)**:
```json
{
  "ingestion_session_id": "ingest_abc123",
  "website_id": "website_abc123",
  "status": "processing",
  "started_at": "2026-05-12T11:45:00Z",
  "total_files": 15,
  "files_processed": 8,
  "files_successful": 7,
  "files_failed": 1,
  "files_remaining": 7,
  "progress_percentage": 53.33,
  "estimated_completion": "2026-05-12T12:15:00Z",
  "current_file": {
    "file_id": "file_mno345",
    "file_name": "report.pdf",
    "status": "processing",
    "started_at": "2026-05-12T11:58:00Z"
  },
  "error_count": 1,
  "warning_count": 2
}
```

---

### List Ingestion Jobs

**Endpoint**: `GET /api/v1/ingestion/jobs`

**Description**: List all ingestion jobs with filtering

**Query Parameters**:
- `website_id`: Filter by website ID
- `status`: Filter by status (queued, processing, completed, failed)
- `since`: Jobs started since date
- `until`: Jobs started until date
- `page`: Page number
- `page_size`: Items per page

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "job_xyz123",
      "discovered_file_id": "file_def456",
      "website_id": "website_abc123",
      "status": "completed",
      "started_at": "2026-05-12T11:46:00Z",
      "completed_at": "2026-05-12T11:48:00Z",
      "retry_count": 0,
      "document_id": "doc_abc123",
      "parser_used": "docling",
      "parse_success": true,
      "error_message": null
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

---

### Get Ingestion Job Details

**Endpoint**: `GET /api/v1/ingestion/jobs/{job_id}`

**Description**: Get detailed information about an ingestion job

**Response (200 OK)**:
```json
{
  "id": "job_xyz123",
  "discovered_file_id": "file_def456",
  "scrape_session_id": "session_xyz789",
  "website_id": "website_abc123",
  "status": "completed",
  "started_at": "2026-05-12T11:46:00Z",
  "completed_at": "2026-05-12T11:48:00Z",
  "retry_count": 0,
  "document_id": "doc_abc123",
  "parser_used": "docling",
  "parse_success": true,
  "parse_error": null,
  "extraction_metadata": {
    "pages_processed": 42,
    "entities_extracted": 15,
    "triplets_created": 28,
    "processing_time_seconds": 118
  },
  "error_message": null,
  "created_at": "2026-05-12T11:46:00Z",
  "updated_at": "2026-05-12T11:48:00Z"
}
```

---

### Retry Failed Ingestion Job

**Endpoint**: `POST /api/v1/ingestion/jobs/{job_id}/retry`

**Description**: Retry a failed ingestion job

**Request Body**:
```json
{
  "parser_override": "mineru",
  "priority": "high"
}
```

**Response (202 Accepted)**:
```json
{
  "success": true,
  "job_id": "job_xyz123",
  "new_status": "queued",
  "retry_count": 1,
  "estimated_start_time": "2026-05-12T12:00:00Z"
}
```

---

## 📚 Knowledge Cards

### List Knowledge Cards

**Endpoint**: `GET /api/v1/cards`

**Description**: List all knowledge cards with filtering

**Query Parameters**:
- `card_type`: Filter by card type (KC-1, KC-2, KC-3, KC-4, KC-5, KC-6)
- `domain`: Filter by domain (geographic, crisis, demographics, programming, policy, finance, hr, knowledge_assets)
- `status`: Filter by status (draft, approved, expired, rejected, under_review)
- `validity`: Filter by validity (valid, expired, expiring_soon)
- `search`: Search by title, content, or entities
- `source_website`: Filter by source website ID
- `created_by`: Filter by creator
- `page`: Page number
- `page_size`: Items per page
- `sort`: Sort field
- `order`: Sort order

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "card_kc1_001",
      "card_type": "KC-1",
      "title": "Donor Intelligence: European Union",
      "domain": "finance",
      "status": "approved",
      "validity_period": {
        "start": "2026-01-01T00:00:00Z",
        "end": "2026-12-31T23:59:59Z"
      },
      "created_at": "2026-05-10T14:00:00Z",
      "created_by": "user_123",
      "approved_at": "2026-05-11T09:30:00Z",
      "approved_by": "user_456",
      "source_websites": ["website_abc123"],
      "source_documents": 5,
      "source_entities": 3
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

---

### Get Knowledge Card Details

**Endpoint**: `GET /api/v1/cards/{card_id}`

**Description**: Get detailed information about a knowledge card

**Response (200 OK)**:
```json
{
  "id": "card_kc1_001",
  "card_type": "KC-1",
  "title": "Donor Intelligence: European Union",
  "description": "Comprehensive intelligence on EU funding priorities and requirements for 2026",
  "domain": "finance",
  "status": "approved",
  "validity_period": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-12-31T23:59:59Z"
  },
  "created_at": "2026-05-10T14:00:00Z",
  "created_by": "user_123",
  "updated_at": "2026-05-11T09:30:00Z",
  "updated_by": "user_456",
  "approved_at": "2026-05-11T09:30:00Z",
  "approved_by": "user_456",
  "source_websites": [
    {
      "id": "website_abc123",
      "url": "https://ec.europa.eu",
      "title": "European Commission"
    }
  ],
  "source_documents": [
    {
      "id": "doc_xyz789",
      "file_name": "EU_Funding_Guidelines_2026.pdf",
      "url": "https://ec.europa.eu/funding/guidelines.pdf"
    }
  ],
  "source_entities": [
    {
      "id": "entity_eu_commission",
      "name": "European Commission",
      "entity_type": "organization"
    }
  ],
  "blocks_count": 8,
  "verification_state": "accepted",
  "confidence_score": 0.95
}
```

---

### Create Knowledge Card

**Endpoint**: `POST /api/v1/cards`

**Description**: Create a new knowledge card

**Request Body**:
```json
{
  "card_type": "KC-1",
  "title": "Donor Intelligence: New Donor",
  "domain": "finance",
  "validity_period": {
    "start": "2026-06-01T00:00:00Z",
    "end": "2027-05-31T23:59:59Z"
  },
  "source_website_ids": ["website_abc123"],
  "source_document_ids": ["doc_xyz789"],
  "source_entity_ids": ["entity_donor_org"],
  "tags": ["new_donor", "priority_high"]
}
```

**Response (201 Created)**:
```json
{
  "id": "card_kc1_042",
  "card_type": "KC-1",
  "title": "Donor Intelligence: New Donor",
  "domain": "finance",
  "status": "draft",
  "validity_period": {
    "start": "2026-06-01T00:00:00Z",
    "end": "2027-05-31T23:59:59Z"
  },
  "created_at": "2026-05-12T13:00:00Z",
  "created_by": "user_123",
  "source_websites": 1,
  "source_documents": 1,
  "source_entities": 1,
  "blocks": []
}
```

---

### Update Knowledge Card

**Endpoint**: `PATCH /api/v1/cards/{card_id}`

**Description**: Update knowledge card properties

**Request Body**:
```json
{
  "title": "Updated Donor Intelligence: European Union",
  "status": "under_review",
  "validity_period": {
    "end": "2027-06-30T23:59:59Z"
  },
  "expiry_reason": "Extended validity due to ongoing funding cycle"
}
```

**Response (200 OK)**:
```json
{
  "id": "card_kc1_001",
  "title": "Updated Donor Intelligence: European Union",
  "status": "under_review",
  "validity_period": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2027-06-30T23:59:59Z"
  },
  "updated_at": "2026-05-12T13:15:00Z",
  "updated_by": "user_123"
}
```

---

### Approve Knowledge Card

**Endpoint**: `POST /api/v1/cards/{card_id}/approve`

**Description**: Approve a knowledge card for use in proposals

**Request Body**:
```json
{
  "validity_period": {
    "start": "2026-05-12T00:00:00Z",
    "end": "2027-05-11T23:59:59Z"
  },
  "approval_notes": "Verified all source information and cross-referenced with official documents"
}
```

**Response (200 OK)**:
```json
{
  "id": "card_kc1_001",
  "status": "approved",
  "approved_at": "2026-05-12T13:30:00Z",
  "approved_by": "user_123",
  "validity_period": {
    "start": "2026-05-12T00:00:00Z",
    "end": "2027-05-11T23:59:59Z"
  }
}
```

---

### Reject Knowledge Card

**Endpoint**: `POST /api/v1/cards/{card_id}/reject`

**Description**: Reject a knowledge card

**Request Body**:
```json
{
  "rejection_reason": "Source information is outdated and contradicts official statistics",
  "suggested_actions": ["Update with current data", "Contact source for verification"]
}
```

**Response (200 OK)**:
```json
{
  "id": "card_kc1_001",
  "status": "rejected",
  "rejected_at": "2026-05-12T13:45:00Z",
  "rejected_by": "user_123",
  "rejection_reason": "Source information is outdated and contradicts official statistics"
}
```

---

## 📝 Wiki Blocks

### List Wiki Blocks

**Endpoint**: `GET /api/v1/cards/{card_id}/blocks`

**Description**: List all wiki blocks in a knowledge card

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "block_intro_001",
      "section_name": "Introduction",
      "word_limit": 200,
      "block_type": "text",
      "verification_state": "accepted",
      "created_at": "2026-05-11T10:00:00Z",
      "updated_at": "2026-05-11T10:15:00Z"
    }
  ],
  "total": 8
}
```

---

### Get Wiki Block Details

**Endpoint**: `GET /api/v1/cards/{card_id}/blocks/{block_id}`

**Description**: Get detailed information about a wiki block

**Response (200 OK)**:
```json
{
  "id": "block_intro_001",
  "card_id": "card_kc1_001",
  "section_name": "Introduction",
  "content": "The European Union remains a key donor for humanitarian operations...",
  "word_limit": 200,
  "block_type": "text",
  "template_query": "SUMMARIZE_DONOR_PRIORITIES",
  "verification_state": "accepted",
  "provenance": {
    "source_website_id": "website_abc123",
    "source_website_url": "https://ec.europa.eu",
    "source_file_id": "file_def456",
    "source_file_url": "https://ec.europa.eu/funding/strategy.pdf",
    "source_document_id": "doc_xyz789",
    "extraction_date": "2026-05-10T14:30:00Z",
    "extraction_tool": "docling",
    "curator_id": "user_456",
    "curation_date": "2026-05-11T10:15:00Z",
    "validation_state": "accepted",
    "validation_date": "2026-05-11T10:15:00Z",
    "validator_id": "user_456"
  },
  "maintenance_tags": [],
  "discussion_thread_id": null,
  "created_at": "2026-05-11T10:00:00Z",
  "created_by": "system",
  "updated_at": "2026-05-11T10:15:00Z",
  "updated_by": "user_456"
}
```

---

### Update Wiki Block

**Endpoint**: `PATCH /api/v1/cards/{card_id}/blocks/{block_id}`

**Description**: Update wiki block content and properties

**Request Body**:
```json
{
  "content": "Updated introduction with verified statistics from Q2 2026 report...",
  "verification_state": "accepted",
  "maintenance_tags": ["verified", "q2_2026_update"]
}
```

**Response (200 OK)**:
```json
{
  "id": "block_intro_001",
  "content": "Updated introduction with verified statistics from Q2 2026 report...",
  "verification_state": "accepted",
  "maintenance_tags": ["verified", "q2_2026_update"],
  "updated_at": "2026-05-12T14:00:00Z",
  "updated_by": "user_123"
}
```

---

### Verify Wiki Block

**Endpoint**: `POST /api/v1/cards/{card_id}/blocks/{block_id}/verify`

**Description**: Mark a wiki block as verified

**Request Body**:
```json
{
  "verification_state": "accepted",
  "verification_notes": "Cross-referenced with three independent sources",
  "confidence_score": 0.98
}
```

**Response (200 OK)**:
```json
{
  "id": "block_intro_001",
  "verification_state": "accepted",
  "verified_at": "2026-05-12T14:15:00Z",
  "verified_by": "user_123",
  "confidence_score": 0.98
}
```

---

### Flag Wiki Block

**Endpoint**: `POST /api/v1/cards/{card_id}/blocks/{block_id}/flag`

**Description**: Flag a wiki block for review

**Request Body**:
```json
{
  "verification_state": "disputed",
  "flag_reason": "Statistics conflict with official UNHCR report Q1 2026",
  "suggested_action": "Review source document and cross-reference",
  "maintenance_tags": ["citation_needed", "data_conflict"]
}
```

**Response (200 OK)**:
```json
{
  "id": "block_intro_001",
  "verification_state": "disputed",
  "flagged_at": "2026-05-12T14:30:00Z",
  "flagged_by": "user_789",
  "maintenance_tags": ["citation_needed", "data_conflict"]
}
```

---

## ✅ Validation Cards

### List Validation Cards

**Endpoint**: `GET /api/v1/validation/cards`

**Description**: List validation cards requiring review

**Query Parameters**:
- `status`: Filter by status (open, under_review, approved, rejected, merged, escalated, no_consensus)
- `assigned_tier`: Filter by review tier (tier_1, tier_2, tier_3)
- `sensitivity`: Filter by sensitivity (low, medium, high)
- `target_type`: Filter by target type (entity, block, card, triplet)
- `contradiction_type`: Filter by contradiction type
- `assigned_to`: Filter by assignee
- `page`: Page number
- `page_size`: Items per page

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "val_card_001",
      "target_type": "block",
      "target_id": "block_intro_001",
      "card_id": "card_kc1_001",
      "status": "open",
      "sensitivity": "medium",
      "assigned_tier": "tier_2",
      "confidence_score": 0.65,
      "created_at": "2026-05-12T14:30:00Z",
      "contradiction_type": "factual"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

---

### Get Validation Card Details

**Endpoint**: `GET /api/v1/validation/cards/{card_id}`

**Description**: Get detailed validation card information

**Response (200 OK)**:
```json
{
  "id": "val_card_001",
  "target_type": "block",
  "target_id": "block_intro_001",
  "card_id": "card_kc1_001",
  "current_value": "The European Union provided $1.2B in humanitarian aid in 2025.",
  "proposed_value": "The European Union provided $1.5B in humanitarian aid in 2025.",
  "diff": "- $1.2B in humanitarian aid in 2025.
+ $1.5B in humanitarian aid in 2025.",
  "evidence": [
    "https://ec.europa.eu/funding/report.pdf (page 42)",
    "https://reliefweb.int/report/world/2025-funding-review"
  ],
  "provenance": {
    "source_website_id": "website_abc123",
    "source_website_url": "https://ec.europa.eu",
    "source_file_id": "file_new789",
    "source_file_url": "https://ec.europa.eu/funding/2025-review.pdf",
    "extraction_date": "2026-05-12T14:00:00Z",
    "extraction_tool": "docling"
  },
  "confidence_score": 0.65,
  "sensitivity": "medium",
  "source_reliability": "trusted",
  "contradiction_type": "factual",
  "status": "open",
  "created_at": "2026-05-12T14:30:00Z",
  "created_by": "system",
  "assigned_to": null,
  "assigned_tier": "tier_2"
}
```

---

### Assign Validation Card

**Endpoint**: `POST /api/v1/validation/cards/{card_id}/assign`

**Description**: Assign a validation card to a reviewer

**Request Body**:
```json
{
  "assigned_to": "user_456",
  "assigned_tier": "tier_2",
  "priority": "high",
  "due_date": "2026-05-15T00:00:00Z"
}
```

**Response (200 OK)**:
```json
{
  "id": "val_card_001",
  "status": "under_review",
  "assigned_to": "user_456",
  "assigned_tier": "tier_2",
  "assigned_at": "2026-05-12T14:45:00Z",
  "assigned_by": "user_123",
  "due_date": "2026-05-15T00:00:00Z"
}
```

---

### Approve Validation Card

**Endpoint**: `POST /api/v1/validation/cards/{card_id}/approve`

**Description**: Approve a validation card

**Request Body**:
```json
{
  "resolution": "Approved after verifying with official EU financial report Q4 2025",
  "confidence_score": 0.92,
  "update_target": true,
  "notification_message": "Please update all references to this statistic"
}
```

**Response (200 OK)**:
```json
{
  "id": "val_card_001",
  "status": "approved",
  "resolved_at": "2026-05-12T15:00:00Z",
  "resolved_by": "user_456",
  "resolution": "Approved after verifying with official EU financial report Q4 2025",
  "target_updated": true
}
```

---

### Reject Validation Card

**Endpoint**: `POST /api/v1/validation/cards/{card_id}/reject`

**Description**: Reject a validation card

**Request Body**:
```json
{
  "resolution": "Rejected - proposed value lacks credible sourcing and contradicts multiple verified sources",
  "rejection_reason": "inadequate_evidence",
  "suggested_action": "Provide official EU documentation supporting the $1.5B figure"
}
```

**Response (200 OK)**:
```json
{
  "id": "val_card_001",
  "status": "rejected",
  "resolved_at": "2026-05-12T15:15:00Z",
  "resolved_by": "user_456",
  "resolution": "Rejected - proposed value lacks credible sourcing...",
  "rejection_reason": "inadequate_evidence"
}
```

---

### Merge Validation Card

**Endpoint**: `POST /api/v1/validation/cards/{card_id}/merge`

**Description**: Merge/Edit a validation card with custom resolution

**Request Body**:
```json
{
  "resolution": "merged",
  "merged_value": "The European Union provided $1.35B in humanitarian aid in 2025, according to consolidated reports.",
  "resolution_notes": "Compromise value based on average of multiple sources",
  "confidence_score": 0.88,
  "update_target": true,
  "new_evidence": [
    "https://ocha.un.org/consolidated-report-2025",
    "https://developmentinitiatives.org/european-funding-2025"
  ]
}
```

**Response (200 OK)**:
```json
{
  "id": "val_card_001",
  "status": "merged",
  "resolved_at": "2026-05-12T15:30:00Z",
  "resolved_by": "user_456",
  "resolution": "merged",
  "merged_value": "The European Union provided $1.35B in humanitarian aid in 2025...",
  "target_updated": true
}
```

---

### Escalate Validation Card

**Endpoint**: `POST /api/v1/validation/cards/{card_id}/escalate`

**Description**: Escalate a validation card to a higher review tier

**Request Body**:
```json
{
  "escalation_reason": "Conflict between high-confidence sources requires policy-level resolution",
  "escalate_to": "tier_3",
  "escalation_notes": "Tier 2 cannot resolve discrepancy between EU official figures and UN consolidated reports",
  "urgency": "high"
}
```

**Response (200 OK)**:
```json
{
  "id": "val_card_001",
  "status": "escalated",
  "escalated_at": "2026-05-12T15:45:00Z",
  "escalated_by": "user_456",
  "assigned_tier": "tier_3",
  "escalation_reason": "Conflict between high-confidence sources...",
  "previous_tier": "tier_2"
}
```

---

## 💬 Discussion Threads

### List Discussion Threads

**Endpoint**: `GET /api/v1/discussion/threads`

**Description**: List all discussion threads

**Query Parameters**:
- `status`: Filter by status (open, under_review, consensus_reached, no_consensus, rejected, escalated, resolved, archived)
- `linked_entity_id`: Filter by linked entity
- `linked_block_id`: Filter by linked block
- `linked_card_id`: Filter by linked card
- `created_by`: Filter by creator
- `watcher`: Filter by watcher
- `search`: Search by title or content
- `page`: Page number
- `page_size`: Items per page

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "thread_001",
      "title": "Discrepancy in refugee statistics",
      "topic": "Data Accuracy",
      "status": "under_review",
      "created_at": "2026-05-12T14:30:00Z",
      "created_by": "user_789",
      "updated_at": "2026-05-12T15:00:00Z",
      "comment_count": 5,
      "watcher_count": 3,
      "linked_entity_id": "entity_refugee_stats",
      "linked_block_id": "block_stats_001"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 20
}
```

---

### Create Discussion Thread

**Endpoint**: `POST /api/v1/discussion/threads`

**Description**: Create a new discussion thread

**Request Body**:
```json
{
  "title": "Conflict in funding allocation data",
  "topic": "Financial Data",
  "content": "The funding allocation figures in KC-1 card conflict with the source document...",
  "linked_entity_id": "entity_funding_2025",
  "linked_block_id": "block_allocation_001",
  "evidence_quality": "high",
  "policy_compliance": true,
  "mentions": ["user_456", "user_789"],
  "attachments": [
    {
      "url": "https://example.com/conflict-analysis.pdf",
      "title": "Funding Conflict Analysis"
    }
  ]
}
```

**Response (201 Created)**:
```json
{
  "id": "thread_002",
  "title": "Conflict in funding allocation data",
  "topic": "Financial Data",
  "status": "open",
  "created_at": "2026-05-12T16:00:00Z",
  "created_by": "user_123",
  "linked_entity_id": "entity_funding_2025",
  "linked_block_id": "block_allocation_001",
  "comment_count": 1,
  "watcher_count": 1
}
```

---

### Get Discussion Thread

**Endpoint**: `GET /api/v1/discussion/threads/{thread_id}`

**Description**: Get discussion thread details and comments

**Query Parameters**:
- `include_comments`: Boolean (default: true)
- `comment_page`: Page number for comments
- `comment_page_size`: Comments per page

**Response (200 OK)**:
```json
{
  "id": "thread_001",
  "title": "Discrepancy in refugee statistics",
  "topic": "Data Accuracy",
  "status": "under_review",
  "created_at": "2026-05-12T14:30:00Z",
  "created_by": {
    "id": "user_789",
    "name": "Jane Doe",
    "role": "Senior Curator"
  },
  "updated_at": "2026-05-12T15:45:00Z",
  "resolved_at": null,
  "resolved_by": null,
  "consensus_result": null,
  "linked_entity_id": "entity_refugee_stats",
  "linked_block_id": "block_stats_001",
  "linked_card_id": "card_kc2_001",
  "watchers": ["user_123", "user_456", "user_789"],
  "comment_count": 8,
  "comments": [
    {
      "id": "comment_001",
      "content": "I've identified a discrepancy between the refugee statistics...",
      "created_at": "2026-05-12T14:30:00Z",
      "created_by": "user_789",
      "is_edited": false,
      "evidence_quality": "high",
      "policy_compliance": true
    }
  ]
}
```

---

### Add Comment to Thread

**Endpoint**: `POST /api/v1/discussion/threads/{thread_id}/comments`

**Description**: Add a comment to a discussion thread

**Request Body**:
```json
{
  "content": "After reviewing the source documents, I can confirm the discrepancy...",
  "mentions": ["user_456"],
  "evidence_quality": "high",
  "policy_compliance": true,
  "attachments": [
    {
      "url": "https://unhcr.org/verification-report.pdf",
      "title": "UNHCR Verification Report Q2 2026"
    }
  ]
}
```

**Response (201 Created)**:
```json
{
  "id": "comment_002",
  "thread_id": "thread_001",
  "content": "After reviewing the source documents, I can confirm the discrepancy...",
  "created_at": "2026-05-12T16:15:00Z",
  "created_by": "user_123",
  "is_edited": false,
  "mentions": ["user_456"],
  "evidence_quality": "high",
  "policy_compliance": true,
  "attachments": [
    {
      "url": "https://unhcr.org/verification-report.pdf",
      "title": "UNHCR Verification Report Q2 2026"
    }
  ]
}
```

---

### Update Discussion Thread Status

**Endpoint**: `PATCH /api/v1/discussion/threads/{thread_id}`

**Description**: Update discussion thread status

**Request Body**:
```json
{
  "status": "consensus_reached",
  "consensus_result": "accept",
  "resolution_summary": "Consensus reached to accept the original values with added context"
}
```

**Response (200 OK)**:
```json
{
  "id": "thread_001",
  "status": "consensus_reached",
  "consensus_result": "accept",
  "resolved_at": "2026-05-12T16:30:00Z",
  "resolved_by": "user_456",
  "resolution_summary": "Consensus reached to accept the original values with added context"
}
```

---

### Watch Discussion Thread

**Endpoint**: `POST /api/v1/discussion/threads/{thread_id}/watch`

**Description**: Start watching a discussion thread

**Response (200 OK)**:
```json
{
  "success": true,
  "thread_id": "thread_001",
  "is_watching": true,
  "watcher_count": 4
}
```

---

### Unwatch Discussion Thread

**Endpoint**: `DELETE /api/v1/discussion/threads/{thread_id}/watch`

**Description**: Stop watching a discussion thread

**Response (200 OK)**:
```json
{
  "success": true,
  "thread_id": "thread_001",
  "is_watching": false,
  "watcher_count": 3
}
```

---

## 🔍 Search & Discovery

### Global Search

**Endpoint**: `GET /api/v1/search`

**Description**: Search across all knowledge entities

**Query Parameters**:
- `query`: Search query
- `types`: Filter by types (websites, files, documents, entities, cards, blocks)
- `domains`: Filter by knowledge domains
- `status`: Filter by status
- `since`: Only results since date
- `until`: Only results until date
- `page`: Page number
- `page_size`: Items per page

**Response (200 OK)**:
```json
{
  "results": [
    {
      "type": "knowledge_card",
      "id": "card_kc1_001",
      "title": "Donor Intelligence: European Union",
      "content_preview": "The European Union remains a key donor...",
      "score": 0.95,
      "matches": ["european union", "donor", "finance"]
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "suggestions": ["european commission", "eu funding", "humanitarian donors"]
}
```

---

### Advanced Search

**Endpoint**: `POST /api/v1/search/advanced`

**Description**: Advanced search with complex queries

**Request Body**:
```json
{
  "query": {
    "must": [
      {"term": "refugee"},
      {"range": {"date": {"gte": "2025-01-01", "lte": "2025-12-31"}}}
    ],
    "should": [
      {"term": "syria"},
      {"term": "ukraine"}
    ],
    "must_not": [
      {"term": "expired"}
    ]
  },
  "filters": {
    "domains": ["crisis", "geographic"],
    "card_types": ["KC-2", "KC-6"],
    "verification_states": ["accepted", "auto_accepted"]
  },
  "sort": [
    {"confidence_score": "desc"},
    {"updated_at": "desc"}
  ]
}
```

**Response (200 OK)**:
```json
{
  "results": [
    {
      "type": "entity",
      "id": "entity_syria_crisis",
      "name": "Syrian Refugee Crisis",
      "entity_type": "crisis",
      "score": 0.92,
      "confidence_score": 0.88,
      "source_documents": 5,
      "related_cards": 3
    }
  ],
  "total": 18,
  "aggregations": {
    "by_domain": {
      "crisis": 12,
      "geographic": 6
    },
    "by_type": {
      "entity": 10,
      "knowledge_card": 8
    }
  }
}
```

---

## 📊 Analytics & Reporting

### Get System Statistics

**Endpoint**: `GET /api/v1/analytics/system`

**Description**: Get system-wide statistics

**Query Parameters**:
- `period`: Time period (day, week, month, quarter, year)
- `since`: Custom start date
- `until`: Custom end date

**Response (200 OK)**:
```json
{
  "websites": {
    "total": 15,
    "active": 12,
    "paused": 2,
    "error": 1
  },
  "files": {
    "total_discovered": 1242,
    "total_ingested": 489,
    "by_type": {
      "pdf": 245,
      "docx": 123,
      "html": 89,
      "xlsx": 25,
      "pptx": 7
    }
  },
  "knowledge_cards": {
    "total": 187,
    "by_status": {
      "draft": 42,
      "approved": 125,
      "expired": 15,
      "rejected": 5
    },
    "by_type": {
      "KC-1": 32,
      "KC-2": 45,
      "KC-3": 28,
      "KC-4": 22,
      "KC-5": 18,
      "KC-6": 42
    }
  },
  "validation_cards": {
    "total": 28,
    "by_status": {
      "open": 8,
      "under_review": 12,
      "approved": 5,
      "rejected": 3
    }
  },
  "discussion_threads": {
    "total": 15,
    "by_status": {
      "open": 5,
      "resolved": 8,
      "archived": 2
    }
  },
  "period": "month"
}
```

---

### Get Website Analytics

**Endpoint**: `GET /api/v1/websites/{website_id}/analytics`

**Description**: Get analytics for a specific website

**Query Parameters**:
- `period`: Time period (default: month)
- `metric`: Specific metric to focus on

**Response (200 OK)**:
```json
{
  "website_id": "website_abc123",
  "url": "https://unhcr.org",
  "period": "month",
  "scrape_sessions": {
    "total": 4,
    "successful": 3,
    "failed": 1
  },
  "files_discovered": {
    "total": 142,
    "trend": "increasing",
    "change_percentage": 12.3
  },
  "files_ingested": {
    "total": 58,
    "success_rate": 92.5,
    "by_type": {
      "pdf": 32,
      "docx": 15,
      "html": 8,
      "xlsx": 3
    }
  },
  "knowledge_extracted": {
    "entities": 89,
    "events": 15,
    "triplets": 142,
    "cards_created": 12
  },
  "time_series": {
    "discovery": [
      {"date": "2026-05-01", "count": 35},
      {"date": "2026-05-08", "count": 42},
      {"date": "2026-05-15", "count": 38},
      {"date": "2026-05-22", "count": 27}
    ],
    "ingestion": [
      {"date": "2026-05-02", "count": 12},
      {"date": "2026-05-09", "count": 18},
      {"date": "2026-05-16", "count": 15},
      {"date": "2026-05-23", "count": 13}
    ]
  }
}
```

---

## 👥 User Management

### List Users

**Endpoint**: `GET /api/v1/users`

**Description**: List all users (Admin only)

**Query Parameters**:
- `role`: Filter by role
- `status`: Filter by status
- `search`: Search by name or email
- `page`: Page number
- `page_size`: Items per page

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "user_123",
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "role": "curator",
      "review_tier": "tier_2",
      "status": "active",
      "last_login": "2026-05-12T09:30:00Z",
      "created_at": "2026-01-15T10:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20
}
```

---

### Get User Profile

**Endpoint**: `GET /api/v1/users/me`

**Description**: Get current user's profile

**Response (200 OK)**:
```json
{
  "id": "user_123",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "role": "curator",
  "review_tier": "tier_2",
  "status": "active",
  "permissions": [
    "website:create",
    "website:read",
    "file:select",
    "card:curate",
    "validation:review_tier_2"
  ],
  "last_login": "2026-05-12T09:30:00Z",
  "created_at": "2026-01-15T10:00:00Z",
  "preferences": {
    "theme": "light",
    "language": "en",
    "notifications": {
      "email": true,
      "push": true
    }
  }
}
```

---

### Update User Profile

**Endpoint**: `PATCH /api/v1/users/me`

**Description**: Update current user's profile

**Request Body**:
```json
{
  "full_name": "John H. Doe",
  "preferences": {
    "theme": "dark",
    "notifications": {
      "email": false
    }
  }
}
```

**Response (200 OK)**:
```json
{
  "id": "user_123",
  "full_name": "John H. Doe",
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications": {
      "email": false,
      "push": true
    }
  },
  "updated_at": "2026-05-12T17:00:00Z"
}
```

---

## ⚙️ System Management

### Health Check

**Endpoint**: `GET /api/v1/health`

**Description**: Check system health status (Public endpoint)

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-12T17:15:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "response_time_ms": 42
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 8
    },
    "storage": {
      "status": "healthy",
      "used_space_gb": 45,
      "total_space_gb": 200
    }
  },
  "version": "3.0.0",
  "environment": "production",
  "uptime_seconds": 86400
}
```

---

### Get System Info

**Endpoint**: `GET /api/v1/system/info`

**Description**: Get system information (Admin only)

**Response (200 OK)**:
```json
{
  "version": "3.0.0",
  "build_date": "2026-05-01T10:00:00Z",
  "environment": "production",
  "api_version": "v1",
  "dependencies": {
    "neo4j": "5.13.0",
    "fastapi": "0.104.0",
    "python": "3.11.4"
  },
  "features": {
    "website_crawling": true,
    "file_discovery": true,
    "automatic_ingestion": true,
    "knowledge_cards": true,
    "curation_workflows": true,
    "validation_cards": true,
    "discussion_threads": true,
    "proposal_drafting": true
  }
}
```

---

## 📝 Error Handling

### Standard Error Responses

**400 Bad Request**:
```json
{
  "error": "bad_request",
  "message": "Invalid request parameters",
  "details": {
    "field": "url",
    "issue": "must be a valid URL"
  },
  "timestamp": "2026-05-12T17:30:00Z",
  "request_id": "req_abc123"
}
```

**401 Unauthorized**:
```json
{
  "error": "unauthorized",
  "message": "Authentication required",
  "details": "No valid API key or JWT token provided",
  "timestamp": "2026-05-12T17:30:00Z",
  "request_id": "req_abc123"
}
```

**403 Forbidden**:
```json
{
  "error": "forbidden",
  "message": "Insufficient permissions",
  "details": "User does not have 'website:create' permission",
  "timestamp": "2026-05-12T17:30:00Z",
  "request_id": "req_abc123"
}
```

**404 Not Found**:
```json
{
  "error": "not_found",
  "message": "Resource not found",
  "details": {
    "resource": "website",
    "id": "website_xyz999"
  },
  "timestamp": "2026-05-12T17:30:00Z",
  "request_id": "req_abc123"
}
```

**409 Conflict**:
```json
{
  "error": "conflict",
  "message": "Resource conflict",
  "details": "Website with this URL already exists",
  "timestamp": "2026-05-12T17:30:00Z",
  "request_id": "req_abc123"
}
```

**429 Too Many Requests**:
```json
{
  "error": "rate_limit_exceeded",
  "message": "API rate limit exceeded",
  "details": {
    "limit": 100,
    "remaining": 0,
    "reset_in_seconds": 30
  },
  "timestamp": "2026-05-12T17:30:00Z",
  "request_id": "req_abc123"
}
```

**500 Internal Server Error**:
```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred",
  "details": "Error ID: err_xyz789",
  "timestamp": "2026-05-12T17:30:00Z",
  "request_id": "req_abc123"
}
```

---

## 🔄 Webhooks

### Webhook Events

**Endpoint**: `POST /api/v1/webhooks`

**Description**: Receive webhook notifications for system events

**Supported Events**:
- `website.scrape.completed`
- `website.scrape.failed`
- `ingestion.completed`
- `ingestion.failed`
- `card.approved`
- `card.expired`
- `validation.created`
- `validation.resolved`
- `discussion.created`
- `discussion.resolved`

**Webhook Payload Example**:
```json
{
  "event": "website.scrape.completed",
  "timestamp": "2026-05-12T18:00:00Z",
  "data": {
    "website_id": "website_abc123",
    "scrape_session_id": "session_xyz789",
    "files_discovered": 42,
    "files_new": 15,
    "files_updated": 5,
    "duration_seconds": 345,
    "status": "completed"
  },
  "webhook_id": "wh_abc123",
  "attempt": 1
}
```

**Webhook Registration**:
```json
{
  "url": "https://your-server.com/webhooks/metamorph",
  "events": ["website.scrape.completed", "ingestion.failed"],
  "secret": "your_webhook_secret",
  "active": true
}
```

---

## 📊 API Usage & Rate Limiting

### Rate Limits

- **Authenticated Users**: 100 requests per minute
- **Unauthenticated Users**: 10 requests per minute
- **Admin Users**: 500 requests per minute

**Rate Limit Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 30
```

### API Usage Analytics

**Endpoint**: `GET /api/v1/analytics/api-usage`

**Description**: Get API usage statistics (Admin only)

**Response (200 OK)**:
```json
{
  "period": "month",
  "total_requests": 4285,
  "by_endpoint": {
    "/api/v1/websites": 850,
    "/api/v1/files": 1240,
    "/api/v1/cards": 1020,
    "/api/v1/validation/cards": 380
  },
  "by_user": {
    "user_123": 842,
    "user_456": 1250,
    "system": 189
  },
  "by_status": {
    "200": 3892,
    "201": 145,
    "400": 89,
    "401": 42,
    "404": 117
  },
  "time_series": [
    {"date": "2026-05-01", "requests": 145},
    {"date": "2026-05-02", "requests": 189}
  ]
}
```

---

## 🔒 Security

### Security Headers

All responses include security headers:
```http
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.example.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https://*.example.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://api.example.com; frame-src 'none'; object-src 'none'
Referrer-Policy: strict-origin-when-cross-origin
```

### CORS Configuration

```http
Access-Control-Allow-Origin: https://metamorph.example.com
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type, Accept, X-Requested-With
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
```

---

## 📄 Changelog

### API Version History

**v1.0** (2026-01-15):
- Initial API release
- Website management endpoints
- Basic file discovery

**v1.1** (2026-02-20):
- Added ingestion endpoints
- Knowledge card management
- Basic curation workflows

**v1.2** (2026-03-10):
- Validation card system
- Discussion threads
- Advanced search

**v1.3** (2026-04-05):
- Analytics endpoints
- Webhook support
- Rate limiting

**v2.0** (2026-05-12):
- Website crawling endpoints
- File selection workflows
- Automatic ingestion triggers
- Complete curation system

---

## 🎯 Best Practices

### API Usage

1. **Use pagination**: Always specify page and page_size parameters
2. **Cache responses**: Cache GET responses where appropriate
3. **Handle errors gracefully**: Implement proper error handling
4. **Use webhooks**: For real-time notifications of important events
5. **Monitor rate limits**: Respect rate limits and implement backoff

### Authentication

1. **Secure token storage**: Never store tokens in client-side code
2. **Short-lived tokens**: Use refresh tokens for long-lived sessions
3. **HTTPS only**: Always use HTTPS for API communication
4. **Rotate secrets**: Regularly rotate API keys and secrets
5. **Scope permissions**: Use least-privilege principle for user roles

### Performance

1. **Batch operations**: Use bulk endpoints where available
2. **Filter early**: Apply filters at query time, not client-side
3. **Selective fields**: Request only needed fields
4. **Compress payloads**: Use gzip compression for large requests
5. **Connection pooling**: Reuse HTTP connections

---

## 📚 API Documentation

- **Interactive Docs**: [Swagger UI](http://localhost:8000/docs)
- **Redoc**: [ReDoc](http://localhost:8000/redoc)
- **OpenAPI Spec**: [JSON](http://localhost:8000/openapi.json)
- **Postman Collection**: [Download](http://localhost:8000/postman.json)

---

## 🆘 Support

For API-related issues:
- **GitHub Issues**: [https://github.com/your-org/metamorph/issues](https://github.com/your-org/metamorph/issues)
- **API Support Email**: api-support@metamorph.example.com
- **Status Page**: [https://status.metamorph.example.com](https://status.metamorph.example.com)

---

## 📄 License

The Metamorph API is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Copyright © 2026 UN and Humanitarian Organizations. All rights reserved.