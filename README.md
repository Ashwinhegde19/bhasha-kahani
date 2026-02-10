# Bhasha Kahani

**Interactive multilingual folktale storytelling platform for children**

Bhasha Kahani brings traditional Indian folktales to life with high-quality AI-powered audio narration in multiple languages. Children can listen to stories with unique character voices, making storytelling an immersive experience.

## Features

- **Multilingual Support** - Stories available in English, Hindi, and Kannada
- **AI-Powered Audio** - High-quality text-to-speech using Sarvam AI's Bulbul V3
- **Character Voices** - Each character has a unique voice for immersive storytelling
- **Whimsical UI** - Kid-friendly design with playful animations and decorations
- **Progress Tracking** - Resume stories where you left off
- **Offline Support** - PWA support for listening without internet
- **Responsive Design** - Works beautifully on mobile, tablet, and desktop

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS 4 |
| UI Components | shadcn/ui, Radix UI, Lucide Icons |
| State Management | Zustand, TanStack Query |
| Backend | FastAPI (Python 3.10+) |
| Database | PostgreSQL |
| Audio Storage | Cloudflare R2 |
| Caching | Redis (Upstash) |
| TTS Engine | Sarvam AI Bulbul V3 |
| Hosting | Vercel (Frontend) + Railway (Backend) |

## Project Structure

```
bhasha-kahani/
├── apps/
│   ├── web/my-app/          # Next.js frontend
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── lib/             # Utilities & API client
│   │   ├── store/           # Zustand stores
│   │   └── types/           # TypeScript types
│   │
│   └── api/                 # FastAPI backend
│       ├── app/
│       │   ├── routers/     # API endpoints
│       │   ├── services/    # Business logic
│       │   ├── models/      # Database models
│       │   └── schemas/     # Pydantic schemas
│       ├── alembic/         # Database migrations
│       └── tests/           # Test suite
│
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Redis (optional for local dev)

### Run Both Services

```bash
./start-dev.sh
```

This starts:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Run Services Separately

**Terminal 1 - Backend:**
```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Configure your env vars
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd apps/web/my-app
npm install
# Create .env.local file (see Environment Variables section)
npm run dev
```

## Environment Variables

### Backend (`apps/api/.env`)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/bhashakahani
REDIS_URL=redis://localhost:6379
SARVAM_API_KEY=your_sarvam_api_key
SECRET_KEY=your-secret-key
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=bhashakahani-audio
R2_PUBLIC_URL=https://your-bucket.r2.dev
```

### Frontend (`apps/web/my-app/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUDIO_CDN=https://audio.bhashakahani.com
```

## Available Scripts

### Frontend

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Backend

```bash
uvicorn app.main:app --reload              # Development server
alembic upgrade head                        # Run migrations
alembic revision --autogenerate -m "msg"   # Create migration
pytest                                      # Run tests
```

## API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /stories` | List all stories |
| `GET /stories/{slug}` | Get story details |
| `GET /audio/{node_id}` | Get audio for a story node |
| `POST /audio/story/{story_id}/pre-generate` | Pre-generate audio for a story |
| `POST /choices/{slug}/choices` | Submit a story choice |
| `GET /users/progress` | Get user progress |
| `POST /users/progress` | Save user progress |

## Deployment

### Frontend (Vercel)

```bash
npm install -g vercel
vercel --prod
```

### Backend (Railway)

```bash
npm install -g @railway/cli
railway login
railway up
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- [Architecture](./ARCHITECTURE.md) - System architecture and data flows
- [API Specification](./API_SPEC.md) - API endpoints and schemas
- [Database Schema](./DATABASE.md) - Database models and relationships
- [Frontend Guide](./FRONTEND.md) - Frontend architecture and components
- [Setup Guide](./SETUP.md) - Detailed setup instructions
- [Technical Spec](./TECH_SPEC.md) - Complete technical specification

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Sarvam AI](https://sarvam.ai/) for the Bulbul TTS API
- [shadcn/ui](https://ui.shadcn.com/) for beautiful UI components
- [Lucide](https://lucide.dev/) for icons
