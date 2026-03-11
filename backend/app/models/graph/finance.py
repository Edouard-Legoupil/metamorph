from .base import Entity
from typing import Optional, List, Dict


class Donor(Entity):
    donorCode: Optional[str] = None


class FundingInstrument(Entity):
    amountUsd: Optional[List[Dict]] = None


class Budget(Entity):
    pass


class Expenditure(Entity):
    pass


class FundingAppeal(Entity):
    pass


class IATITransaction(Entity):
    transactionTypeCode: Optional[str] = None
    transactionDate: Optional[str] = None
    transactionValue: Optional[List[Dict]] = None
    transactionCurrency: Optional[str] = None
