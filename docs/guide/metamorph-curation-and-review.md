# Metamorph Curation & Review

## 1. Curation Overview

Metamorph empowers curators, reviewers, analysts, and trusted contributors to keep knowledge clean, current, and trustworthy.

The system combines:

- curated wiki blocks
- claim-level validation
- discussion-driven review
- conflict queues
- provenance-aware evidence handling
- consensus workflows
- revision history
- audit logging
- human and agentic retroaction loops

Metamorph follows a Wikipedia-inspired operating model:

> The visible wiki is the curated consensus layer.  
> The discussion layer is where conflicting, uncertain, or proposed information is evaluated.  
> The audit and revision layer is the immutable record of how knowledge changed over time.

For every topic, entity, claim, or wiki block, Metamorph separates:

```text
Curated Knowledge
    what users currently see as accepted

Discussion / Review
    where disputed or proposed knowledge is debated and validated

Revision History
    what changed, when, by whom, and why

Canonical Graph / Claim Store
    the trusted machine-readable knowledge state
```

This ensures that the application does not treat incoming information as truth immediately. Instead, new information is routed through policy, confidence, provenance, review, and consensus mechanisms before it becomes part of the trusted knowledge base.

---

## 2. Core Knowledge Surfaces

### 2.1 Curated Wiki Surface

The curated wiki surface is the reader-facing knowledge layer.

It contains the currently accepted version of a topic, entity, field, paragraph, claim, or analytical block.

This surface is equivalent to Wikipedia’s **Article** tab.

It should display only information that is:

- accepted
- sufficiently sourced
- current
- relevant
- policy-compliant
- traceable to provenance
- not actively disputed, unless clearly marked

Each wiki block may contain:

```pseudo
WikiBlock {
  id
  topic_id
  entity_id?
  claim_ids[]
  current_revision_id
  content
  citations[]
  provenance[]
  verification_state
  freshness_state
  dispute_state
  maintenance_tags[]
  linked_discussion_threads[]
}
```

The curated wiki surface should not expose every extracted or incoming claim as accepted knowledge. Instead, it should expose the best current representation of the knowledge base.

---

### 2.2 Discussion and Review Surface

The discussion and review surface is where contested, uncertain, sensitive, or low-confidence information is evaluated before it becomes accepted knowledge.

This surface is equivalent to Wikipedia’s **Discussion / Talk** tab.

It is used to discuss:

- conflicting claims
- proposed edits
- source reliability
- evidence quality
- outdated information
- unclear provenance
- disputed interpretations
- competing operational definitions
- policy-sensitive changes
- regional or HQ-level disagreements
- whether a change should be accepted, rejected, merged, escalated, or left unresolved

A discussion thread may be linked to:

- a topic
- an entity
- a wiki block
- a claim
- a conflict record
- a source
- a graph relationship
- a proposed patch

```pseudo
DiscussionThread {
  id
  topic_id?
  entity_id?
  block_id?
  claim_id?
  conflict_id?
  title
  status
  created_by
  created_at
  comments[]
  linked_sources[]
  proposed_patch?
  consensus_result?
  escalation_tier?
}
```

The discussion surface stores the editorial reasoning behind the curated knowledge surface.

---

### 2.3 Revision and Audit Surface

The revision and audit surface is the immutable record of all changes.

This surface is equivalent to Wikipedia’s **Revision History**, extended with structured audit metadata.

It answers:

```text
Who changed this?
What changed?
When did it change?
Why did it change?
What evidence supported the change?
Which review process approved it?
Can the previous state be restored?
```

Every accepted, rejected, merged, reverted, or escalated action creates an auditable event.

```pseudo
Revision {
  id
  target_type
  target_id
  parent_revision_id?
  actor_id
  actor_type
  timestamp
  previous_state
  new_state
  edit_summary
  rationale
  evidence_ids[]
  discussion_thread_id?
  conflict_id?
  review_action_id?
  tags[]
}
```

The revision history is not the same as the discussion layer.

```text
Revision history = immutable change ledger
Discussion layer = reasoning and conflict-resolution workspace
Curated wiki = accepted public knowledge state
```

---

