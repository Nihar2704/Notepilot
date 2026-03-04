# ✈️ NotePilot — Local MVP Roadmap
### YouTube → Smart Notes · Runs on Your Machine

> **Hardware:** RTX 3050 4GB VRAM · 8GB DDR5 RAM  
> **LLM:** Groq API (free tier)  
> **Deployment:** Local only — `localhost`  
> **Core Feature:** YouTube URL → Summary + Key Concepts + Detailed Notes + Takeaways

---

## What NotePilot Does (Nothing More, Nothing Less)

```
You paste a YouTube URL
        ↓
NotePilot fetches the transcript
        ↓
Groq AI generates 4 note sections
        ↓
You read, copy, or download your notes
```

**Output per video:**

| # | Section | Description |
|---|---------|-------------|
| 1 | 📋 Summary | 4–6 sentence overview |
| 2 | 🔑 Key Concepts | 5–8 terms with clear definitions |
| 3 | 📝 Detailed Notes | 3–6 sections, section-by-section breakdown |
| 4 | 💡 Takeaways | 3–5 bullet points to remember |

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│           REACT FRONTEND                    │
│      Vite · Tailwind · localhost:5173       │
└──────────────────┬──────────────────────────┘
                   │ HTTP + polling
                   ▼
┌─────────────────────────────────────────────┐
│           FASTAPI BACKEND                   │
│           localhost:8000                    │
│                                             │
│  POST /api/summarize                        │
│  GET  /api/status/{job_id}                  │
│  GET  /api/history                          │
│  GET  /api/health                           │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │        NOTEPILOT PIPELINE            │   │
│  │                                      │   │
│  │  1. Validate URL                     │   │
│  │  2. Check SQLite cache               │   │
│  │  3. Fetch transcript                 │   │
│  │  4. Clean + chunk text               │   │
│  │  5. Groq map-reduce generation       │   │
│  │  6. Format + cache result            │   │
│  └──────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴───────────┐
        ▼                      ▼
  ┌───────────┐        ┌───────────────┐
  │ SQLite DB │        │   Groq API    │
  │ (cache)   │        │ llama-3.1-8b  │
  └───────────┘        └───────────────┘
```

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | **FastAPI** + Python 3.11 | Async, clean, great for ML tasks |
| Frontend | **React** + Vite + Tailwind | Fast dev, lightweight |
| Transcript | **youtube-transcript-api** | No API key, instant |
| Metadata | **yt-dlp** | Title, duration, thumbnail |
| LLM | **Groq** `llama-3.1-8b-instant` | Free · 128K context · ~500 tok/s |
| Chunking | **LangChain** `RecursiveCharacterTextSplitter` | Sentence-aware splitting |
| Cache | **SQLite** via `aiosqlite` | File-based, zero config |
| Server | **Uvicorn** | Run locally with one command |

**Removed from stack (local-only simplifications):**
- ~~slowapi rate limiting~~ — not needed, it's just you
- ~~CORS production config~~ — simple localhost allow-all
- ~~Render / Vercel deployment~~ — not needed
- ~~Environment hardening~~ — not needed locally

---

## Project Structure

```
notepilot/
│
├── backend/
│   ├── main.py                  # FastAPI app, CORS localhost, startup
│   ├── config.py                # .env loader
│   ├── requirements.txt
│   │
│   ├── routers/
│   │   └── summarize.py         # All API endpoints
│   │
│   ├── pipeline/
│   │   ├── validator.py         # URL validation, video ID extraction
│   │   ├── transcript.py        # Fetch + clean transcript
│   │   ├── chunker.py           # Split text into chunks
│   │   ├── llm.py               # Groq API wrapper
│   │   ├── summarizer.py        # Map-reduce orchestration
│   │   └── formatter.py         # LLM JSON → clean response
│   │
│   ├── db/
│   │   ├── cache.py             # SQLite read/write helpers
│   │   └── schema.sql           # Table definition
│   │
│   └── prompts/
│       ├── map_prompt.txt        # Per-chunk extraction prompt
│       └── reduce_prompt.txt     # Final notes generation prompt
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── URLInput.jsx      # Input + submit button
│       │   ├── StatusBar.jsx     # Animated progress steps
│       │   ├── VideoMeta.jsx     # Title, channel, duration
│       │   ├── TabNav.jsx        # Tab switcher
│       │   ├── SummaryPanel.jsx
│       │   ├── ConceptGrid.jsx
│       │   ├── NotesPanel.jsx
│       │   ├── TakeawayList.jsx
│       │   ├── ExportButton.jsx  # Download .md
│       │   ├── HistoryList.jsx   # Past notes from cache
│       │   └── ErrorBanner.jsx
│       ├── hooks/
│       │   └── useSummarize.js   # Submit + polling logic
│       └── index.css             # Tailwind + CSS variables
│
├── data/
│   └── notepilot.db             # SQLite cache (auto-created on first run)
│
├── .env                         # Your Groq API key
├── .env.example
└── README.md                    # Local setup instructions only
```

---

## The Pipeline (Step by Step)

### Step 1 — Validate
```
Input URL
   ├── Regex: must match youtube.com/watch?v= or youtu.be/
   ├── Extract video_id
   ├── Reject: live streams, playlists
   └── Check SQLite cache → if hit, return instantly (no LLM call)
