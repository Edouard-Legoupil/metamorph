from .base import Entity
from typing import Optional, List, Dict


class Country(Entity):
    name: str
    iso3: str
    geo_lat: Optional[float] = None
    geo_long: Optional[float] = None


class Region(Entity):
    name: str
    adminLevel: Optional[int] = None
    pcode: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_long: Optional[float] = None


class Settlement(Entity):
    name: str
    settlementType: Optional[str] = None
    populationFigure: Optional[List[Dict]] = (
        None  # [{"value": int, "date": str, "source": str}]
    )
    populationDate: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_long: Optional[float] = None


class Border(Entity):
    name: str
    geo_lat: Optional[float] = None
    geo_long: Optional[float] = None


class DisasterZone(Entity):
    name: str
    geo_lat: Optional[float] = None
    geo_long: Optional[float] = None
