from .base import Entity
from typing import Optional, List, Dict


class PopulationGroup(Entity):
    groupType: Optional[str] = None
    estimatedSize: Optional[List[Dict]] = None


class HouseholdProfile(Entity):
    pass


class VulnerabilityProfile(Entity):
    pass


class CommunityStructure(Entity):
    pass


class RegistrationCohort(Entity):
    pass
