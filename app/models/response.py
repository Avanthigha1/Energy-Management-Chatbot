"""
models/response.py — Exact response format required.

Every chat response follows this structure.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatResponse(BaseModel):
    text:        str                                   
    kpis:        Dict[str, Any]                         
    insights:    Dict[str, Any]                        
    floor_data:  Optional[List[Dict[str, Any]]] = None  
    comparison:  Optional[Dict[str, Any]]       = None  
