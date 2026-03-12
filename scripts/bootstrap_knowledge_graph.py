#!/usr/bin/env python3
"""
Bootstrap the Neo4j knowledge graph from the ontology (OWL/SKOS in Turtle format).
- Creates class/node labels and core relationship types in Neo4j
- Sets up SKOS controlled vocabularies (ConceptSchemes, Concepts)
- For use with unhcr-knowledge-ontology.ttl
"""

import sys
import argparse
from neo4j import GraphDatabase
import rdflib


def main():
    parser = argparse.ArgumentParser(
        description="Bootstraps knowledge graph from ontology .ttl to Neo4j."
    )
    parser.add_argument(
        "--ontology", type=str, required=True, help="Path to .ttl ontology file"
    )
    parser.add_argument(
        "--neo4j-url", type=str, default="bolt://localhost:7687", help="Neo4j URI"
    )
    parser.add_argument("--neo4j-user", type=str, default="neo4j")
    parser.add_argument("--neo4j-password", type=str, default="password")
    args = parser.parse_args()

    # Parse ontology
    g = rdflib.Graph()
    print(f"[INFO] Loading {args.ontology} ...")
    g.parse(args.ontology, format="turtle")

    # Connect to Neo4j
    driver = GraphDatabase.driver(
        args.neo4j_url, auth=(args.neo4j_user, args.neo4j_password)
    )
    print(f"[INFO] Connected to {args.neo4j_url}")

    with driver.session() as session:
        # Node labels (owl:Class)
        for s in g.subjects(rdflib.RDF.type, rdflib.OWL.Class):
            label = s.split("#")[-1] if "#" in s else s.split("/")[-1]
            cypher = "MERGE (c:OntologyClass {name: $label})"
            session.run(cypher, label=label)
            print(f"[CLASS] {label}")
        # Relationship types (owl:ObjectProperty)
        for s in g.subjects(rdflib.RDF.type, rdflib.OWL.ObjectProperty):
            rel = s.split("#")[-1] if "#" in s else s.split("/")[-1]
            cypher = "MERGE (r:OntologyRelationship {type: $rel})"
            session.run(cypher, rel=rel)
            print(f"[REL] {rel}")
        # SKOS ConceptSchemes and Concepts
        for scheme in g.subjects(
            rdflib.RDF.type,
            rdflib.URIRef("http://www.w3.org/2004/02/skos/core#ConceptScheme"),
        ):
            scheme_name = (
                scheme.split("#")[-1] if "#" in scheme else scheme.split("/")[-1]
            )
            cypher = "MERGE (s:ConceptScheme {scheme: $scheme})"
            session.run(cypher, scheme=scheme_name)
            # Link to contained concepts
            for concept in g.subjects(rdflib.SKOS.inScheme, scheme):
                conc_name = (
                    concept.split("#")[-1] if "#" in concept else concept.split("/")[-1]
                )
                cypher2 = "MERGE (c:Concept {name: $name})-[:IN_SCHEME]->(s:ConceptScheme {scheme: $scheme})"
                session.run(cypher2, name=conc_name, scheme=scheme_name)
                print(f"[SKOS] {conc_name} in {scheme_name}")

    print("[DONE] Knowledge graph ontology bootstrapped!")


if __name__ == "__main__":
    main()
