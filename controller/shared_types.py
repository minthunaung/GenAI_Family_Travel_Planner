from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel,Field

class HybridState(BaseModel):
    input: str # Still need input for initial state, though router is removed
    next: Optional[
        Literal["seed_data","create_rag","fetch_family","extract_location","photo_memory","summarize"
        ]
    ] = None
    output: Optional[str] = None # Still need output for final result
    history: List[str] = [] # Still need history

    family: Optional[List[Dict[str, Any]]] = None
    selected_activity: Optional[str] = None
    rag_context: Optional[List[str]] = None
    recommendations: Optional[str] = None
    location: Optional[str] = None
    weather_ok: Optional[bool] = None
    weather_info: Optional[str] = None
    photo_idea: Optional[str] = None
    photo_url: Optional[str] = None
    memory_log: Optional[List[str]] = []
    decision: Optional[str] = None