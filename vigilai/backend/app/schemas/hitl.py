from pydantic import BaseModel


class HITLCandidate(BaseModel):
    rank: int
    term: str
    code: str
    system_organ_class: str | None = None
    score: float


class HITLResolveRequest(BaseModel):
    selected_term: str
    selected_code: str
    officer_id: str = "demo-officer"
