"""
RAG retrieval accuracy check against the 6 seeded HR policy documents.

Each case maps a natural-language question to the document category that
should be retrieved. Requires seed_documents.py to have been run against
a live DB with real embeddings (not the old mock).
"""

import pytest

from app.db.session import SessionLocal
from app.rag.embedding import generate_embedding
from app.rag.vector_search import search_similar_documents

CASES = [
    ("휴가는 1년에 며칠 쓸 수 있어?", "vacation"),
    ("회사 노트북 보안 규정이 어떻게 돼?", "security"),
    ("재택근무 며칠까지 가능해?", "remote_work"),
    ("헬스장 지원비 얼마야?", "benefits"),
    ("출장 숙소비 한도가 얼마야?", "expenses"),
    ("괴롭힘 신고는 어디로 해?", "code_of_conduct"),
]

# Unrelated small talk should retrieve nothing above the distance threshold
NEGATIVE_CASES = [
    "오늘 날씨 어때?",
    "점심 뭐 먹지",
]


@pytest.mark.parametrize("question,expected_category", CASES)
def test_retrieves_expected_category(question, expected_category):
    db = SessionLocal()
    try:
        embedding = generate_embedding(question, task_type="RETRIEVAL_QUERY")
        docs = search_similar_documents(db, embedding, top_k=3)
        categories = [d.doc_metadata.get("category") for d in docs]
        assert expected_category in categories, (
            f"Q: {question!r} expected {expected_category!r} in top-3, got {categories}"
        )
    finally:
        db.close()


@pytest.mark.parametrize("question", NEGATIVE_CASES)
def test_unrelated_question_returns_no_docs(question):
    db = SessionLocal()
    try:
        embedding = generate_embedding(question, task_type="RETRIEVAL_QUERY")
        docs = search_similar_documents(db, embedding, top_k=3)
        assert docs == [], f"Q: {question!r} unexpectedly matched {len(docs)} doc(s)"
    finally:
        db.close()
