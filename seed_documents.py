"""
seed_documents.py

Reads docs/seed_documents.json, generates embeddings, and loads them into
the pgvector-backed documents table.

Usage:
    python seed_documents.py
"""

import json
from pathlib import Path

from app.db.models import Document
from app.db.session import SessionLocal
from app.rag.embedding import generate_embedding

SEED_FILE = Path(__file__).parent / "docs" / "seed_documents.json"


def load_seed_documents() -> list[dict]:
    with open(SEED_FILE, encoding="utf-8") as f:
        return json.load(f)


def seed():
    documents = load_seed_documents()
    print(f"{len(documents)} documents to load into pgvector...")

    db = SessionLocal()
    try:
        existing_seed_ids = {
            doc.doc_metadata.get("seed_id")
            for doc in db.query(Document).all()
            if doc.doc_metadata
        }
        for doc in documents:
            if doc["id"] in existing_seed_ids:
                print(f"  - [{doc['metadata']['category']}] {doc['id']} already seeded, skipping")
                continue
            embedding = generate_embedding(doc["content"])
            metadata = {**doc["metadata"], "seed_id": doc["id"]}
            db.add(Document(content=doc["content"], embedding=embedding, doc_metadata=metadata))
            print(f"  - [{doc['metadata']['category']}] {doc['id']} queued")
        db.commit()
    finally:
        db.close()

    print("Seeding complete.")


if __name__ == "__main__":
    seed()
