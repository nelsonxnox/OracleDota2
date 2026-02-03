# OracleDota - Dota 2 Match Analysis

A Dota 2 match analyzer that provides insights into your games.

## Features

- 🎮 **Match Analysis**: Fetch and analyze any public Dota 2 match
- 📊 **Detailed Stats**: KDA, GPM, XPM, item timings, and more
- 🔍 **OpenDota Integration**: Reliable match data fetching

## Setup

### 1. Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)

### 2. Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENDOTA_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend (Terminal 1)

```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

## Usage

1. Open `http://localhost:3000` in your browser
2. Enter a Dota 2 Match ID (e.g., `7550000000`)
3. Click "Analyze Match"

## API Endpoints

- `GET /` - API information
- `GET /match/{match_id}` - Fetch and analyze a match
- `GET /health` - Health check

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **OpenDota API** - Match data source

### Frontend
- **Next.js** - React framework
- **TailwindCSS** - Styling
- **Recharts** - Data visualization
- **Framer Motion** - Animations

## Project Structure

```
proyecto de dota 2/
├── main.py              # FastAPI server
├── opendota_service.py  # Match data fetching & processing
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── frontend/            # Next.js frontend
```

## Troubleshooting

### "Match not parsed yet"
Some matches need to be parsed by OpenDota first. Wait 2-3 minutes and try again.

### Frontend can't connect to backend
Ensure the backend is running on port 8000 and CORS is enabled.

## License

MIT

## Credits

- Match data provided by [OpenDota](https://www.opendota.com/)
