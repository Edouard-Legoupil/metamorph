Implement the community trust system from Pipeline Blueprint Section 4.3.2.

Create services/trust/community_trust.py:

1. Trust score model:
   - Each wiki block has community_trust_score (integer)
   - Incremented by:
     * User reads block and does not flag: +1 (max 1 per user per block)
     * User clicks [Verify] button: +3
     * User cites block in proposal (via tracking): +5
   - Decremented by:
     * User flags as incorrect: -2 (triggers review)
     * Conflict discovered after read: -1 per affected reader

2. Implicit verification logic:
   threshold = config.get("COMMUNITY_TRUST_THRESHOLD", 3)
   
   IF block.verification_status == "AUTO_ACCEPTED":
       if block.community_trust_score >= threshold:
           block.verification_status = "COMMUNITY_VERIFIED"
           block.verified_at = now()
           # Remove 🤖 icon, add 👥 icon

3. Read tracking:
   - Track unique user reads per block
   - Use browser fingerprinting or auth for logged-in users
   - Store read events: {block_id, user_id, timestamp, session_id}
   - Deduplicate reads within 24h per user

4. Flag workflow:
   - When user flags content, create FlagRecord
   - Flag triggers:
     * Immediate review queue entry
     * Notification to Tier 1 focal point
     * Block temporarily shows "Under Review" banner
   - If 3+ flags from unique users, auto-escalate to Tier 2

5. Trust decay:
   - Trust scores decay over time (configurable: 10% per year)
   - Newer verifications weighted more heavily
   - If block has no reads in 6 months, flag for review

6. Verification visualization:
   - 🤖 Auto-accepted (no human eyes yet)
   - ⚠️ Pending verification (shadow update)
   - 👥 Community-verified (implicit consensus)
   - ✅ Human-verified (explicit curator approval)
   - 🔴 Contested (active flags/conflicts)

Plug these hooks into block preview endpoints, and invoke trust score/read/verify/flag in REST as needed for wiki page rendering or agentic moderation.   