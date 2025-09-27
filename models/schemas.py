from pydantic import BaseModel

class ResearchQuery(BaseModel):
    query: str
    domain: str