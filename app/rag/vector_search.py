from sqlalchemy.orm import Session

from app.db.models import Document 

def search_similar_documents(db: Session, query_embedding: list[float], top_k: int=3 )-> list[Document]:
     return(
          # top k distance .. DSA 
          db.query(Document)
          .order_by(Document.embedding.cosine_distance(query_embedding))
          .limit(top_k)
          .all()
     )