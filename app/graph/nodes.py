from app.graph.state import GraphState
from app.db.session import SessionLocal
from app.rag.embedding import generate_embedding
from app.rag.vector_search import search_similar_documents

from app.llm.vertex_client import generate_response
from app.db.models import Request, Result

RAG_KEYWORDS = [
    "정책", "규정", "가이드", "휴가", "보안", "복지", "문서",
    "policy", "guideline", "regulation", "vacation", "security", "benefits", "document",
]
def classify_intent(state:GraphState) ->GraphState:
    text = state["user_text"].lower()
    needs_rag = any(keyword.lower() in text for keyword in RAG_KEYWORDS)
    return {**state, "needs_rag": needs_rag}

def embed_query(state: GraphState) -> GraphState:
    embedding = generate_embedding(state["user_text"])
    return {**state, "query_embedding": embedding}

def search_vector_db(state: GraphState) -> GraphState:
    db = SessionLocal()
    try:
        docs = search_similar_documents(db, state["query_embedding"], top_k=3)
    finally:
        db.close()
    return {
        **state,
        "retrieved_docs": [doc.content for doc in docs],
        "retrieved_doc_ids": [str(doc.id) for doc in docs],
    }

def build_prompt(state: GraphState) -> GraphState:
    if state.get("retrieved_docs"):
        context = "\n\n".join(state["retrieved_docs"])
        prompt = f"Context:\n{context}\n\nQuestion: {state['user_text']}"
    else:
        prompt = state["user_text"]
    return {**state, "prompt": prompt}


def call_llm(state: GraphState) -> GraphState:
    response = generate_response(state["prompt"])
    return {**state, "llm_response": response}


def save_result(state:GraphState) -> GraphState:
    db = SessionLocal()
    try :
        request = db.query(Request).filter(Request.id == state["request_id"]).first()
        if request:
            request.status = "done"

        result = Result(
            request_id = state["request_id"],
            llm_response = state["llm_response"],
            retrieved_doc_ids = state.get("retrieved_doc_ids") or None,

        )
        db.add(result)
        db.commit()

    finally:
        db.close()
    return state