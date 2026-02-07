# Bhasha Kahani - Database Schema

## 📊 Database Overview

This document describes the complete database schema for Bhasha Kahani using PostgreSQL with SQLAlchemy ORM.

---

## 🗄️ Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE SCHEMA                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │    stories      │       │   characters    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ anonymous_id    │       │ slug (UQ)       │       │ story_id (FK)   │
│ created_at      │       │ age_range       │       │ slug            │
│ last_active     │       │ region          │       │ name            │
│ preferences     │       │ moral           │       │ voice_profile   │
│ metadata        │       │ duration_min    │       │ bulbul_speaker  │
└────────┬────────┘       │ cover_image     │       │ description     │
         │               │ is_active       │       │ display_order   │
         │               │ created_at      │       └────────┬────────┘
         │               │ updated_at      │                │
         │               └────────┬────────┘                │
         │                        │                         │
         │                        │                         │
         │                        ▼                         │
         │               ┌─────────────────┐                │
         │               │ story_translations│               │
         │               ├─────────────────┤                │
         │               │ id (PK)         │                │
         │               │ story_id (FK)   │                │
         │               │ language_code   │                │
         │               │ title           │                │
         │               │ description     │                │
         │               │ content_json    │◄───────────────┘
         │               │ is_complete     │
         │               └─────────────────┘
         │
         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  user_progress  │       │  story_nodes    │       │  story_choices  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │       │ story_id (FK)   │       │ node_id (FK)    │
│ story_id (FK)   │       │ node_type       │       │ choice_key      │
│ current_node_id │       │ character_id(FK)│       │ text            │
│ choices_made    │       │ display_order   │       │ next_node_id    │
│ is_completed    │       │ is_start        │       │ is_default      │
│ completion_pct  │       │ is_end          │       │ metadata        │
│ last_played     │       │ metadata        │       └─────────────────┘
│ created_at      │       └─────────────────┘
│ updated_at      │
└─────────────────┘
         │
         │
         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  bookmarks      │       │  audio_files    │       │  analytics      │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │       │ node_id (FK)    │       │ user_id (FK)    │
│ story_id (FK)   │       │ language_code   │       │ story_id (FK)   │
│ created_at      │       │ code_mix_ratio  │       │ event_type      │
│ notes           │       │ speaker_id      │       │ event_data      │
└─────────────────┘       │ r2_url          │       │ session_id      │
                          │ file_size       │       │ created_at      │
                          │ duration_sec    │       │ ip_address      │
                          │ checksum        │       │ user_agent      │
                          │ created_at      │       └─────────────────┘
                          │ accessed_at     │
                          │ access_count    │
                          └─────────────────┘
```

---

## 📋 Table Definitions

### 1. Users Table

Stores anonymous and authenticated users.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anonymous_id VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW(),
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_users_anonymous_id ON users(anonymous_id);
CREATE INDEX idx_users_last_active ON users(last_active);
```

**SQLAlchemy Model:**

```python
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anonymous_id = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    preferences = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)
```

---

### 2. Stories Table

Master table for stories.

```sql
CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    age_range VARCHAR(20) NOT NULL, -- '4-6', '7-10', etc.
    region VARCHAR(50) NOT NULL, -- 'pan-indian', 'bengali', 'tamil', etc.
    moral TEXT,
    duration_min INTEGER,
    cover_image VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stories_slug ON stories(slug);
CREATE INDEX idx_stories_age_range ON stories(age_range);
CREATE INDEX idx_stories_region ON stories(region);
CREATE INDEX idx_stories_active ON stories(is_active) WHERE is_active = TRUE;
```

**SQLAlchemy Model:**

```python
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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    translations = relationship("StoryTranslation", back_populates="story", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="story", cascade="all, delete-orphan")
    nodes = relationship("StoryNode", back_populates="story", cascade="all, delete-orphan")
```

---

### 3. Story Translations Table

Localized content for stories.

```sql
CREATE TABLE story_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL, -- 'hi', 'ta', 'bn', 'hi-mixed', etc.
    title VARCHAR(200) NOT NULL,
    description TEXT,
    content_json JSONB NOT NULL, -- Full story structure
    is_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(story_id, language_code)
);

CREATE INDEX idx_story_translations_story ON story_translations(story_id);
CREATE INDEX idx_story_translations_lang ON story_translations(language_code);
```

