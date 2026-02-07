# Bhasha Kahani - API Specification

## 📡 API Overview

This document describes the complete REST API for Bhasha Kahani built with FastAPI.

**Base URL:** `https://api.bhashakahani.com/v1`

---

## 🔐 Authentication

### Anonymous Authentication

All endpoints support anonymous authentication using a generated JWT token.

```http
POST /auth/anonymous
Content-Type: application/json

{
  "client_id": "optional-client-identifier"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Using the Token

```http
GET /stories
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📚 Endpoints

### 1. Stories API

#### List Stories

```http
GET /stories
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| language | string | No | Filter by language (hi, ta, bn) |
| age_range | string | No | Filter by age (4-6, 7-10, 11-14) |
| region | string | No | Filter by region |
| search | string | No | Search in title/description |
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 20, max: 100) |

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "slug": "clever-crow",
      "title": "चालाक कौआ",
      "description": "Ek clever crow ki kahani",
      "language": "hi",
      "age_range": "4-8",
      "region": "pan-indian",
      "moral": "Intelligence and persistence solve problems",
      "duration_min": 4,
      "cover_image": "https://cdn.bhashakahani.com/stories/clever-crow/cover.jpg",
      "character_count": 3,
      "choice_count": 2,
      "is_completed_translation": true,
      "created_at": "2026-02-07T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 3,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

#### Get Story Details

```http
GET /stories/{slug}
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| slug | string | Story unique identifier |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| language | string | No | Language code (default: hi) |
| include_nodes | boolean | No | Include full story structure |

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "slug": "clever-crow",
  "title": "चालाक कौआ",
  "description": "Ek clever crow ki kahani",
  "language": "hi",
  "age_range": "4-8",
  "region": "pan-indian",
  "moral": "Intelligence and persistence solve problems",
  "duration_min": 4,
  "cover_image": "https://cdn.bhashakahani.com/stories/clever-crow/cover.jpg",
  "available_languages": ["hi", "ta", "bn", "hi-mixed"],
  "characters": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "slug": "narrator",
      "name": "Dadi",
      "voice_profile": "warm_elderly",
      "bulbul_speaker": "meera",
      "avatar_url": "https://cdn.bhashakahani.com/characters/dadi.png"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "slug": "crow",
      "name": "Kauwa",
      "voice_profile": "young_energetic",
      "bulbul_speaker": "arvind",
      "avatar_url": "https://cdn.bhashakahani.com/characters/crow.png"
    }
  ],
  "nodes": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440001",
      "node_type": "narration",
      "character_id": "660e8400-e29b-41d4-a716-446655440001",
      "display_order": 1,
      "is_start": true,
      "is_end": false,
      "text": "Bacchon, aaj main tumhe sunata hoon ek clever crow ki kahani...",
      "audio_url": "https://audio.bhashakahani.com/hi/clever-crow/node-1-meera.mp3",
      "duration_sec": 15.5
    }
  ],
  "start_node_id": "770e8400-e29b-41d4-a716-446655440001",
  "created_at": "2026-02-07T10:00:00Z",
  "updated_at": "2026-02-07T10:00:00Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": {
    "code": "STORY_NOT_FOUND",
    "message": "Story with slug 'unknown-story' not found",
    "details": {}
  }
}
```

---

#### Get Story Node

```http
GET /stories/{slug}/nodes/{node_id}
```

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440005",
  "node_type": "choice",
  "character_id": "660e8400-e29b-41d4-a716-446655440001",
  "display_order": 5,
  "is_start": false,
  "is_end": false,
  "text": "Crow ne dekha ek pot with thoda sa paani. Tumhe kya lagta hai?",
  "audio_url": "https://audio.bhashakahani.com/hi/clever-crow/node-5-meera.mp3",
  "duration_sec": 12.3,
  "choices": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440001",
      "choice_key": "A",
      "text": "Drop stones in the pot",
      "next_node_id": "770e8400-e29b-41d4-a716-446655440006",
      "is_default": false
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440002",
      "choice_key": "B",
      "text": "Try to break the pot",
      "next_node_id": "770e8400-e29b-41d4-a716-446655440007",
      "is_default": false
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "choice_key": "C",
      "text": "Ask other birds for help",
      "next_node_id": "770e8400-e29b-41d4-a716-446655440008",
      "is_default": false
    }
  ]
}
```

---

### 2. Audio API

#### Get Audio URL

