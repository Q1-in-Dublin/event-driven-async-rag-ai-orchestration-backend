from typing import TypedDict

class GraphState(TypedDict):
    reuqest_id : str
    user_text : str
    needs_rag : bool
    query_embedding: list[float]
    retrieved_docs: list[str]
    retrieved_doc_ids: list[str]
    prompt : str
    llm_response: str