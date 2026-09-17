import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from app.db.session import Base


class Request(Base):

    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Text, nullable=False)
    channel_id = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="queued")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Result(Base):
    __tablename__ = "results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id"), nullable=False)
    llm_response = Column(Text, nullable=False)
    # can be null
    retreived_doc_ids = Column(ARRAY(UUID(as_uuid=True)), nullable= True)
    created_at = Column(DateTime(timezone=True),server_default=func.now())


class RetryLog(Base):
    __tablename__ = "retry_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id"), nullable= False)
    attempted_number = Column(Integer, nullable=False)
    error_reason = Column(Text, nullable=False)
    attempted_at = Column(DateTime(timezone=True),server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable= False)
    doc_metadata = Column("metadata", JSONB, nullable = True)