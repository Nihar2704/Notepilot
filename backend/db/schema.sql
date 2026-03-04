CREATE TABLE IF NOT EXISTS notes (
    video_id TEXT PRIMARY KEY,
    title TEXT,
    channel TEXT,
    duration_seconds INTEGER,
    thumbnail TEXT,
    transcript TEXT,
    notes_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
