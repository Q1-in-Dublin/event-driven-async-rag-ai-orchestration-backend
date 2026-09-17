from app.graph.state import GraphState

RAG_KEYWORDS = [
    "정책", "규정", "가이드", "휴가", "보안", "복지", "문서",
    "policy", "guideline", "regulation", "vacation", "security", "benefits", "document",
]
def classify_intent(state:GraphState) ->GraphState:
    text = state["user_text"].lower()
    needs_rag = any(keyword.lower() in text for keyword in RAG_KEYWORDS)
    return {**state, "needs_rag": needs_rag}