-- AIGAR persistent library metadata
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  size_bytes INTEGER NOT NULL DEFAULT 0,
  sha256 TEXT,
  r2_key TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'uploaded',
  uploaded_at INTEGER NOT NULL,
  uploaded_by TEXT,
  chunk_count INTEGER NOT NULL DEFAULT 0,
  error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_sha256 ON documents(sha256);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at DESC);

CREATE TABLE IF NOT EXISTS chunks (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL,
  sequence INTEGER NOT NULL,
  start_page INTEGER,
  end_page INTEGER,
  text_length INTEGER NOT NULL DEFAULT 0,
  text_checksum TEXT,
  r2_key TEXT NOT NULL UNIQUE,
  created_at INTEGER NOT NULL,
  FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_sequence ON chunks(document_id, sequence);