```

### Step 2 — Fetch Transcript
```
youtube_transcript_api.get_transcript(video_id)
   ├── Tries manual captions first
   ├── Falls back to auto-generated captions
   └── Returns list of { text, start, duration }
```
> **No Whisper in MVP.** If no captions → clear error: *"No captions available for this video."*  
> Most lectures have captions. Whisper gets added in v1.1.

### Step 3 — Clean + Chunk
```
Cleaning:
  • Join all segments into one string
  • Remove [Music], [Applause], [Laughter] tags
  • Fix broken mid-sentence newlines
  • Normalize whitespace

Chunking:
  • chunk_size    = 3000 chars  (~750 tokens)
  • chunk_overlap = 200 chars
  • separators    = ["\n\n", "\n", ". ", " "]
```

### Step 4 — Map-Reduce via Groq

```
Full transcript (e.g. 8,000 words)
        │
   Split into N chunks (~3–6 for typical lecture)
        │
   ┌────┴────┬──────┬──────┐
   ▼         ▼      ▼      ▼
 Groq      Groq   Groq   Groq    ← MAP: each chunk → mini-summary + key points
   │         │      │      │        (0.5s delay between calls, stays under rate limit)
   └────┬────┴──────┴──────┘
        ▼
      Groq                        ← REDUCE: combine into final 4-section notes
        │
        ▼
   Notes JSON
```

### Step 5 — Cache + Return
```
Save to SQLite keyed by video_id:
  { title, channel, duration, thumbnail, transcript, notes_json, created_at }

Return to frontend:
  { metadata, notes: { summary, key_concepts, detailed_notes, takeaways } }
```

---

## API Design

### `POST /api/summarize`
```json
Request:  { "url": "https://youtube.com/watch?v=VIDEO_ID" }
Response: { "job_id": "abc123", "status": "processing" }
```
Returns immediately. Pipeline runs as a background task.

### `GET /api/status/{job_id}`
Polled every 2 seconds by the frontend.

```json
// While processing:
{ "status": "processing", "step": "Generating notes...", "progress": 65 }

// On success:
{
  "status": "done",
  "cached": false,
  "data": {
    "metadata": {
      "title": "Neural Networks Explained",
      "channel": "3Blue1Brown",
      "duration_seconds": 1847,
      "thumbnail": "https://img.youtube.com/..."
    },
    "notes": {
      "summary": "This lecture introduces...",
      "key_concepts": [
        { "term": "Backpropagation", "definition": "An algorithm that computes gradients..." }
      ],
      "detailed_notes": [
        { "section": "Introduction", "content": "The lecture begins by..." }
      ],
      "takeaways": [
        "Neural networks learn by adjusting weights through backpropagation",
        "Depth of the network determines complexity of learnable patterns"
      ]
    }
  }
}

// On error:
{ "status": "error", "message": "No captions found for this video." }
```

### `GET /api/history`
Returns last 20 cached notes (title, channel, video_id, created_at).

### `GET /api/health`
```json
{ "status": "ok", "groq": true, "cache_entries": 14 }
```

---

## Prompts

### Map Prompt (`prompts/map_prompt.txt`)
```
You are an expert lecture note-taker.

Extract key information from this transcript segment only.

Respond in valid JSON:
{
  "mini_summary": "2-3 sentence summary of this segment",
  "key_points": ["point 1", "point 2", "point 3"],
  "terms": ["term 1", "term 2"]
}

