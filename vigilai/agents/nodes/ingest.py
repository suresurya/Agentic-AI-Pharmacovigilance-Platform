import re
from agents.state import AgentState


def ingest_node(state: AgentState) -> AgentState:
    raw = state["raw_text"].strip()

    # Detect language mix ratio: rough heuristic — Hindi words in Roman script
    hindi_markers = [
        "aur", "ke", "ki", "ka", "hai", "tha", "thi", "mein", "ne", "ko",
        "se", "par", "bhi", "nahi", "nahin", "bahut", "kuch", "yeh", "woh",
        "agar", "toh", "phir", "baad", "pehle", "jab", "jaise", "jaisi",
        "lena", "liya", "li", "lete", "kha", "khaaya", "piya", "uthna",
        "chakkar", "ulti", "dard", "kaanpna", "sujan", "khujli", "rash",
    ]
    words = re.findall(r'\b\w+\b', raw.lower())
    hindi_count = sum(1 for w in words if w in hindi_markers)
    ratio = round(hindi_count / max(len(words), 1), 2)

    return {
        **state,
        "raw_text": raw,
        "language_mix_ratio": ratio,
    }
