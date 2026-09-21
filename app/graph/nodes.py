from app.graph.state import GraphState
from app.db.session import SessionLocal
from app.rag.embedding import generate_embedding
from app.rag.vector_search import search_similar_documents

from app.llm.vertex_client import generate_response
from app.db.models import Request, Result
from langgraph.graph import END, StateGraph
from slack_sdk import WebClient
from app.config import settings


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


def respond_to_slack(state: GraphState) -> GraphState:
    print(f"[DEBUG] respond_to_slack called with channel_id={state.get('channel_id')}")
    try:
        client = WebClient(token=settings.slack_bot_token)
        channel_id = state.get("channel_id")
        user_id = state.get("user_id")
        response = state["llm_response"]

        if channel_id:
            text = f"<@{user_id}> {response}"
            client.chat_postMessage(channel=channel_id, text=text)
            print(f"[Slack] Sent message to {channel_id}")
        else:
            print(f"[DEBUG] No channel_id in state")
    except Exception as e:
        print(f"[Slack Error] Failed to send message: {e}")
        import traceback
        traceback.print_exc()

    return state

# Connecting LangGraph State graph
# integrating as a workflow
def build_graph():
    # initiate node and register
    graph = StateGraph(GraphState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("embed_query", embed_query)
    graph.add_node("search_vector_db", search_vector_db)
    graph.add_node("build_prompt", build_prompt)
    graph.add_node("call_llm", call_llm)
    graph.add_node("save_result", save_result)
    graph.add_node("respond_to_slack", respond_to_slack)

    #starting point
    graph.set_entry_point("classify_intent")
    #conditional point
    graph.add_conditional_edges(
        "classify_intent",
        lambda state: "embed_query" if state["needs_rag"] else "build_prompt",
    )
    # embed_query -> search_vector_db -> build_prompt
    graph.add_edge("embed_query", "search_vector_db")
    graph.add_edge("search_vector_db", "build_prompt")
    #build_prompt -> call_llm -> save_result
    graph.add_edge("build_prompt", "call_llm")
    graph.add_edge("call_llm", "save_result")
    # save_result -> respond_to_slack-> end
    graph.add_edge("save_result", "respond_to_slack")
    graph.add_edge("respond_to_slack", END)

    return graph.compile()