## 3. Curation Workflows

### 3.1 Validation Cards

Every conflict, claim, proposed edit, or extracted update presents a validation card.

Component:

```pseudo
ValidationCard
```

Each validation card should include:

- current accepted value
- incoming or proposed update
- diff between current and proposed value
- evidence
- provenance
- extraction metadata
- source reliability indicators
- confidence score
- sensitivity classification
- linked wiki block
- linked discussion thread, if any
- linked audit history
- reviewer tier assignment
- freshness status
- contradiction status

Available reviewer actions:

- Approve
- Reject
- Merge/Edit
- Escalate
- Open Discussion
- Link to Existing Discussion
- Request Source Review
- Mark as Duplicate
- Mark as No Consensus
- Revert to Previous Accepted State

Functional behavior:

```pseudo
function handleValidationAction(card_id, action, actor, rationale):
    card = getValidationCard(card_id)

    if action == "approve":
        acceptClaimOrPatch(card, actor, rationale)

    if action == "reject":
        rejectClaimOrPatch(card, actor, rationale)

    if action == "merge_edit":
        createEditedPatch(card, actor, rationale)

    if action == "escalate":
        escalateReview(card, actor, rationale)

    if action == "open_discussion":
        createDiscussionThread(card, actor, rationale)

    if action == "no_consensus":
        preserveCurrentState(card)
        markDiscussionNoConsensus(card)

    createAuditEvent(card, action, actor, rationale)
    refreshAffectedSurfaces(card)
```

---

### 3.2 In-Wiki Curation

Every wiki block can be:

- verified
- flagged
- edited
- reverted
- discussed
- resolved
- escalated
- archived

Each block should expose inline curation controls:

```pseudo
WikiBlockActions {
  verify
  flag
  edit
  discuss
  view_history
  view_provenance
  resolve_conflict
  escalate
}
```

Each block should display:

- verification badge
- freshness indicator
- provenance modal
- conflict banner, if disputed
- maintenance tags
- linked discussion threads
- last accepted revision
- latest pending proposals

Reviewer actions trigger:

1. backend workflow update
2. immediate wiki/card/graph refresh
3. audit logging
4. claim store update if accepted
5. graph database update if accepted
6. discussion update if linked
7. notification to watchers or responsible review tier

Accepted or rejected actions flow into the canonical graph and claim store through the retroaction loop.

---

### 3.3 Article-Like and Talk-Like Separation

Metamorph should explicitly model each curated knowledge object as having two linked spaces:

```pseudo
CuratedObject {
  id
  type
  current_accepted_revision_id
  discussion_space_id
  revision_history_id
  verification_state
  dispute_state
}
```

For example:

```pseudo
Topic {
  id
  title
  curated_page_id
  discussion_page_id
  revision_history_id
  canonical_graph_refs[]
}
```

The curated page displays accepted information.

The discussion page stores contested or proposed information.

The revision history stores all state changes.

Functional rule:

```pseudo
if content_is_accepted_by_policy_confidence_and_review:
    display_in_curated_wiki()
else:
    route_to_discussion_or_review_queue()
```

---

## 4. Trust Routing and Verification States

### 4.1 Trust Routing

Incoming claims, extracted facts, proposed edits, and graph updates must be routed based on confidence, sensitivity, source reliability, contradiction level, and policy rules.

Routing states:

#### Auto-Accept

High-confidence, low-risk updates may become accepted and visible immediately if eligible by policy.

Examples:

- non-controversial metadata correction
- low-risk stale field refresh
- trusted source update
- high-confidence duplicate confirmation

```pseudo
if confidence >= auto_accept_threshold
and source_reliability == "trusted"
and sensitivity == "low"
and contradiction_detected == false:
    autoAccept()
```

#### Shadow / Pending

Moderate-confidence updates are stored but not fully accepted.

They may appear with pending badges or remain visible only to reviewers.

```pseudo
if confidence is moderate
or source_reliability is uncertain
or freshness requires confirmation:
    markPending()
    enqueueForReview()
```

#### Escalation

Low-confidence, contradictory, sensitive, high-impact, or policy-relevant updates require human review.

