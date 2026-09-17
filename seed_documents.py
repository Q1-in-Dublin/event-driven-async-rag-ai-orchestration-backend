"""
seed_documents.py

sample_documents.json을 읽어 embedding을 생성하고 pgvector의 documents 테이블에 적재합니다.
기술 설계 문서의 documents 테이블 스키마(id, content, embedding, metadata)를 따릅니다.

사용법:
    python seed_documents.py
"""

import json
import uuid
from pathlib import Path

# 프로젝트의 rag/embedding.py, db/session.py를 사용한다고 가정
# from app.rag.embedding import generate_embedding
# from app.db.session import get_db_session

SEED_FILE = Path(__file__).parent / "seed_documents.json"


def load_seed_documents() -> list[dict]:
    with open(SEED_FILE, encoding="utf-8") as f:
        return json.load(f)


def seed():
    documents = load_seed_documents()
    print(f"{len(documents)} loaded documents in pgvector...")

    for doc in documents:
        # embedding = generate_embedding(doc["content"])  # 실제 embedding 모델 호출
        embedding = [0.0] * 1536  # placeholder — 실제 구현 시 embedding.py 연결 필요

        # db.execute(
        #     "INSERT INTO documents (id, content, embedding, metadata) VALUES (%s, %s, %s, %s)",
        #     (str(uuid.uuid4()), doc["content"], embedding, json.dumps(doc["metadata"])),
        # )
        print(f"  - [{doc['metadata']['category']}] {doc['id']} 적재 완료 (임시: DB insert 미연결)")

    print("시드 데이터 적재 완료.")


if __name__ == "__main__":
    seed()
