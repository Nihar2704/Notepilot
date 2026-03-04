import re
from typing import Optional

def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the video ID from a YouTube URL.
    Supports:
    - youtube.com/watch?v=ID
    - youtu.be/ID
    - youtube.com/embed/ID
    - youtube.com/v/ID
    """
    patterns = [
        r'(?:v=|\/v\/|embed\/|youtu\.be\/|\/)([^"&?\/\s]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def is_valid_youtube_url(url: str) -> bool:
    """
    Basic validation for YouTube URLs.
    """
    if not url:
        return False
    
    # Check if it contains youtube.com or youtu.be
    if "youtube.com" not in url and "youtu.be" not in url:
        return False
        
    return extract_video_id(url) is not None
