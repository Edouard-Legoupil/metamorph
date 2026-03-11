from neo4j import GraphDatabase, Transaction
import os
import uuid
from typing import List, Dict

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def upsert_document_txn(metadata: dict, file_path: str) -> str:
    doc_id = metadata.get("doc_id") or str(uuid.uuid4())
    now = metadata.get("created_at")
    cypher = (
        "MERGE (d:Document:Entity {identifier: $id}) "
        "SET d.title=$title, d.author=$author, d.publication_date=$pub, d.source_url=$src, "
        "    d.version=1, d.status='IMPORTED', d.file_path=$path, d.createdAt=$now, d.lastUpdated=$now "
        "RETURN d.identifier"
    )
    with driver.session() as session:

        def do_txn(tx: Transaction):
            tx.run(
                cypher,
                id=doc_id,
                title=metadata.get("title"),
                author=metadata.get("author"),
                pub=metadata.get("publication_date"),
                src=metadata.get("source_url"),
                path=file_path,
                now=now,
            )

        session.execute_write(do_txn)
    return doc_id


def upsert_triplets_neo4j(doc_id: str, triplets: List[Dict]):
    cypher = """
    MATCH (d:Document {identifier: $doc_id})
    FOREACH (t IN $triplets |
      MERGE (s:Entity {name: t.subject.name, label: t.subject.label})
      MERGE (o:Entity {name: t.object.name, label: t.object.label})
      MERGE (s)-[r:REL {type: t.predicate}]->(o)
      SET r += t.metadata, s += t.subject.properties, o += t.object.properties
      SET r.source_document_id = $doc_id
    )
    """
    # This cypher is illustrative; you might want to refine node label/property logic.
    with driver.session() as session:
        session.run(cypher, doc_id=doc_id, triplets=triplets)


def update_document_status_neo4j(doc_id: str, new_status: str):
    cypher = "MATCH (d:Document {identifier: $doc_id}) SET d.status=$status"
    with driver.session() as session:
        session.run(cypher, doc_id=doc_id, status=new_status)
