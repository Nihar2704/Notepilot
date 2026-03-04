from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

def chunk_text(text: str, chunk_size: int = 3000, chunk_overlap: int = 200) -> List[str]:
    """
    Splits text into chunks of specified size and overlap.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "]
    )
    return splitter.split_text(text)