```pseudo
if confidence is low
or contradiction_detected == true
or sensitivity in ["legal", "policy", "protection", "security", "high-impact"]:
    escalateToReviewTier()
```

---

### 4.2 Verification States

Each claim, field, block, and entity can have a verification state.

```pseudo
VerificationState:
  - accepted
  - auto_accepted
  - pending
  - disputed
  - under_review
  - rejected
  - merged
  - escalated
  - stale
  - superseded
  - no_consensus
```

Recommended transition model:

```text
incoming
  ↓
pending / auto_accepted / escalated
  ↓
accepted / rejected / merged / disputed / no_consensus
  ↓
superseded / reverted / archived
```

---

## 5. Discussion, Consensus, and Conflict Resolution

### 5.1 Discussion Threads

A discussion thread is created when information is contested, unclear, sensitive, or requires collective judgment.

Discussion threads should support:

- comments
- replies
- source attachments
- proposed patches
- claim diffs
- reviewer mentions
- escalation requests
- consensus summaries
- resolution status
- links back to affected wiki blocks

```pseudo
DiscussionThread {
  id
  title
  target_type
  target_id
  status
  created_by
  created_at
  updated_at
  comments[]
  proposed_patch?
  linked_conflict_ids[]
  linked_claim_ids[]
  linked_sources[]
  consensus_result?
  closed_by?
  closed_at?
}
```

Thread statuses:

```pseudo
DiscussionStatus:
  - open
  - under_review
  - consensus_reached
  - no_consensus
  - rejected
  - escalated
  - resolved
  - archived
```

---

### 5.2 Consensus Model

Metamorph should not treat consensus as a simple majority vote.

Consensus should be based on:

- quality of evidence
- policy compliance
- source reliability
- freshness
- operational relevance
- regional applicability
- reviewer authority and domain expertise
- absence or presence of unresolved objections
- sensitivity level
- strength of reasoning

```pseudo
ConsensusAssessment {
  thread_id
  positions[]
  evidence_quality_score
  source_reliability_score
  policy_alignment_score
  reviewer_expertise_weight
  unresolved_objections[]
  result
}
```

Possible consensus results:

```pseudo
ConsensusResult:
  - accept
  - reject
  - merge
  - no_consensus
  - escalate
  - defer_until_more_evidence
```

Functional evaluation:

```pseudo
function evaluateConsensus(thread_id):
    thread = getDiscussionThread(thread_id)
    comments = thread.comments
    evidence = thread.linked_sources

    assessment = assessEvidence(evidence)
    policy_alignment = assessPolicyAlignment(comments, thread.proposed_patch)
    objections = extractUnresolvedObjections(comments)

    if assessment.isStrong
    and policy_alignment.isCompliant
    and objections.noneMaterial:
        return "accept"

    if assessment.isWeak
    or policy_alignment.isNonCompliant:
        return "reject"

    if objections.material
    and escalationRequired(thread):
        return "escalate"

    if competingValidPositionsExist(comments):
        return "no_consensus"

    return "defer_until_more_evidence"
```

---

### 5.3 No Consensus Behavior

When no consensus is reached, Metamorph should preserve the current accepted state unless a higher-priority safety, legal, or governance rule requires intervention.

```pseudo
function handleNoConsensus(target):
    preserveCurrentAcceptedRevision(target)
    markTargetAsNoConsensus(target)
    linkDiscussionThread(target)
    createAuditEvent("no_consensus")
```

No consensus does not mean the incoming proposal is accepted. It means the system retains the status quo while preserving the discussion trail.

---

## 6. Conflict Handling

Conflicts are queued by contradiction detection across:

- quantitative values
- normative statements
- contact information
- organizational structures
- temporal claims
- classifications
- geographic scope
- policy statements
- entity relationships
- operational procedures
- source disagreement
- reviewer disagreement

Each conflict record should contain:

```pseudo
Conflict {
  id
  target_type
  target_id
  existing_value
  incoming_value
  evidence[]
  provenance[]
  scope_note
  severity
  tier_assignment
  sensitivity
  conflict_type
  status
  linked_validation_card_id
  linked_discussion_thread_id?
  created_at
  resolved_at?
}
```

