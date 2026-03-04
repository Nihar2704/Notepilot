# ✈️ NotePilot — Technical Project Report
### YouTube → Smart Notes · Local AI-Powered Study Assistant

NotePilot is a high-performance, local-first application designed to transform long YouTube lectures into structured, academic-grade study notes. It leverages the cutting-edge speed of the Groq Llama-3.1 model to provide nearly instant summarization.

---

## 1. System Architecture
NotePilot follows a modern **Decoupled Client-Server Architecture**:

- **Frontend:** A React 18 application built with Vite for sub-second hot-reloading and Tailwind CSS v4 for "Calm Academic" styling.
- **Backend:** An asynchronous FastAPI (Python 3.11+) server that manages long-running AI tasks in the background.
- **Database:** A zero-config SQLite database (via `aiosqlite`) used as a persistent cache to ensure that the same video is never processed twice, saving API costs and time.
- **AI Engine:** Groq Cloud API running `llama-3.1-8b-instant`.

---

## 2. The NotePilot Pipeline (The "Brain")
When a URL is submitted, NotePilot executes a 6-stage pipeline:

1.  **Validation:** Extracts the YouTube Video ID and checks the SQLite cache. If found, it returns the result in **< 10ms**.
2.  **Metadata Fetching:** Uses `yt-dlp` to grab the video title, channel name, and thumbnail.
3.  **Transcript Extraction:**
    - Primary: `youtube-transcript-api` (fastest).
    - Fallback: `yt-dlp` (resilient).
    - Translation: Automatically detects non-English captions and translates them to English.
4.  **Semantic Chunking:** Since LLMs have "context windows," we use LangChain’s `RecursiveCharacterTextSplitter` to break long transcripts (e.g., a 2-hour lecture) into logical 3,000-character chunks with overlap to maintain context.
5.  **Map-Reduce Orchestration:**
    - **Map Stage:** The LLM summarizes each chunk individually into "mini-summaries" and key terms.
    - **Reduce Stage:** The LLM takes all mini-summaries and synthesizes them into the final 4-section study note structure.
6.  **JSON Sanitization:** A custom parser ensures the LLM's raw text is converted into valid JSON, even if the AI includes conversational "filler."

---

## 3. Tech Stack & Rationale

| Technology | Role | Why we used it? |
| :--- | :--- | :--- |
| **Groq (Llama 3.1 8B)** | LLM Model | **Speed.** Groq can process ~500 tokens/sec. It summarizes a 30-min video in seconds where GPT-4 would take minutes. |
| **FastAPI** | Backend | **Async support.** Allows the server to handle multiple users and background tasks without "freezing" the UI. |
| **Vite + React** | Frontend | **Development Speed.** Minimal overhead and incredibly fast build times compared to Create React App. |
| **Tailwind v4** | CSS | **Utility-first.** Allows for a high-end "Notion-like" aesthetic without writing 1000s of lines of custom CSS. |
| **SQLite** | Database | **Zero-Config.** No need to install a heavy database like PostgreSQL. It's just a file on your disk. |
| **LangChain** | Data Processing | **Industry standard** for splitting text and managing LLM prompts. |

---

## 4. Unique Selling Points (USP)
1.  **Speed:** Powered by Groq, it is arguably the fastest YouTube summarizer you can run locally.
2.  **Academic Structure:** Unlike generic summaries, it provides **4 distinct sections**: A 4-6 sentence summary, a grid of key concepts, detailed section-by-section notes, and actionable takeaways.
3.  **Local-First Privacy:** Your history and cache live on your machine, not on a third-party server.
4.  **Translation Support:** Can take a lecture in Hindi, Spanish, or French and provide the study notes in English.

---

## 5. Major Problems Fixed During Development

### 🛑 Problem 1: ModuleNotFoundError (Imports)
- **Cause:** Python's confusing handling of package paths when running scripts from different subfolders.
- **Fix:** We refactored all imports to be relative and adjusted the project to run directly from the `backend/` directory, simplifying the developer workflow.

### 🛑 Problem 2: FileNotFoundError (SQL & Prompts)
- **Cause:** Using relative paths like `open("prompts/map.txt")` fails if the user starts the server from a different folder.
- **Fix:** Implemented robust path discovery using `os.path.abspath(__file__)`. Now, NotePilot finds its prompt files and database regardless of where you start it from.

### 🛑 Problem 3: YouTube Rate Limiting (429 Errors)
- **Cause:** YouTube blocks automated requests from shared IP addresses (common in cloud environments).
- **Fix:** We built a multi-stage fallback system. If the primary API fails, it tries `yt-dlp`. If all fails, we implemented a **Mock Fallback mode** to allow UI/UX testing even when the IP is blocked.

### 🛑 Problem 4: LLM JSON Formatting Errors
- **Cause:** LLMs sometimes add text like "Here is your JSON:" which breaks the code.
- **Fix:** Created a "Safe Parser" using regex and string stripping to find the JSON hidden inside the AI's response.

---

## 6. User Flow
1.  **Input:** User enters a YouTube URL into the clean, centered search bar.
2.  **Processing:** The "Generate" button turns into a loading state. The backend starts the background job.
3.  **Feedback:** The frontend polls the server every 2 seconds for status updates.
4.  **Output:** Once complete, the UI smoothly transitions to display the 4-tabbed study guide.
5.  **Persistence:** The user can refresh the page or return later; the SQLite cache will load the notes instantly.

---

## 7. Edge Cases Handled
- **No Captions:** If a video has no audio or captions, NotePilot provides a clear "No captions available" error rather than crashing.
- **Long Videos:** Handled via the Map-Reduce chunking strategy to prevent "Out of Token" errors.
- **Invalid URLs:** Front-end and back-end regex validation prevent processing non-YouTube links.
- **Port Conflict:** Built-in guidance for resolving `[Errno 10048]` (port 8000 already in use).

---
**NotePilot · Project Report · March 2026**
