from .base import Entity
from typing import Optional, List, Dict


class Operation(Entity):
    name: str
    operationCode: Optional[str] = None


class Project(Entity):
    name: str
    projectCode: Optional[str] = None
    budgetUsd: Optional[List[Dict]] = None


class Programme(Entity):
    name: str
    programmeType: Optional[str] = None


class Activity(Entity):
    name: str
    activityType: Optional[str] = None


class SubOffice(Entity):
    name: str


class ServicePoint(Entity):
    name: str


class ImplementingPartner(Entity):
    name: str
