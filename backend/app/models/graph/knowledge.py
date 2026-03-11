from .base import Entity
from typing import Optional, List, Dict


class Indicator(Entity):
    indicatorCode: str
    numericValue: Optional[List[Dict]] = None


class InterventionType(Entity):
    pass


class EvidenceFinding(Entity):
    textValue: Optional[str] = None


class EffectivenessMetric(Entity):
    pass


class ContextCondition(Entity):
    pass


class LessonsLearned(Entity):
    pass


class UnintendedEffect(Entity):
    pass


class Document(Entity):
    pass


class Assessment(Entity):
    pass


class SituationReport(Entity):
    pass


class ActivityReport(Entity):
    pass


class TrainingMaterial(Entity):
    pass


class Dataset(Entity):
    pass


class Evaluation(Entity):
    pass


class Sector(Entity):
    sectorCode: Optional[str] = None
    sectorVocabulary: Optional[str] = None
    sectorPercentage: Optional[float] = None
    sectorLabel: Optional[str] = None