Conflict statuses:

```pseudo
ConflictStatus:
  - unresolved
  - under_review
  - discussion_open
  - consensus_reached
  - no_consensus
  - resolved
  - escalated
  - dismissed
  - archived
```

Conflict types:

```pseudo
ConflictType:
  - factual_accuracy
  - source_reliability
  - temporal_mismatch
  - quantitative_mismatch
  - classification_mismatch
  - scope_mismatch
  - geographic_mismatch
  - structural_mismatch
  - normative_disagreement
  - policy_conflict
  - sensitive_domain
  - duplicate_entity
  - graph_relationship_conflict
```

Functional lifecycle:

```text
Detected
  ↓
Queued
  ↓
Validation Card Created
  ↓
Discussion Opened if Needed
  ↓
Evidence Reviewed
  ↓
Consensus / Escalation / No Consensus
  ↓
Accepted / Rejected / Merged / Preserved / Archived
```

---

## 7. Maintenance Tags and Banners

Metamorph should use maintenance tags to make unresolved quality issues visible on the curated wiki surface.

Tags should appear on blocks, claims, sections, entities, or topics.

Examples:

```pseudo
MaintenanceTag:
  - citation_needed
  - source_review_needed
  - disputed
  - stale
  - freshness_review_needed
  - conflicting_values
  - low_confidence
  - policy_review_needed
  - regional_validation_needed
  - neutrality_or_framing_issue
  - duplicate_possible
  - graph_conflict
```

Each tag should include:

```pseudo
MaintenanceTag {
  id
  target_type
  target_id
  tag_type
  reason
  created_by
  created_at
  linked_discussion_thread_id?
  linked_conflict_id?
  severity
  visibility
}
```

Functional behavior:

```pseudo
function addMaintenanceTag(target, tag):
    target.maintenance_tags.append(tag)

    if tag.requiresDiscussion:
        ensureDiscussionThreadExists(target, tag)

    createAuditEvent("maintenance_tag_added", target, tag)
    refreshCuratedSurface(target)
```

Tags act as bridges between visible knowledge and the underlying review process.

---

## 8. Review Tiers and Escalation

Review is organized by tier.

- **Tier 1 — Field / Local**
  - operational data
  - local entities
  - local contact points
  - field-level observations
  - low-to-medium impact updates

- **Tier 2 — Regional**
  - regional SOPs
  - regional strategy
  - cross-country conflicts
  - regional operating context
  - regional coordination issues

- **Tier 3 — HQ / Thematic**
  - global policy
  - legal concerns
  - protection-sensitive content
  - high-impact decisions
  - global taxonomy
  - authoritative thematic guidance

Each tier has:

- review queues
- escalation rules
- permissions
- decision SLAs
- audit policies
- notification policies
- consensus requirements

```pseudo
function assignReviewTier(conflict_or_claim):
    if conflict_or_claim.sensitivity == "high":
        return "tier_3"

    if conflict_or_claim.scope == "regional":
        return "tier_2"

    if conflict_or_claim.scope == "local":
        return "tier_1"

    return defaultTierByDomain(conflict_or_claim.domain)
```

---

## 9. Human Retroaction Feedback Loop

When a curator, reviewer, analyst, or trusted contributor performs any action, the system records it immediately.

Actions include:

- approving
- editing
- merging
- escalating
- rejecting
- reverting
- tagging
- opening a discussion
- closing a discussion
- marking no consensus
- applying consensus
- archiving a thread

Each action creates:

1. an audit log entry
2. a revision entry, if state changed
3. an update to the curation table
4. an update to the relevant claim/fact/entity record
5. an update to graph state, if applicable
6. a UI refresh event
7. a notification event, if watchers or reviewers are subscribed

```pseudo
RetroactionEvent {
  id
  action_type
  actor_id
  actor_type
  target_type
  target_id
  previous_state
  new_state
  rationale
  evidence_ids[]
  discussion_thread_id?
  conflict_id?
  timestamp
}
```

The retroaction loop must be bidirectionally traceable:

