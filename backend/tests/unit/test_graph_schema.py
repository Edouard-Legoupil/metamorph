import pytest
from neo4j import AsyncGraphDatabase


@pytest.mark.asyncio
async def test_country_node_creation():
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687", auth=("neo4j", "password")
    )
    async with driver.session() as session:
        await session.run("""
            CREATE (c:Country:GeographicEntity:Entity {
                identifier:"uuid123", name:"Uganda", iso3:"UGA",
                createdAt:datetime(), lastUpdated:datetime(),
                verificationStatus:'AUTO_ACCEPTED', hasTag:['test']
            });
        """)
        result = await session.run("MATCH (c:Country {iso3:'UGA'}) RETURN c")
        rec = await result.single()
        assert rec


@pytest.mark.asyncio
async def test_temporal_versioning():
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687", auth=("neo4j", "password")
    )
    async with driver.session() as session:
        await session.run("""
          CREATE (i:Indicator:Entity {
            identifier:'uuid-ind',
            indicatorCode:'POP01',
            numericValue:[
              {value:100.0, date:'2023-01-01', source:'doc-x'},
              {value:140.0, date:'2023-07-01', source:'doc-y'}
            ],
            createdAt:datetime(), lastUpdated:datetime(),
            verificationStatus:'SHADOW', hasTag:['pop','trend']
          });
        """)
        result = await session.run(
            "MATCH (i:Indicator {indicatorCode:'POP01'}) RETURN i.numericValue AS vals"
        )
        rec = await result.single()
        vals = rec["vals"]
        assert vals[-1]["value"] == 140.0
