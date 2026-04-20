from typing import Optional
from beanie import Document


class WHOARTTerm(Document):
    code: str
    term: str
    system_organ_class: Optional[str] = None

    class Settings:
        name = "whoart_terms"
