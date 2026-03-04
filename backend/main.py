import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from db.cache import init_db, get_cache_count
from routers.summarize import router as summarize_router
from contextlib import asynccontextmanager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await init_db()
    yield
    # Shutdown logic (if any)

app = FastAPI(title="NotePilot API", lifespan=lifespan)

# CORS — allow localhost only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summarize_router)

@app.get("/api/health")
async def health_check():
    cache_count = await get_cache_count()
    return {
        "status": "ok",
        "groq": os.getenv("GROQ_API_KEY") is not None,
        "cache_entries": cache_count
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
