from fastapi import FastAPI

from app.db import models
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app  = FastAPI()

@app.get("/health")
def health():
    return {"Status" : "OK"}
