from backend.pipeline.transcript import fetch_transcript
import asyncio

async def test():
    video_id = "ksTPzTWUb6o"
    print(f"Testing transcript fetch for {video_id}...")
    res = fetch_transcript(video_id)
    if res:
        print(f"Success! Fetched {len(res)} characters.")
    else:
        print("Failed to fetch transcript.")

if __name__ == "__main__":
    asyncio.run(test())
