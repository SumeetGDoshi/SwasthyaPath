# Swasthya Path - Layer 1: Report Intelligence Agent

AI-powered medical report analysis and duplicate detection for Indian healthcare.

![Swasthya Path](https://img.shields.io/badge/Hackathon-2024-emerald)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

Swasthya Path helps Indian patients avoid unnecessary duplicate medical tests by:

- **AI-Powered Analysis**: Upload any medical report (image/PDF) and extract structured data using Claude AI
- **Duplicate Detection**: Automatically detect if you're repeating tests unnecessarily
- **Cost Savings**: See exactly how much money you save by avoiding duplicate tests
- **Health Timeline**: Track all your medical tests in a beautiful chronological view

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 14 + React + TypeScript
- **UI Components**: shadcn/ui + Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **AI**: Claude Sonnet (Anthropic)
- **Deployment**: Vercel (Frontend) + Railway (Backend)

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Supabase account (free tier)
- Anthropic API key

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/swasthyapath.git
cd swasthyapath
```

### 2. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the migration script:

```bash
# Copy the contents of backend/database/migrations.sql
# Paste and run in Supabase SQL Editor
```

3. Create a storage bucket:
   - Go to **Storage** → **New Bucket**
   - Name: `medical-reports`
   - Public: Yes

4. Get your credentials:
   - Go to **Settings** → **API**
   - Copy: `Project URL`, `anon/public key`, `service_role key`

### 3. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example .env
```

Edit `.env` with your credentials:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
CORS_ORIGINS=http://localhost:3000
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

### 4. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/upload-report` | POST | Upload and analyze report |
| `/api/reports/{user_id}` | GET | Get all reports |
| `/api/timeline/{user_id}` | GET | Get test timeline |
| `/api/savings/{user_id}` | GET | Get savings summary |
| `/api/demo/setup` | POST | Set up demo data |

## Demo Flow

1. Open http://localhost:3000
2. Click "Try Demo" to set up demo data
3. Go to "Upload Report"
4. Upload a medical report image
5. See AI analysis results
6. If duplicate detected, see savings alert
7. View timeline with all tests

## Deployment

### Deploy Backend to Railway

1. Create account at [railway.app](https://railway.app)
2. New Project → Deploy from GitHub repo
3. Select `backend` folder as root
4. Add environment variables:
   - `ANTHROPIC_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `CORS_ORIGINS` (your Vercel URL)

### Deploy Frontend to Vercel

1. Create account at [vercel.com](https://vercel.com)
2. Import GitHub repo
3. Select `frontend` folder as root
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` (your Railway URL)

## Project Structure

```
swasthyapath/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── agents/
│   │   └── report_agent.py        # Claude AI integration
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   ├── database/
│   │   ├── supabase_client.py     # Database client
│   │   └── migrations.sql         # SQL schema
│   ├── utils/
│   │   └── image_processing.py    # Image utilities
│   ├── requirements.txt
│   ├── Dockerfile
│   └── railway.toml
├── frontend/
│   ├── src/
│   │   ├── app/                   # Next.js pages
│   │   ├── components/            # React components
│   │   ├── lib/                   # Utilities & API client
│   │   └── types/                 # TypeScript types
│   ├── package.json
│   └── vercel.json
└── README.md
```

## Key Features

### 1. AI Report Analysis

The Claude Vision API extracts:
- Hospital and doctor information
- Test names and values
- Reference ranges
- Normal/abnormal status

### 2. Smart Duplicate Detection

Checks against validity periods:
- HbA1c: 90 days
- Lipid Profile: 180 days
- CBC: 30 days
- X-Ray: 365 days

### 3. Indian Healthcare Context

- Indian test costs (INR)
- Common Indian lab formats
- Hindi/English bilingual support
- Popular hospital chains

## Environment Variables

### Backend

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_KEY` | Supabase service key |
| `CORS_ORIGINS` | Allowed origins |

### Frontend

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL |

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## Known Limitations (MVP)

- Simple user ID authentication (no OAuth)
- Manual report upload (no ABDM integration)
- Basic timeline (no advanced analytics)
- JPEG/PNG/PDF only

## Roadmap

- [ ] Layer 2: VanshRaksha (Family Health Prediction)
- [ ] Layer 3: Population Surge Prediction
- [ ] Layer 4: QuickCare Emergency Response
- [ ] Layer 5: Daily Health Logging

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built for Indian Healthcare Hackathon 2024
- Powered by Anthropic Claude AI
- UI components from shadcn/ui

---

Made with ❤️ for Indian Healthcare