**SQLAlchemy Model:**

```python
class StoryTranslation(Base):
    __tablename__ = "story_translations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content_json = Column(JSON, nullable=False)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('story_id', 'language_code', name='uq_story_language'),
    )
    
    # Relationships
    story = relationship("Story", back_populates="translations")
```

---

### 4. Characters Table

Story characters with voice profiles.

```sql
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    slug VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    voice_profile VARCHAR(50) NOT NULL,
    bulbul_speaker VARCHAR(50) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    avatar_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_characters_story ON characters(story_id);
CREATE INDEX idx_characters_speaker ON characters(bulbul_speaker);
```

**SQLAlchemy Model:**

```python
class Character(Base):
    __tablename__ = "characters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    voice_profile = Column(String(50), nullable=False)
    bulbul_speaker = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    avatar_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    story = relationship("Story", back_populates="characters")
    nodes = relationship("StoryNode", back_populates="character")
```

---

### 5. Story Nodes Table

Individual story segments (narration, dialogue, choices).

```sql
CREATE TABLE story_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    node_type VARCHAR(20) NOT NULL, -- 'narration', 'dialogue', 'choice', 'end'
    character_id UUID REFERENCES characters(id) ON DELETE SET NULL,
    display_order INTEGER NOT NULL,
    is_start BOOLEAN DEFAULT FALSE,
    is_end BOOLEAN DEFAULT FALSE,
    text_content JSONB NOT NULL, -- { "hi": "...", "ta": "...", "bn": "..." }
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_story_nodes_story ON story_nodes(story_id);
CREATE INDEX idx_story_nodes_type ON story_nodes(node_type);
CREATE INDEX idx_story_nodes_order ON story_nodes(story_id, display_order);
CREATE INDEX idx_story_nodes_start ON story_nodes(story_id, is_start) WHERE is_start = TRUE;
```

**SQLAlchemy Model:**

```python
class StoryNode(Base):
    __tablename__ = "story_nodes"
    
    NODE_TYPES = ['narration', 'dialogue', 'choice', 'end']
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    node_type = Column(String(20), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="SET NULL"))
    display_order = Column(Integer, nullable=False)
    is_start = Column(Boolean, default=False)
    is_end = Column(Boolean, default=False)
    text_content = Column(JSON, nullable=False)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    story = relationship("Story", back_populates="nodes")
    character = relationship("Character", back_populates="nodes")
    choices = relationship("StoryChoice", back_populates="node", cascade="all, delete-orphan")
```

---

### 6. Story Choices Table

Choice options for choice-type nodes.

```sql
CREATE TABLE story_choices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL REFERENCES story_nodes(id) ON DELETE CASCADE,
    choice_key VARCHAR(10) NOT NULL, -- 'A', 'B', 'C'
    text_content JSONB NOT NULL, -- { "hi": "...", "ta": "..." }
    next_node_id UUID REFERENCES story_nodes(id) ON DELETE SET NULL,
    is_default BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(node_id, choice_key)
);

CREATE INDEX idx_story_choices_node ON story_choices(node_id);
CREATE INDEX idx_story_choices_next ON story_choices(next_node_id);
```

**SQLAlchemy Model:**

```python
class StoryChoice(Base):
    __tablename__ = "story_choices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("story_nodes.id", ondelete="CASCADE"), nullable=False)
    choice_key = Column(String(10), nullable=False)
    text_content = Column(JSON, nullable=False)
    next_node_id = Column(UUID(as_uuid=True), ForeignKey("story_nodes.id", ondelete="SET NULL"))
    is_default = Column(Boolean, default=False)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('node_id', 'choice_key', name='uq_node_choice'),
    )
    
    # Relationships
    node = relationship("StoryNode", back_populates="choices", foreign_keys=[node_id])
    next_node = relationship("StoryNode", foreign_keys=[next_node_id])
```

---

### 7. Audio Files Table

Generated audio file metadata.

