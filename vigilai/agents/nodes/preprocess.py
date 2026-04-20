import re
import unicodedata
from agents.state import AgentState


def preprocess_node(state: AgentState) -> AgentState:
    text = state["raw_text"]

    # Unicode normalization
    text = unicodedata.normalize("NFC", text)

    # Remove URLs, hashtags, mentions, emojis
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'#\w+|@\w+', '', text)
    text = re.sub(r'[^\w\s\.\,\!\?\-\/]', '', text, flags=re.UNICODE)

    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Simple whitespace tokenization for subword hint
    tokens = text.split()

    return {
        **state,
        "clean_text": text,
        "tokens": tokens,
    }
