"""
models/intent.py — Defines what the LLM must return.

The LLM reads the user's query and fills in this structure.
Pydantic checks it immediately — if the LLM returns garbage, we catch it here.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class QueryType(str, Enum):
    SINGLE_DAY      = "single_day"       
    FLOOR_BREAKDOWN = "floor_breakdown"  
    COMPARISON      = "comparison"       
    PUE_ANALYSIS    = "pue_analysis"    
    COOLING_RATIO   = "cooling_ratio"    
    UNKNOWN         = "unknown"          


class IntentResult(BaseModel):
    intent:     QueryType
    date_1:     Optional[str] = None   
    date_2:     Optional[str] = None   
    metric:     Optional[str] = None   
    