```sql
CREATE TABLE audio_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL REFERENCES story_nodes(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    code_mix_ratio DECIMAL(3,2) DEFAULT 0.00, -- 0.00 to 1.00
    speaker_id VARCHAR(50) NOT NULL,
    r2_url VARCHAR(500) NOT NULL,
    file_size INTEGER, -- bytes
    duration_sec DECIMAL(6,2),
    checksum VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    accessed_at TIMESTAMPTZ,
    access_count INTEGER DEFAULT 0,
    UNIQUE(node_id, language_code, code_mix_ratio, speaker_id)
);

CREATE INDEX idx_audio_files_node ON audio_files(node_id);
CREATE INDEX idx_audio_files_lang ON audio_files(language_code);
CREATE INDEX idx_audio_files_speaker ON audio_files(speaker_id);
CREATE INDEX idx_audio_files_accessed ON audio_files(accessed_at);
```

**SQLAlchemy Model:**

```python
class AudioFile(Base):
    __tablename__ = "audio_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("story_nodes.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False)
    code_mix_ratio = Column(DECIMAL(3, 2), default=0.00)
    speaker_id = Column(String(50), nullable=False)
    r2_url = Column(String(500), nullable=False)
    file_size = Column(Integer)
    duration_sec = Column(DECIMAL(6, 2))
    checksum = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accessed_at = Column(DateTime(timezone=True))
    access_count = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('node_id', 'language_code', 'code_mix_ratio', 'speaker_id', 
                        name='uq_audio_variant'),
    )
```

---

### 8. User Progress Table

Tracks user story progress.

```sql
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    current_node_id UUID REFERENCES story_nodes(id) ON DELETE SET NULL,
    choices_made JSONB DEFAULT '[]', -- [{ "node_id": "...", "choice": "A" }]
    is_completed BOOLEAN DEFAULT FALSE,
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    play_count INTEGER DEFAULT 0,
    total_time_sec INTEGER DEFAULT 0,
    last_played_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, story_id)
);

CREATE INDEX idx_user_progress_user ON user_progress(user_id);
CREATE INDEX idx_user_progress_story ON user_progress(story_id);
CREATE INDEX idx_user_progress_completed ON user_progress(user_id, is_completed) WHERE is_completed = TRUE;
```

**SQLAlchemy Model:**

```python
class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    current_node_id = Column(UUID(as_uuid=True), ForeignKey("story_nodes.id", ondelete="SET NULL"))
    choices_made = Column(JSON, default=list)
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(DECIMAL(5, 2), default=0.00)
    play_count = Column(Integer, default=0)
    total_time_sec = Column(Integer, default=0)
    last_played_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'story_id', name='uq_user_story_progress'),
    )
```

---

### 9. Bookmarks Table

User bookmarked stories.

```sql
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, story_id)
);

CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);
CREATE INDEX idx_bookmarks_story ON bookmarks(story_id);
```

**SQLAlchemy Model:**

```python
class Bookmark(Base):
    __tablename__ = "bookmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'story_id', name='uq_user_bookmark'),
    )
```

---

### 10. Analytics Events Table

Event tracking for analytics.

```sql
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    story_id UUID REFERENCES stories(id) ON DELETE SET NULL,
    node_id UUID REFERENCES story_nodes(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL, -- 'story_start', 'choice_made', 'audio_play', etc.
    event_data JSONB DEFAULT '{}',
    session_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_analytics_user ON analytics_events(user_id);
CREATE INDEX idx_analytics_story ON analytics_events(story_id);
CREATE INDEX idx_analytics_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_created ON analytics_events(created_at);
CREATE INDEX idx_analytics_session ON analytics_events(session_id);
```

**SQLAlchemy Model:**

```python
class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    EVENT_TYPES = [
        'page_view', 'story_start', 'story_complete', 
        'choice_made', 'audio_play', 'audio_pause',
        'language_change', 'bookmark_add', 'bookmark_remove'
    ]
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="SET NULL"))
    node_id = Column(UUID(as_uuid=True), ForeignKey("story_nodes.id", ondelete="SET NULL"))
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON, default=dict)
    session_id = Column(String(100), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(INET)
    user_agent = Column(Text)
```

---

## 🔗 Relationships Summary

```python
# Complete relationship mapping

Story
├── translations: StoryTranslation[]
├── characters: Character[]
├── nodes: StoryNode[]

StoryTranslation
└── story: Story

Character
├── story: Story
└── nodes: StoryNode[]

StoryNode
├── story: Story
├── character: Character (optional)
└── choices: StoryChoice[]

StoryChoice
├── node: StoryNode
└── next_node: StoryNode (optional)

User
├── progress: UserProgress[]
└── bookmarks: Bookmark[]

UserProgress
├── user: User
├── story: Story
└── current_node: StoryNode (optional)

Bookmark
├── user: User
└── story: Story

AudioFile
└── node: StoryNode

AnalyticsEvent
├── user: User (optional)
├── story: Story (optional)
└── node: StoryNode (optional)
```

