# Render.com Deployment Configuration

## Build Command
```bash
pip install -r backend/requirements.txt
```

## Start Command
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables (Set in Render Dashboard)

### Required
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `FIREBASE_CREDENTIALS` - Complete JSON content of firebase_credentials.json (as a single-line string)

### Optional
- `PORT` - Automatically set by Render (default: 10000)
- `PYTHON_VERSION` - 3.10 (if not auto-detected)

## Health Check Endpoint
`/health`

## Notes
- Ensure the repository is connected to Render
- Use "Web Service" type
- Select "Python" as the environment
- Enable auto-deploy from main branch
