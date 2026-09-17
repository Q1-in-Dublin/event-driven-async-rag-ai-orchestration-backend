import hashlib
import random

EMBEDDING_DIM = 1536

def generate_embedding(text:str)-> list[float]:
    #ponytail : mock embedding, no real semantic meaning - swap for
    # a real embedding model(Vertex AI) once credentials are available
    seed = int(hashlib.sha256(text.encode()).hexdigest(),16)
    rng = random.Random(seed)
    return [rng.uniform(-1,1) for _ in range(EMBEDDING_DIM)]