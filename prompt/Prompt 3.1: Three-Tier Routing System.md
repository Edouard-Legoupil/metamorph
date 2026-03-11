Implement the trust routing system from Pipeline Blueprint Sections 4.2 and 7.1.

Create services/routing/trust_router.py:

1. Confidence-based routing:
   - Extract extraction_confidence from triplet metadata
   - Apply entity_resolution_confidence from GLinker
   - Calculate aggregate_confidence = weighted average

2. Tier assignment logic:
   def determine_tier(triplet, existing_graph_state):
       # 1. Check for existing conflicts
       if has_conflict(triplet):
           conflict = create_conflict_record(triplet)
           if conflict.severity == "CRITICAL":
               return ("🔴 HUMAN_ESCALATION", {"tier": 2, "conflict": conflict})
           else:
               return ("🟡 SHADOW_UPDATE", {"conflict": conflict})
       
       # 2. Check for new entity
       if not triplet.subject.id and not triplet.object.id:
           return ("🔴 HUMAN_ESCALATION", {"tier": 1, "reason": "new_entity"})
       
       # 3. Check confidence thresholds
       if triplet.metadata.extraction_confidence >= 0.95:
           if triplet.subject.id and triplet.object.id:
               return ("🟢 AUTO_ACCEPT", {})
           else:
               # Entity resolution needed
               return ("🟡 SHADOW_UPDATE", {"reason": "entity_resolution_needed"})
       
       elif triplet.metadata.extraction_confidence >= 0.70:
           return ("🟡 SHADOW_UPDATE", {"reason": "confidence_threshold"})
       
       else:
           return ("🔴 HUMAN_ESCALATION", {"tier": 1, "reason": "low_confidence"})

3. Shadow update implementation:
   - Update graph node with verification_status = "SHADOW"
   - Update wiki block with "⚠️ PENDING" tag
   - Create CurationQueueItem
   - Schedule for review within SLA (24h for MINOR, 7d for SHADOW)

4. Auto-accept implementation:
   - Update graph node with verification_status = "AUTO_ACCEPTED"
   - Add 🤖 icon to wiki block
   - Increment source_documents count
   - No human review needed
   - Track for community verification (see 3.2)

5. Human escalation:
   - Create CurationQueueItem with priority based on severity
   - Assign to appropriate tier (1: Field, 2: Regional, 3: HQ)
   - Send notification (email, in-app, Slack)
   - Track SLA and escalate if unassigned > 48h

6. Routing metrics:
   - Track distribution by tier (auto/shadow/human)
   - Monitor average time to resolution
   - Flag routing logic issues (e.g., too many auto-accepts with later conflicts)


Add REST endpoints for batch trust routing or to wire curation/SLAs to frontend review/curation control,    