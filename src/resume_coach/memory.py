from langgraph.checkpoint.memory import MemorySaver

memory_store = MemorySaver()

def get_thread_config(thread_id: str) -> dict:
    """
    Returns the LangGraph config dict for a given session thread.
    Every agent.invoke() call passes this config so LangGraph
    knows which conversation history to load.
    """
    return {"configurable": {"thread_id": thread_id}}