```text
Wiki block → Claim → Source → Discussion → Decision → Audit event → Graph update

Graph node → Accepted claim → Wiki block → Revision → Reviewer action → Discussion
```

This ensures every curation action permanently alters or preserves the trusted knowledge base in an auditable and reproducible way.

---

## 10. Watchers, Notifications, and Community Trust

### 10.1 Watchers

Users may watch topics, entities, blocks, claims, discussions, or review queues.

Watchers are notified when:

- a watched block is edited
- a claim is disputed
- a discussion is opened
- a consensus decision is applied
- a conflict is escalated
- a source is rejected
- a tag is added or removed
- a watched claim becomes stale

```pseudo
Watcher {
  id
  user_id
  target_type
  target_id
  notification_preferences
}
```

---

### 10.2 Community Trust

Community verification can increase confidence when trusted users read, use, or verify a block without flagging it.

However, silent reads should not override explicit contradictions, high-risk changes, or unresolved disputes.

```pseudo
function updateCommunityTrust(block):
    if trustedUsersViewedWithoutFlag(block)
    and noActiveConflict(block)
    and freshnessWindowValid(block):
        increaseTrustScore(block)
```

Community trust signals may support promotion from pending to accepted only when policy allows.

---

## 11. Reverts and Rollbacks

Metamorph should support reverting a curated object to a previous accepted revision.

Reverts are required when:

- an accepted update is later found incorrect
- a source is invalidated
- an edit was premature
- a policy violation is detected
- an automated acceptance was wrong
- an editor applied the wrong patch
- a conflict was unresolved but content was applied

```pseudo
function revertTarget(target_id, revision_id, actor, rationale):
    previous_revision = getRevision(revision_id)
    createNewRevisionFrom(previous_revision)
    createAuditEvent("revert", actor, rationale)
    notifyWatchers(target_id)
    refreshAffectedSurfaces(target_id)
```

A revert may automatically open or update a discussion thread.

```pseudo
if revertedChangeWasSubstantive:
    ensureDiscussionThreadExists(target_id, "Revert discussion")
```

---

## 12. Audit and QA

All reviewer and system actions must be audit-trailed in immutable logs.

Audit and QA dashboards must show:

- live decisions
- historic decisions
- unresolved conflicts
- no-consensus cases
- pending discussions
- stale claims
- source reliability issues
- high-risk auto-acceptances
- revert frequency
- reviewer activity
- tier escalation patterns
- graph propagation status

All state transitions must be documented for:

- trust
- governance
- reproducibility
- accountability
- agentic review
- human oversight

The API and QA dashboards must reflect both live and historic decisions.

---

## 13. Recommended Implementation Objects

A coding agent should model Metamorph curation using the following primary objects:

```pseudo
Entity Topic {
  id
  title
  slug
  curated_page_id
  discussion_page_id
  revision_history_id
  graph_refs[]
  created_at
  updated_at
}

Entity CuratedPage {
  id
  topic_id
  current_revision_id
  blocks[]
  verification_state
  dispute_state
  protection_level
}

Entity WikiBlock {
  id
  curated_page_id
  block_type
  content
  claim_ids[]
  current_revision_id
  citations[]
  provenance[]
  verification_state
  freshness_state
  dispute_state
  maintenance_tags[]
}

Entity DiscussionPage {
  id
  topic_id
  threads[]
}

Entity DiscussionThread {
  id
  discussion_page_id
  target_type
  target_id
  title
  status
  comments[]
  proposed_patch?
  consensus_result?
  escalation_tier?
  created_by
  created_at
  closed_by?
  closed_at?
}

Entity DiscussionComment {
  id
  thread_id
  author_id
  parent_comment_id?
  body
  cited_sources[]
  created_at
}

Entity Claim {
  id
  entity_id?
  subject
  predicate
  object
  qualifiers[]
  sources[]
  provenance[]
  confidence
  verification_state
  current_revision_id
}

Entity Conflict {
  id
  target_type
  target_id
  existing_value
  incoming_value
  conflict_type
  severity
  status
  linked_discussion_thread_id?
  linked_validation_card_id?
}

Entity Revision {
  id
  target_type
  target_id
  parent_revision_id?
  actor_id
  previous_state
  new_state
  edit_summary
  rationale
  created_at
}

Entity AuditEvent {
  id
  action_type
  actor_id
  target_type
  target_id
  previous_state
  new_state
  rationale
  evidence_ids[]
  timestamp
}
```

