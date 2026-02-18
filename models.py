from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class KeywordResult(BaseModel):
    seed_keyword: str
    suggestions: List[str]
    questions: List[str]
    trends_score: Optional[float]
    created_at: datetime = datetime.now()

class SearchHistory(BaseModel):
    query: str
    results_count: int
    created_at: datetime = datetime.now()