```http
GET /audio/{node_id}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| language | string | Yes | Language code (hi, ta, bn) |
| speaker | string | No | Bulbul speaker ID (default: auto-select) |
| code_mix | float | No | Code-mix ratio 0.0-1.0 (default: 0.0) |

**Response (200 OK):**
```json
{
  "node_id": "770e8400-e29b-41d4-a716-446655440001",
  "language": "hi",
  "code_mix_ratio": 0.3,
  "speaker": "meera",
  "audio_url": "https://audio.bhashakahani.com/hi/clever-crow/node-1-meera-mixed-30.mp3",
  "duration_sec": 15.5,
  "file_size": 248000,
  "is_cached": true,
  "expires_at": "2026-03-07T10:00:00Z"
}
```

**Response (202 Accepted - Generating):**
```json
{
  "node_id": "770e8400-e29b-41d4-a716-446655440001",
  "language": "hi",
  "status": "generating",
  "estimated_wait_sec": 5,
  "retry_after": 5
}
```

---

#### Generate Audio (Admin)

```http
POST /audio/generate
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "node_id": "770e8400-e29b-41d4-a716-446655440001",
  "language": "hi",
  "speaker": "meera",
  "code_mix_ratio": 0.3
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "990e8400-e29b-41d4-a716-446655440001",
  "status": "queued",
  "estimated_duration_sec": 10
}
```

---

#### Bulk Generate Audio (Admin)

```http
POST /audio/generate/bulk
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "story_id": "550e8400-e29b-41d4-a716-446655440000",
  "languages": ["hi", "ta", "bn"],
  "code_mix_ratios": [0.0, 0.3, 0.5]
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "990e8400-e29b-41d4-a716-446655440002",
  "total_nodes": 15,
  "total_variants": 135,
  "status": "queued"
}
```

---

### 3. Choices API

#### Make a Choice

```http
POST /stories/{slug}/choices
Content-Type: application/json

{
  "node_id": "770e8400-e29b-41d4-a716-446655440005",
  "choice_key": "A"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "choice_made": {
    "node_id": "770e8400-e29b-41d4-a716-446655440005",
    "choice_key": "A",
    "choice_text": "Drop stones in the pot"
  },
  "next_node": {
    "id": "770e8400-e29b-41d4-a716-446655440006",
    "node_type": "narration",
    "character_id": "660e8400-e29b-41d4-a716-446655440001",
    "text": "Bahut accha socha! Crow ne cleverly stones drop kiye...",
    "audio_url": "https://audio.bhashakahani.com/hi/clever-crow/node-6-meera.mp3",
    "duration_sec": 18.2,
    "is_end": false
  },
  "progress": {
    "completion_percentage": 65.5,
    "choices_made_count": 1
  }
}
```

---

### 4. User Progress API

#### Get User Progress

```http
GET /users/progress
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "story_id": "550e8400-e29b-41d4-a716-446655440000",
      "story_slug": "clever-crow",
      "story_title": "चालाक कौआ",
      "cover_image": "https://cdn.bhashakahani.com/stories/clever-crow/cover.jpg",
      "current_node_id": "770e8400-e29b-41d4-a716-446655440006",
      "is_completed": false,
      "completion_percentage": 65.5,
      "play_count": 2,
      "total_time_sec": 320,
      "last_played_at": "2026-02-07T14:30:00Z",
      "choices_made": [
        {
          "node_id": "770e8400-e29b-41d4-a716-446655440005",
          "choice_key": "A",
          "made_at": "2026-02-07T14:25:00Z"
        }
      ]
    }
  ],
  "summary": {
    "total_stories_started": 3,
    "total_stories_completed": 1,
    "total_time_minutes": 45
  }
}
```

---

#### Update Progress

```http
POST /users/progress
Content-Type: application/json

{
  "story_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_node_id": "770e8400-e29b-41d4-a716-446655440006",
  "is_completed": false,
  "time_spent_sec": 120
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "progress": {
    "story_id": "550e8400-e29b-41d4-a716-446655440000",
    "completion_percentage": 65.5,
    "total_time_sec": 440,
    "updated_at": "2026-02-07T14:32:00Z"
  }
}
```

---

#### Complete Story

```http
POST /users/progress/complete
Content-Type: application/json

{
  "story_id": "550e8400-e29b-41d4-a716-446655440000",
  "ending_type": "clever_solution",
  "rating": 5,
  "feedback": "Bahut acchi kahani!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "achievement": {
    "name": "First Story Complete!",
    "badge_url": "https://cdn.bhashakahani.com/badges/first-story.png"
  },
  "next_recommendations": [
    {
      "story_id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "The Kind Woodcutter",
      "reason": "Based on your interest"
    }
  ]
}
```

---

### 5. Bookmarks API

#### List Bookmarks

```http
GET /users/bookmarks
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440001",
      "story_id": "550e8400-e29b-41d4-a716-446655440000",
      "story_slug": "clever-crow",
      "story_title": "चालाक कौआ",
      "cover_image": "https://cdn.bhashakahani.com/stories/clever-crow/cover.jpg",
      "notes": "Favorite story for bedtime",
      "created_at": "2026-02-07T10:00:00Z"
    }
  ]
}
```

---

#### Add Bookmark

```http
POST /users/bookmarks
Content-Type: application/json

{
  "story_id": "550e8400-e29b-41d4-a716-446655440000",
  "notes": "Favorite story for bedtime"
}
```

**Response (201 Created):**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440001",
  "story_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-07T10:00:00Z"
}
```

