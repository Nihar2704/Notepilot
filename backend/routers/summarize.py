import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from pipeline.validator import is_valid_youtube_url, extract_video_id
from pipeline.transcript import fetch_metadata, fetch_transcript
from pipeline.summarizer import run_map_reduce_pipeline
from db.cache import get_cached_note, save_note, get_history

router = APIRouter()

# In-memory job tracker
# { job_id: { status, step, progress, data, error } }
jobs: Dict[str, dict] = {}

class SummarizeRequest(BaseModel):
    url: str

async def process_video(job_id: str, video_id: str, url: str):
    """
    Background task to process the video.
    """
    try:
        print(f"Processing video {video_id} for job {job_id}...")
        # Step 1: Validate (already done in endpoint but for safety)
        jobs[job_id].update({"step": "Validating URL...", "progress": 5})
        
        # Step 2: Check Cache
        jobs[job_id].update({"step": "Checking cache...", "progress": 10})
        cached = await get_cached_note(video_id)
        if cached:
            print("Found in cache!")
            jobs[job_id].update({
                "status": "done",
                "step": "Found in cache!",
                "progress": 100,
                "data": {
                    "metadata": {
                        "title": cached["title"],
                        "channel": cached["channel"],
                        "duration_seconds": cached["duration_seconds"],
                        "thumbnail": cached["thumbnail"]
                    },
                    "notes": cached["notes"]
                },
                "cached": True
            })
            return

        # Step 3: Fetch Metadata
        jobs[job_id].update({"step": "Fetching metadata...", "progress": 20})
        try:
            print("Fetching metadata...")
            metadata = fetch_metadata(video_id)
        except Exception as e:
            print(f"Metadata fetch failed: {e}")
            metadata = {
                "title": "YouTube Video",
                "channel": "YouTube Channel",
                "duration_seconds": 0,
                "thumbnail": ""
            }
        
        # Step 4: Fetch Transcript
        jobs[job_id].update({"step": "Fetching transcript...", "progress": 40})
        print("Fetching transcript...")
        transcript = fetch_transcript(video_id)
        if not transcript:
            print("No transcript found (after all fallbacks)!")
            jobs[job_id].update({
                "status": "error",
                "message": "No captions available for this video."
            })
            return
            
        print(f"Transcript ready ({len(transcript)} chars). Starting summarization...")
        # Step 5: Map-Reduce Summarization
        jobs[job_id].update({"step": "Generating notes (this may take 20-40s)...", "progress": 60})
        notes = await run_map_reduce_pipeline(transcript, metadata)
        
        if not notes:
            jobs[job_id].update({
                "status": "error",
                "message": "Failed to generate notes. AI service error."
            })
            return
            
        # Step 6: Cache result
        jobs[job_id].update({"step": "Saving to cache...", "progress": 95})
        await save_note(video_id, metadata, transcript, notes)
        
        # Done
        jobs[job_id].update({
            "status": "done",
            "step": "Done!",
            "progress": 100,
            "data": {
                "metadata": metadata,
                "notes": notes
            },
            "cached": False
        })
        
    except Exception as e:
        print(f"Error in background task: {e}")
        jobs[job_id].update({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        })

@router.post("/api/summarize")
async def summarize(request: SummarizeRequest, background_tasks: BackgroundTasks):
    if not is_valid_youtube_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
    video_id = extract_video_id(request.url)
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "status": "processing",
        "step": "Starting pipeline...",
        "progress": 0
    }
    
    background_tasks.add_task(process_video, job_id, video_id, request.url)
    
    return {"job_id": job_id, "status": "processing"}

@router.get("/api/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@router.get("/api/history")
async def history():
    return await get_history()