---

## 14. Minimum API Capabilities

For Wikipedia-like curation, Metamorph should support:

```http
GET /topics/{id}
GET /topics/{id}/curated
GET /topics/{id}/discussion
GET /topics/{id}/history

POST /topics/{id}/blocks/{block_id}/edit
POST /topics/{id}/blocks/{block_id}/verify
POST /topics/{id}/blocks/{block_id}/flag
POST /topics/{id}/blocks/{block_id}/revert

POST /claims/{id}/validate
POST /claims/{id}/reject
POST /claims/{id}/merge
POST /claims/{id}/escalate

POST /conflicts/{id}/review
POST /conflicts/{id}/resolve
POST /conflicts/{id}/dismiss
POST /conflicts/{id}/escalate

POST /discussion/threads
POST /discussion/threads/{id}/comments
POST /discussion/threads/{id}/close
POST /discussion/threads/{id}/apply-consensus

POST /tags
DELETE /tags/{id}

GET /audit/events
GET /revisions/{target_type}/{target_id}
```

---

## 15. Coding-Agent Decision Rules

A coding agent implementing Metamorph should use these rules.

### 15.1 Add Directly to Curated Wiki When

```pseudo
if information_is_factual
and source_is_reliable
and confidence_is_high
and sensitivity_is_low
and no_conflict_detected
and policy_allows_auto_accept:
    updateCuratedWiki()
    updateCanonicalClaimStore()
    updateGraph()
    createRevision()
    createAuditEvent()
```

---

### 15.2 Route to Review Queue When

```pseudo
if confidence_is_moderate
or source_reliability_is_uncertain
or freshness_requires_confirmation
or claim_changes_existing_value:
    createValidationCard()
    enqueueForReview()
    markAsPending()
```

---

### 15.3 Open Discussion When

```pseudo
if information_is_contested
or multiple_valid_sources_disagree
or proposed_change_affects_interpretation
or reviewer_disagreement_exists
or prior_revert_exists
or change_is_substantial:
    createDiscussionThread()
    linkToTarget()
    markTargetAsDisputed()
```

---

### 15.4 Escalate When

```pseudo
if sensitivity_is_high
or policy_risk_exists
or legal_risk_exists
or protection_risk_exists
or cross_regional_impact_exists
or tier_1_or_2_cannot_resolve:
    escalateToHigherTier()
    createAuditEvent()
```

---

### 15.5 Preserve Current State When No Consensus

```pseudo
if discussion_result == "no_consensus":
    keepCurrentAcceptedRevision()
    markIncomingProposalAsNotAccepted()
    recordNoConsensus()
    linkDiscussionToTarget()
    notifyWatchers()
```

---

## 16. System Principle

The core Metamorph curation principle is:

```pseudo
CuratedWiki = materialized_view(CurrentAcceptedKnowledge)
DiscussionLayer = deliberation_space_for_contested_or_uncertain_knowledge
RevisionHistory = immutable_change_log
AuditLog = governance_and_accountability_record
CanonicalGraph = machine_readable_trusted_state
```

Or, more simply:

> Metamorph should separate the presentation of trusted knowledge from the negotiation of contested knowledge.

This means:

```pseudo
if knowledge_is_accepted:
    show_it_as_curated
elif knowledge_is_pending:
    show_it_as_pending_or_queue_for_review
elif knowledge_is_disputed:
    route_it_to_discussion_and_conflict_resolution
elif knowledge_is_rejected:
    preserve_it_in_audit_but_do_not_publish_as_truth
```

---

## 17. Documentation Links

See also:

- `PIPELINE.md` for knowledge flow and retroaction summary
- `ARCHITECTURE.md` for system context
- `API.md` for ValidationCard, discussion, revision, and curation endpoints
- `GRAPH.md` for canonical graph propagation rules
- `QA.md` for audit, quality assurance, and reviewer dashboard behavior
