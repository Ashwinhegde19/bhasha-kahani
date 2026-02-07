import uuid
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class AudioFile(Base):
    __tablename__ = "audio_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("story_nodes.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False)
    code_mix_ratio = Column(Numeric(3, 2), default=0.00)
    speaker_id = Column(String(50), nullable=False)
    r2_url = Column(String(500), nullable=False)
    file_size = Column(Integer)
    duration_sec = Column(Numeric(6, 2))
    checksum = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accessed_at = Column(DateTime(timezone=True))
    access_count = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('node_id', 'language_code', 'code_mix_ratio', 'speaker_id', 
                        name='uq_audio_variant'),
    )
