# OFC Solver AI

AI-powered Open-Face Chinese Poker analysis using GTO (Game Theory Optimal) solutions.

## Features

- 🤖 **Natural Language Queries**: Ask questions in plain English
- 📊 **GTO Database Access**: Queries a comprehensive CFR-solved database
- 🎯 **Smart SQL Generation**: AI generates optimal queries automatically
- 🔄 **Multi-step Reasoning**: Handles complex questions requiring multiple queries

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Test CLI Mode

```bash
python cli.py
```

Example questions to try:
- "What's the average EV for solutions with a pair of aces on top?"
- "Show me a solution with a flush on the bottom"
- "How many solutions use jokers?"
- "What are the most common hand types for the middle row?"

### 3. Run the API Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

### 4. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health (includes DB status) |
| `/chat` | POST | Chat with the AI agent |
| `/query` | POST | Execute raw SQL (SELECT only) |
| `/schema` | GET | Get database schema |
| `/stats` | GET | Get table row counts |

#### Chat Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the highest EV solution in the database?"}'
```

## Configuration

Environment variables (in `.env`):

```env
MYSQL_HOST=ofc.coach
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=cfr

ANTHROPIC_API_KEY=your_api_key
```

## Database Schema

### solutions (main table)
- `solution`: Hand arrangement (e.g., "Jh4s3h-As5c4c3c2h-KdJd9d7d3d")
- `ev`: Expected value
- `frequency`: GTO play frequency
- `top_comb`, `mid_comb`, `bot_comb`: Hand type names
- `dead`: Dead cards

### alternative_solutions
- Alternative plays for each solution with frequencies and EVs

### spots
- Game situations with opponent hands

## Card Notation

- Ranks: A, K, Q, J, T, 9-2
- Suits: h (♥), d (♦), c (♣), s (♠)
- Jokers: `*` prefix (e.g., `*Qd`)

## Solution Format

`Top-Middle-Bottom` where:
- Top: 3 cards (weakest)
- Middle: 5 cards
- Bottom: 5 cards (strongest)

Example: `Jh4s3h-As5c4c3c2h-KdJd9d7d3d`
- Top: J♥ 4♠ 3♥ (high card)
- Middle: A♠ 5♣ 4♣ 3♣ 2♥ (wheel straight)
- Bottom: K♦ J♦ 9♦ 7♦ 3♦ (flush)

## License

Private - For authorized users only.