Transcript:
{chunk_text}

Return ONLY the JSON. No explanation. No markdown fences.
```

### Reduce Prompt (`prompts/reduce_prompt.txt`)
```
You are an expert academic note-taker creating study notes for a student.

Lecture: "{title}" by {channel}

Segment summaries:
{combined_summaries}

Generate structured study notes in valid JSON:
{
  "summary": "4-6 sentence overview of the entire lecture",
  "key_concepts": [
    { "term": "concept name", "definition": "clear 1-2 sentence explanation" }
  ],
  "detailed_notes": [
    { "section": "Section Title", "content": "Detailed notes..." }
  ],
  "takeaways": [
    "Key insight 1",
    "Key insight 2"
  ]
}

Rules:
- key_concepts: 5-8 items, plain language a student can understand
- detailed_notes: 3-6 sections, each 3+ sentences
- takeaways: 3-5 items, memorable and actionable
- Return ONLY the JSON. No markdown. No preamble.
```

---

## UI Design

### Design Direction
**Calm academic.** Like a well-designed university reading tool — not a startup dashboard.  
Students should feel focused the moment they open it.

```
Fonts:   DM Serif Display (headings) + Source Sans 3 (body)
Theme:   Off-white paper · Deep navy text · Amber accent
Feel:    Notion meets a well-designed textbook
```

```css
--bg:           #F7F6F1   /* warm paper white */
--surface:      #FFFFFF   /* cards + panels */
--border:       #E8E6DF   /* subtle dividers */
--text:         #1A1A2E   /* deep navy */
--muted:        #6B6B80   /* secondary / captions */
--accent:       #C9873A   /* amber — buttons, highlights */
--accent-light: #FFF4E6   /* amber tint — concept cards */
--success:      #2E7D4F   /* green — completed steps */
```

### Screen 1 — Empty State
```
✈️  NotePilot                                    [History]

        Turn any lecture into smart notes.

  [ 🔗  Paste a YouTube lecture URL...                    ]
                  [ Generate Notes → ]

       Works with lectures, talks, tutorials, MOOCs
```

### Screen 2 — Processing
```
✈️  NotePilot

  📹  Neural Networks Explained — 3Blue1Brown · 31 min

  ✅  URL validated
  ✅  Transcript fetched  (6,240 words)
  ⟳   Generating notes...  ━━━━━━━░░░  70%
  ○   Done

        Usually takes 10–20 seconds
```

### Screen 3 — Notes View
```
✈️  NotePilot                      [New Note]  [↓ Export .md]

  Neural Networks Explained
  3Blue1Brown · 31 min · youtube.com/watch?v=...

  [Summary]  [Key Concepts]  [Detailed Notes]  [Takeaways]
  ────────────────────────────────────────────────────────

  📋 SUMMARY
  ┌──────────────────────────────────────────────────────┐
  │  This lecture provides an intuitive introduction to  │
  │  neural networks, from biological analogy all the    │
  │  way up to backpropagation and gradient descent...   │
  └──────────────────────────────────────────────────────┘

  🔑 KEY CONCEPTS
  ┌───────────────────┐   ┌──────────────────────────┐
  │  Backpropagation  │   │  Gradient Descent        │
  │  Algorithm for    │   │  Optimization method...  │
  │  computing grads  │   │                          │
  └───────────────────┘   └──────────────────────────┘
```

---

## Edge Cases

| Case | Response |
|------|----------|
| Not a YouTube URL | "Please enter a valid YouTube URL." |
| Playlist URL | "Please paste a single video URL, not a playlist." |
| Live stream | "Live streams can't be summarized. Try after it ends." |
| Private / deleted video | "This video is unavailable or private." |
| No captions at all | "No captions available for this video." |
| Auto-generated captions | Used normally, small notice shown |
| Already in cache | Returns instantly, skips all processing |
| LLM returns bad JSON | Retry once with stricter prompt → raw text fallback |
| Groq rate limit hit | 0.5s delay between chunk calls, stays well under 30 req/min |
| Groq API down | "AI service unavailable. Check your GROQ_API_KEY or try again." |
| Very short video (< 2 min) | Process normally, notes will be brief |
| Very long video (> 3 hrs) | Warn: "Long video — processing may take 2–3 minutes." |

---

## Critical Points

**1. JSON parsing must never crash**
```python
def safe_parse(text: str) -> dict | None:
    cleaned = text.strip().removeprefix("```json").removesuffix("```").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None  # caller handles retry
