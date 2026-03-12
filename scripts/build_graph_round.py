#!/usr/bin/env python3
"""
Progressive Knowledge Graph Builder
- Applies round-based, dependency-aware graph materialization as in ontology README
- Usage: python build_graph_round.py --round N
"""

import sys
import argparse
import os
from neo4j import GraphDatabase


def build_round(driver, round_num):
    with driver.session() as session:
        if round_num == 1:
            # Seed anchors: Country, Region, Donor, Organisation, Policy, LegalFramework, PopulationGroup (empty)
            # Here you would crawl or extract stable masterdata into Neo4j from CSV/static upstreams
            print(
                "[R1] Seeding countries, regions, donors, orgs, policies, legal frameworks, population masters..."
            )
            # Example stub:
            session.run("MERGE (c:Country {iso3: 'KEN', name: 'Kenya'})")
            session.run("MERGE (o:Organisation {name: 'UNHCR'})")
            print("[DONE] Round 1 masterdata. Extend with actual source ingestion.")
        elif round_num == 2:
            print(
                "[R2] Seeding operational context: situations, operations, programmes, partners..."
            )
            # Example stub:
            session.run("MERGE (s:Situation {title: 'Kenya Situation'})")
            # ...add code to extract/crawl paradata, infer links
            print("[DONE] Round 2 context. Extend with NER/ETL/parsing.")
        elif round_num == 3:
            print("[R3] Seeding evidence, transactional detail, claims...")
            session.run("MERGE (e:Evaluation {title: 'Eval 2024', about: 'Kenya'})")
            # ...add code to parse/load evaluations, contracts, etc
            print("[DONE] Round 3 evidence. Extend to ETL actual documents + claims.")
        else:
            print(f"[ERR] Unknown round {round_num}. Use 1-3.")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Incremental knowledge graph builder per ontology rounds."
    )
    parser.add_argument(
        "--round",
        required=True,
        type=int,
        help="Build round: (1=anchors, 2=context, 3=evidence)",
    )
    parser.add_argument(
        "--neo4j-url", type=str, default="bolt://localhost:7687", help="Neo4j URI"
    )
    parser.add_argument("--neo4j-user", type=str, default="neo4j")
    parser.add_argument("--neo4j-password", type=str, default="password")
    args = parser.parse_args()
    driver = GraphDatabase.driver(
        args.neo4j_url, auth=(args.neo4j_user, args.neo4j_password)
    )
    build_round(driver, args.round)
    print("[SUCCESS] Round completed. See docs/ontology/README.md for next steps.")


if __name__ == "__main__":
    main()
