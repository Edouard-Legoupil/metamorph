from .base import Entity
from typing import Optional


class Policy(Entity):
    policyCode: Optional[str] = None


class SOP(Entity):
    pass


class LegalFramework(Entity):
    instrumentType: Optional[str] = None


class NationalLaw(Entity):
    pass


class ExComConclusion(Entity):
    pass


class PledgeCommitment(Entity):
    pass


class StandardIndicator(Entity):
    pass
