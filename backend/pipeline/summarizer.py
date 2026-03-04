import asyncio
import os
from typing import List, Dict, Optional
from pipeline.chunker import chunk_text
from pipeline.llm import groq_call, safe_parse_json

async def run_map_reduce_pipeline(transcript: str, metadata: Dict) -> Optional[Dict]:
    """
    Orchestrates the map-reduce summarization process.
    """
    # Get current directory to build absolute paths to prompts
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Prompts are in ../prompts/
    prompts_dir = os.path.join(os.path.dirname(current_dir), "prompts")
    
    # 1. Chunk transcript
    chunks = chunk_text(transcript)
    print(f"Transcript split into {len(chunks)} chunks.")
    
    # 2. Map stage: Mini-summary for each chunk
    map_prompt_path = os.path.join(prompts_dir, "map_prompt.txt")
    with open(map_prompt_path, "r") as f:
        map_prompt_template = f.read()
        
    map_results = []
    for i, chunk in enumerate(chunks):
        prompt = map_prompt_template.format(chunk_text=chunk)
        print(f"Mapping chunk {i+1}/{len(chunks)}...")
        
        # Retry logic for map
        res = await groq_call(prompt)
        print(f"Map raw response: {res}")
        parsed = safe_parse_json(res)
        print(f"Map parsed: {parsed}")
        
        if parsed:
            map_results.append(parsed)
        else:
            print(f"Warning: Failed to parse map result for chunk {i+1}.")
            
        # Space out calls to stay under rate limit (30 req/min)
        await asyncio.sleep(0.5)
        
    if not map_results:
        return None
        
    # 3. Reduce stage: Combine into final notes
    reduce_prompt_path = os.path.join(prompts_dir, "reduce_prompt.txt")
    with open(reduce_prompt_path, "r") as f:
        reduce_prompt_template = f.read()
        
    combined_summaries = "\n\n".join([
        f"- {res.get('mini_summary')}\n  Key points: {', '.join(res.get('key_points', []))}"
        for res in map_results
    ])
    
    reduce_prompt = reduce_prompt_template.format(
        title=metadata.get("title"),
        channel=metadata.get("channel"),
        combined_summaries=combined_summaries
    )
    
    print("Reducing summaries into final notes...")
    final_res = await groq_call(reduce_prompt)
    final_notes = safe_parse_json(final_res)
    
    return final_notes
