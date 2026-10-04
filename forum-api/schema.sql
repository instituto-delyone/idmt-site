CREATE TABLE IF NOT EXISTS discussions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  author_name TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'Clínica',
  question TEXT NOT NULL,
  context TEXT,
  content TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'published'
);

CREATE TABLE IF NOT EXISTS comments (
  id TEXT PRIMARY KEY,
  discussion_id TEXT NOT NULL,
  author_name TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'published',
  FOREIGN KEY (discussion_id) REFERENCES discussions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_discussions_created_at ON discussions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_discussions_category ON discussions(category);
CREATE INDEX IF NOT EXISTS idx_comments_discussion_id ON comments(discussion_id, created_at ASC);
