# Prompt as Specification Template

> **Purpose:** Use this template to author **specific, bounded specifications** that extend AGENT.md without repeating it. 

Each spec should capture **only the delta** — what's unique to this component, workflow, or feature.

---

## Alignment Verification (Complete Before Writing Spec)

Before drafting, confirm this spec does not conflict with:

| AGENT.md Section | Verification Check | Status |
|------------------|-------------------|--------|
| § Architecture Principles (1-10) | Does this spec respect all 10 principles? | [ ] |
| § Layer Definitions (0-6) | Which layer(s) does this touch? | L___ |
| § Ontology Reference | Does this use/extend defined node/edge types? | [ ] |
| § Data Model Concepts | Are entities/claims/evidence structures compatible? | [ ] |
| § Technology Stack | Are proposed tools in the approved stack? | [ ] |
| § Workflows (1-4) | Does this fit within or extend defined workflows? | [ ] |
| § Security/Governance | Are audit/provenance requirements met? | [ ] |

**If any check fails:** Revise spec or propose AGENT.md amendment via ADR.

---



<provided_material>
[AGENT.md](AGENT.md) defines: 
- [x] The system vision, layered architecture, and key landscape/pipeline diagrams.
- [x] End-to-end knowledge pipeline, claim/evidence model, rules for provenance, agent context, and progressive QA.
- [x] PostgreSQL, graph, and vector schema (DBA/operator reference).
- [x] Reviewer, conflict, curation, and trust/verification surface/policy.
- [x] For hands-on setup/bootstrapping.

</provided_material>

<markdown_specification>
## Overview
[High-level description of what we're building - requirements not already implied by AGENT.md

## Core Features
- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## User Flow

```mermaid
[Insert flow diagram or step-by-step user journey]
```
## Data Structure
 
```mermaid
// Key data models/types if applicable
```

## Component Architecture
```mermaid
[Breakdown of main components and their relationships]
```

</markdown_specification>


<UI_behavior>

Use only of if the spec comes with UI requirements

## Layout & Responsiveness

- Desktop layout requirements
- Mobile/tablet breakpoints
- Grid/flexbox specifications

## Interactions

- Hover states
- Click/tap behaviors
- Animations & transitions
- Loading states
- Error states
- Success confirmations

## Accessibility

- Keyboard navigation
- Screen reader considerations
- Color contrast requirements
- Focus indicators

</UI_behavior>



<data_contract>

## API Specifications

- Endpoints needed
- Request/response formats
- Error handling patterns

## State Management

- Global state structure
- Local vs shared state
- Data persistence requirements
- Cache strategies

</data_contract>



<verification>

## Visual Verification Checklist

- Matches design specifications
- Responsive behavior confirmed
- Dark/light mode if applicable
- Cross-browser consistency

## Functional Verification

- All user flows complete
- Edge cases handled
- Error scenarios tested
- Data persistence verified

</verification>

<testing_guidance>

## Manual Testing Scenarios

- Happy path testing
- Edge case testing
- Device/browser testing matrix

## Automated Testing Expectations

- Unit test coverage requirements
- Integration test scenarios
- E2E test critical paths

## Performance Testing

- Load testing criteria
- Lighthouse score targets
- Memory leak checks

</testing_guidance>



<success_criteria>
## Definition of Done

- All core features implemented
- Tests passing
- Performance targets met
- Documentation updated
- Code review completed

## Acceptance Criteria

- Stakeholder approval
- User testing passed
- Deployment successful

</success_criteria>