```

**2. In-memory job tracker is fine for local use**
```python
jobs: dict[str, dict] = {}
# { job_id: { status, step, progress, data, error } }
# Resets on server restart — completely fine locally
```

**3. Space out Groq map calls**
```python
for chunk in chunks:
    result = await groq_call(chunk)
    await asyncio.sleep(0.5)   # stays under 30 req/min free limit
```

**4. CORS — allow localhost only**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**5. Cache everything**
Same video should never hit Groq twice. Always check `video_id` in SQLite before starting the pipeline.

---

## Build Plan (9 Days)

### Days 1–2 · Foundation
- [ ] Create folder structure + virtual environment
- [ ] Install all dependencies (`requirements.txt`)
- [ ] FastAPI skeleton with `/api/health` working
- [ ] SQLite schema created + basic cache helpers
- [ ] `.env` with Groq API key — test one Groq call

### Days 3–5 · Pipeline
- [ ] URL validator + video ID extractor
- [ ] `youtube-transcript-api` integration
- [ ] `yt-dlp` metadata fetch (title, duration, thumbnail)
- [ ] Text cleaner (strip noise, normalize)
- [ ] LangChain chunker configured and tested
- [ ] Groq map call working (single chunk → mini-summary)
- [ ] Full map-reduce pipeline working end to end
- [ ] JSON parser with retry logic
- [ ] Cache read/write wired into pipeline
- [ ] Test with 5–10 real lecture videos via `curl`

### Days 6–7 · API Layer
- [ ] Background task + in-memory job tracker
- [ ] `POST /api/summarize` endpoint
- [ ] `GET /api/status/{job_id}` polling endpoint
- [ ] `GET /api/history` from SQLite cache
- [ ] All error states return clean, readable messages
- [ ] Full backend tested via browser / Postman

### Days 8–9 · Frontend
- [ ] Vite + React + Tailwind setup
- [ ] `URLInput` with inline validation feedback
- [ ] `StatusBar` with animated steps + 2s polling
- [ ] `VideoMeta` strip (thumbnail, title, channel, duration)
- [ ] `TabNav` + all 4 note panels wired up
- [ ] `ExportButton` → download `.md` file
- [ ] `HistoryList` from `/api/history`
- [ ] `ErrorBanner` for all error cases
- [ ] Full end-to-end flow tested in browser
- [ ] Test 10+ real lecture videos (MOOC, YouTube EDU, talks)

---

## Local Setup (One Time)

```bash
# 1. Create project and virtual environment
mkdir notepilot && cd notepilot
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt

# 3. Create .env
echo "GROQ_API_KEY=your_key_here" > .env
echo "CACHE_DB_PATH=../data/notepilot.db" >> .env

# 4. Run backend
uvicorn main:app --reload --port 8000

# 5. Run frontend (new terminal)
cd ../frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### requirements.txt
```
fastapi
uvicorn[standard]
python-dotenv
httpx
youtube-transcript-api
yt-dlp
langchain
langchain-community
groq
aiosqlite
langdetect
```

### Get Your Free Groq API Key
1. Go to **console.groq.com**
2. Sign up free (no credit card needed)
3. Create an API key → paste into `.env`
4. Free tier: **14,400 req/day · 30 req/min** — more than enough for personal use

---

## Post-MVP Features (When Ready)

| Feature | Effort | Value |
|---------|--------|-------|
| Whisper fallback (no-caption videos) | Medium | High |
| PDF summarization | Medium | High |
| Dark mode toggle | Low | Medium |
| Q&A chat with notes | High | High |
| Flashcard export (Anki `.apkg`) | Low | Medium |
| Chapter-aware note splitting | Medium | Medium |

---

## Summary Card

```
NotePilot — Local MVP
──────────────────────────────────────────────
Input:     YouTube URL
Output:    Summary · Key Concepts ·
           Detailed Notes · Takeaways
LLM:       Groq llama-3.1-8b-instant (free)
Backend:   FastAPI + SQLite · localhost:8000
Frontend:  React + Vite + Tailwind · localhost:5173
Build:     9 focused days
Deploy:    Your machine only
──────────────────────────────────────────────
```

---
*NotePilot · Local MVP Roadmap · March 2026*