---

#### Remove Bookmark

```http
DELETE /users/bookmarks/{bookmark_id}
```

**Response (204 No Content)**

---

### 6. Analytics API

#### Track Event

```http
POST /analytics/events
Content-Type: application/json

{
  "event_type": "story_start",
  "story_id": "550e8400-e29b-41d4-a716-446655440000",
  "node_id": "770e8400-e29b-41d4-a716-446655440001",
  "event_data": {
    "language": "hi",
    "code_mix_ratio": 0.3
  },
  "session_id": "session-123456"
}
```

**Response (202 Accepted)**

---

#### Get Story Stats (Admin)

```http
GET /analytics/stories/{slug}/stats
Authorization: Bearer {admin_token}
```

**Response (200 OK):**
```json
{
  "story_id": "550e8400-e29b-41d4-a716-446655440000",
  "story_slug": "clever-crow",
  "total_plays": 1250,
  "unique_players": 890,
  "completion_rate": 0.72,
  "avg_completion_time_min": 4.5,
  "language_breakdown": {
    "hi": 0.45,
    "ta": 0.30,
    "bn": 0.25
  },
  "choice_distribution": {
    "node_770e8400-e29b-41d4-a716-446655440005": {
      "A": 0.55,
      "B": 0.25,
      "C": 0.20
    }
  },
  "daily_stats": [
    {
      "date": "2026-02-06",
      "plays": 45,
      "completions": 32
    }
  ]
}
```

---

### 7. Admin API

#### List All Stories (Admin)

```http
GET /admin/stories
Authorization: Bearer {admin_token}
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "slug": "clever-crow",
      "title": "चालाक कौआ",
      "is_active": true,
      "translation_status": {
        "hi": "complete",
        "ta": "complete",
        "bn": "in_progress"
      },
      "audio_status": {
        "hi": { "generated": 15, "total": 15 },
        "ta": { "generated": 15, "total": 15 },
        "bn": { "generated": 5, "total": 15 }
      },
      "stats": {
        "plays": 1250,
        "completions": 900
      }
    }
  ]
}
```

---

#### Create Story (Admin)

```http
POST /admin/stories
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "slug": "kind-woodcutter",
  "age_range": "5-10",
  "region": "bengali",
  "moral": "Honesty is always rewarded",
  "duration_min": 5,
  "translations": {
    "hi": {
      "title": "ईमानदार लकड़हारा",
      "description": "Ek imandaar lakadhare ki kahani"
    },
    "bn": {
      "title": "সৎ কাঠুরে",
      "description": "Ek saty kataurer golpo"
    }
  },
  "characters": [
    {
      "slug": "narrator",
      "name": "Thakurma",
      "voice_profile": "warm_elderly",
      "bulbul_speaker": "meera"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "slug": "kind-woodcutter",
  "created_at": "2026-02-07T10:00:00Z"
}
```

---

#### Update Story (Admin)

```http
PATCH /admin/stories/{slug}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "is_active": false
}
```

**Response (200 OK)**

---

#### Delete Story (Admin)

```http
DELETE /admin/stories/{slug}
Authorization: Bearer {admin_token}
```

**Response (204 No Content)**

---

## 🔄 WebSocket API (Real-time)

### Connection

```javascript
const ws = new WebSocket('wss://api.bhashakahani.com/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
  }));
};
```

### Events

#### Story Progress Sync

```javascript
// Client -> Server
{
  "type": "progress_update",
  "story_id": "550e8400-e29b-41d4-a716-446655440000",
  "node_id": "770e8400-e29b-41d4-a716-446655440006",
  "timestamp": "2026-02-07T14:30:00Z"
}

// Server -> Client
{
  "type": "progress_synced",
  "completion_percentage": 65.5
}
```

#### Collaborative Mode (Post-MVP)

```javascript
// Join collaborative session
{
  "type": "join_session",
  "session_id": "collab-123",
  "story_id": "550e8400-e29b-41d4-a716-446655440000"
}

// Sync choice across participants
{
  "type": "choice_made",
  "user_id": "...",
  "choice_key": "A",
  "node_id": "..."
}
```

---

## 📊 Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async processing) |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

---

## ⚠️ Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "language": ["Required field"],
      "code_mix": ["Must be between 0 and 1"]
    }
  }
}
```

---

## 📈 Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| General API | 60 requests/minute |
| Audio Generation | 10 requests/minute |
| Analytics Events | 100 events/minute |
| WebSocket | 10 messages/second |

---

## 📚 OpenAPI Schema

FastAPI automatically generates OpenAPI documentation at:

- **Swagger UI:** `https://api.bhashakahani.com/docs`
- **ReDoc:** `https://api.bhashakahani.com/redoc`
- **OpenAPI JSON:** `https://api.bhashakahani.com/openapi.json`

---

**Version:** 1.0  
**Last Updated:** February 7, 2026
