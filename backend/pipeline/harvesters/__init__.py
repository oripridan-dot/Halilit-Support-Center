"""
Harvester Package - Data ingestion from the 3 source pillars.

Official:    Manufacturer websites (specs, names, images)
Commercial:  Halilit website (prices, SKUs, stock)
Contextual:  Web search + AI synthesis (reviews, tips)
"""

from .official import OfficialHarvester
from .commercial import CommercialHarvester
from .contextual import ContextualHarvester

__all__ = ["OfficialHarvester", "CommercialHarvester", "ContextualHarvester"]
