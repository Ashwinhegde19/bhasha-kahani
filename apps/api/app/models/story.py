import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    Boolean,
    Integer,
    Text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Story(Base):
    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    age_range = Column(String(20), nullable=False, index=True)
    region = Column(String(50), nullable=False, index=True)
    moral = Column(Text)
    duration_min = Column(Integer)
    cover_image = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    translations = relationship(
        "StoryTranslation", back_populates="story", cascade="all, delete-orphan"
    )
    characters = relationship(
        "Character", back_populates="story", cascade="all, delete-orphan"
    )
    nodes = relationship(
        "StoryNode", back_populates="story", cascade="all, delete-orphan"
    )


class StoryTranslation(Base):
    __tablename__ = "story_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(
        UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False
    )
    language_code = Column(String(10), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content_json = Column(JSON, nullable=False, default=dict)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("story_id", "language_code", name="uq_story_language"),
    )

    story = relationship("Story", back_populates="translations")


class Character(Base):
    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(
        UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False
    )
    slug = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    voice_profile = Column(String(50), nullable=False)
    bulbul_speaker = Column(String(50), nullable=False, index=True)
    name_translations = Column(
        JSON, default=dict
    )  # {"en": "Dadi", "hi": "दादी", "kn": "ಅಜ್ಜಿ"}
    description = Column(Text)
    display_order = Column(Integer, default=0)
    avatar_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    story = relationship("Story", back_populates="characters")
    nodes = relationship("StoryNode", back_populates="character")


class StoryNode(Base):
    __tablename__ = "story_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(
        UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False
    )
    node_type = Column(String(20), nullable=False)  # narration, dialogue, choice, end
    character_id = Column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="SET NULL")
    )
    display_order = Column(Integer, nullable=False)
    is_start = Column(Boolean, default=False)
    is_end = Column(Boolean, default=False)
    text_content = Column(
        JSON, nullable=False, default=dict
    )  # {"en": "...", "hi": "...", "kn": "..."}
    node_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    story = relationship("Story", back_populates="nodes")
    character = relationship("Character", back_populates="nodes")
    choices = relationship(
        "StoryChoice",
        back_populates="node",
        foreign_keys="StoryChoice.node_id",
        cascade="all, delete-orphan",
    )


class StoryChoice(Base):
    __tablename__ = "story_choices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(
        UUID(as_uuid=True),
        ForeignKey("story_nodes.id", ondelete="CASCADE"),
        nullable=False,
    )
    choice_key = Column(String(10), nullable=False)  # A, B, C
    text_content = Column(
        JSON, nullable=False, default=dict
    )  # {"en": "...", "hi": "...", "kn": "..."}
    next_node_id = Column(
        UUID(as_uuid=True), ForeignKey("story_nodes.id", ondelete="SET NULL")
    )
    is_default = Column(Boolean, default=False)
    node_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("node_id", "choice_key", name="uq_node_choice"),)

    node = relationship("StoryNode", back_populates="choices", foreign_keys=[node_id])
    next_node = relationship("StoryNode", foreign_keys=[next_node_id])
