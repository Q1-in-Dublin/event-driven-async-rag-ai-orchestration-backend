import os

import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

EMBEDDING_DIM = 768

_model = None


def _get_model() -> TextEmbeddingModel:
    global _model
    if _model is None:
        vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), location="us-central1")
        _model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")
    return _model


def generate_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    # task_type must match how the vector is used: documents are indexed as
    # RETRIEVAL_DOCUMENT, user questions are embedded as RETRIEVAL_QUERY.
    # Mixing them collapses all similarity scores into a narrow, useless range.
    embeddings = _get_model().get_embeddings([TextEmbeddingInput(text, task_type)])
    return embeddings[0].values