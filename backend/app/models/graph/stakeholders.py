from .base import Entity
from typing import Optional


class Organisation(Entity):
    name: str


class UNAgency(Entity):
    name: str


class ClusterSector(Entity):
    name: str


class NGOPartner(Entity):
    name: str


class PrivateDonor(Entity):
    pass


class GovernmentAuthority(Entity):
    name: str


class Position(Entity):
    pass


class FocalPoint(Entity):
    pass


class ContactInfo(Entity):
    contactOrgName: Optional[str] = None
    contactEmail: Optional[str] = None
    contactWebsite: Optional[str] = None
    contactAddress: Optional[str] = None
