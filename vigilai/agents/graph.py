from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents.state import AgentState
from agents.nodes.ingest import ingest_node
from agents.nodes.preprocess import preprocess_node
from agents.nodes.ner import ner_node
from agents.nodes.relation import relation_node
from agents.nodes.normalize import normalize_node
from agents.nodes.report import report_node


def _should_hitl(state: AgentState) -> str:
    return "hitl_pause" if state.get("hitl_required") else "report"


def build_graph() -> StateGraph:
    memory = MemorySaver()
    graph = StateGraph(AgentState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("preprocess", preprocess_node)
    graph.add_node("ner", ner_node)
    graph.add_node("relation", relation_node)
    graph.add_node("normalize", normalize_node)
    graph.add_node("report", report_node)

    # Placeholder node that signals HITL pause — pipeline_runner handles actual wait
    graph.add_node("hitl_pause", lambda s: s)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "preprocess")
    graph.add_edge("preprocess", "ner")
    graph.add_edge("ner", "relation")
    graph.add_edge("relation", "normalize")
    graph.add_conditional_edges("normalize", _should_hitl, {
        "hitl_pause": "hitl_pause",
        "report": "report",
    })
    graph.add_edge("hitl_pause", END)
    graph.add_edge("report", END)

    return graph.compile(checkpointer=memory)


if __name__ == "__main__":
    g = build_graph()
    result = g.invoke(
        {
            "narrative_id": "test-001",
            "raw_text": "Maine metformin 500mg li aur subah uthke ulti jaisi feeling thi",
            "ws_narrative_id": "test-001",
        },
        config={"configurable": {"thread_id": "test-001"}},
    )
    print("Entities:", result.get("entities"))
    print("Relations:", result.get("relations"))
    print("Normalized:", result.get("normalized_pairs"))