---

## 📊 Indexes Summary

| Table | Index Name | Columns | Type |
|-------|------------|---------|------|
| users | idx_users_anonymous_id | anonymous_id | B-tree |
| users | idx_users_last_active | last_active | B-tree |
| stories | idx_stories_slug | slug | B-tree, unique |
| stories | idx_stories_age_range | age_range | B-tree |
| stories | idx_stories_active | is_active | Partial |
| story_translations | idx_story_translations_story | story_id | B-tree |
| story_translations | idx_story_translations_lang | language_code | B-tree |
| characters | idx_characters_story | story_id | B-tree |
| characters | idx_characters_speaker | bulbul_speaker | B-tree |
| story_nodes | idx_story_nodes_story | story_id | B-tree |
| story_nodes | idx_story_nodes_order | story_id, display_order | B-tree |
| story_nodes | idx_story_nodes_start | story_id, is_start | Partial |
| story_choices | idx_story_choices_node | node_id | B-tree |
| story_choices | idx_story_choices_next | next_node_id | B-tree |
| audio_files | idx_audio_files_node | node_id | B-tree |
| audio_files | idx_audio_files_lang | language_code | B-tree |
| user_progress | idx_user_progress_user | user_id | B-tree |
| user_progress | idx_user_progress_completed | user_id, is_completed | Partial |
| analytics_events | idx_analytics_created | created_at | B-tree |
| analytics_events | idx_analytics_type | event_type | B-tree |

---

## 🔄 Database Migrations (Alembic)

```python
# alembic/env.py
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.models import Base  # Import all models

config = context.config
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

### Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "add_user_preferences"

# Run migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current version
alembic current
```

---

## 💾 Sample Data

```sql
-- Insert sample story
INSERT INTO stories (slug, age_range, region, moral, duration_min, cover_image)
VALUES (
    'clever-crow',
    '4-8',
    'pan-indian',
    'Intelligence and persistence solve problems',
    4,
    'https://cdn.bhashakahani.com/stories/clever-crow/cover.jpg'
);

-- Insert translations
INSERT INTO story_translations (story_id, language_code, title, description, content_json, is_complete)
VALUES (
    (SELECT id FROM stories WHERE slug = 'clever-crow'),
    'hi',
    'चालाक कौआ',
    'Ek clever crow ki kahani',
    '{
        "nodes": [
            {"id": "intro", "type": "narration", "text": "Bacchon, aaj main tumhe sunata hoon..."},
            {"id": "scene1", "type": "narration", "text": "Ek bahut garam din tha..."}
        ]
    }'::jsonb,
    TRUE
);

-- Insert characters
INSERT INTO characters (story_id, slug, name, voice_profile, bulbul_speaker, display_order)
VALUES 
    ((SELECT id FROM stories WHERE slug = 'clever-crow'), 'narrator', 'Dadi', 'warm_elderly', 'meera', 1),
    ((SELECT id FROM stories WHERE slug = 'clever-crow'), 'crow', 'Kauwa', 'young_energetic', 'arvind', 2);
```

---

## 📈 Database Scaling Considerations

### Partitioning Strategy (Post-MVP)

```sql
-- Partition analytics_events by month
CREATE TABLE analytics_events_2024_01 PARTITION OF analytics_events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Automated partition creation
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
BEGIN
    -- Create next month's partition
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS analytics_events_%s PARTITION OF analytics_events
         FOR VALUES FROM (%L) TO (%L)',
        to_char(NOW() + INTERVAL '1 month', 'YYYY_MM'),
        DATE_TRUNC('month', NOW() + INTERVAL '1 month'),
        DATE_TRUNC('month', NOW() + INTERVAL '2 months')
    );
END;
$$ LANGUAGE plpgsql;
```

### Read Replicas

```yaml
# For high read scenarios
primary_db:
  url: ${DATABASE_URL}
  
read_replicas:
  - url: ${DATABASE_REPLICA_1_URL}
  - url: ${DATABASE_REPLICA_2_URL}
```

---

**Version:** 1.0  
**Last Updated:** February 7, 2026
