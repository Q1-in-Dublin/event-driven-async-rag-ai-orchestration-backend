from typing import TypedDict

class GraphState(TypedDict):
    reuqest_id : str
    user_text : str
    needs_rag : str
    retrieved_docs : list[str]
    prompt : str
    llm_response: str