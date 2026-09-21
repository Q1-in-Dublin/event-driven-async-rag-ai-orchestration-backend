from sqlalchemy.orm import Session

from app.db.models import Document

# ponytail: cosine_distance ranges 0 (identical) to 2 (opposite);
# tune this if real queries start missing relevant docs or pulling unrelated ones
DISTANCE_THRESHOLD = 0.45


def search_similar_documents(db: Session, query_embedding: list[float], top_k: int = 3) -> list[Document]:
    distance = Document.embedding.cosine_distance(query_embedding)
    results = (
        db.query(Document, distance.label("distance"))
        .order_by(distance)
        .limit(top_k)
        .all()
    )
    return [doc for doc, dist in results if dist <= DISTANCE_THRESHOLD]
