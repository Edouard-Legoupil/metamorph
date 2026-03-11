# Metamorph Graph Schema

## Node Types (Labels)
Country, Region, Settlement, PopulationGroup, Project, Policy, ... (see full ontology mapping in TTL)

## Universal Properties
- identifier (UUID, unique)
- createdAt, lastUpdated (datetime)
- verificationStatus ("AUTO_ACCEPTED", etc)
- hasTag (list[str])

## Versioned Fields
- time-series ≈ `[{"value": ..., "date": ..., "source": ...}, ...]`, e.g. populationFigure, numericValue, amountUsd

## Relationships
All object properties in ontology. Each edge: `{source_document_id, confidence, created_at, verification_status}`.

## Indexes
- Unique on all identifiers.
- Text/geo/search fields indexed.

*(Copy in the ontology for full mapping)*
