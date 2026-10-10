-- AIGAR D1 schema: persistent library + adaptive interaction layer.
-- Keep this bootstrap schema aligned with the tables used by storage_runtime.py
-- and conversation_runtime.py. All statements are idempotent.

CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  size_bytes INTEGER NOT NULL DEFAULT 0,
  sha256 TEXT,
  r2_key TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'uploaded',
  uploaded_at INTEGER NOT NULL,
  uploaded_by TEXT,
  chunk_count INTEGER NOT NULL DEFAULT 0,
  error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_sha256 ON documents(sha256);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at DESC);

-- The live ingestion pipeline uses document_chunks (not the legacy "chunks" name).
CREATE TABLE IF NOT EXISTS document_chunks (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL,
  sequence INTEGER NOT NULL,
  source TEXT NOT NULL,
  start_page INTEGER,
  end_page INTEGER,
  r2_key TEXT NOT NULL,
  text_length INTEGER NOT NULL DEFAULT 0,
  checksum TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  UNIQUE(document_id, sequence)
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_document
  ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_sequence
  ON document_chunks(document_id, sequence);

CREATE TABLE IF NOT EXISTS adaptive_interactions (
  id TEXT PRIMARY KEY,
  session_hash TEXT NOT NULL,
  turn_id TEXT NOT NULL,
  interaction_type TEXT NOT NULL,
  secondary_types_json TEXT NOT NULL DEFAULT '[]',
  predicted_mode TEXT,
  model_version TEXT NOT NULL,
  minimal_snapshot_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_adaptive_interactions_created
  ON adaptive_interactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_adaptive_interactions_session
  ON adaptive_interactions(session_hash, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_adaptive_interactions_type
  ON adaptive_interactions(interaction_type, created_at DESC);

CREATE TABLE IF NOT EXISTS adaptive_feedback (
  id TEXT PRIMARY KEY,
  interaction_id TEXT,
  category TEXT NOT NULL CHECK(category IN ('intent','context','reasoning','evidence','format','other')),
  rating TEXT NOT NULL CHECK(rating IN ('minor','incomplete','wrong','wrong_mode')),
  comment TEXT,
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','in_review','reviewed','closed')),
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_adaptive_feedback_created
  ON adaptive_feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_adaptive_feedback_interaction
  ON adaptive_feedback(interaction_id);
CREATE INDEX IF NOT EXISTS idx_adaptive_feedback_status
  ON adaptive_feedback(status, created_at DESC);

CREATE TABLE IF NOT EXISTS adaptive_feedback_reviews (
  id TEXT PRIMARY KEY,
  feedback_id TEXT NOT NULL,
  reviewer_id TEXT NOT NULL,
  root_cause TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN ('confirmed','partially_confirmed','not_confirmed','inconclusive')),
  notes TEXT,
  reviewed_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_adaptive_feedback_reviews_feedback
  ON adaptive_feedback_reviews(feedback_id, reviewed_at DESC);

CREATE TABLE IF NOT EXISTS adaptive_evaluation_cases (
  id TEXT PRIMARY KEY,
  review_id TEXT NOT NULL,
  input_snapshot_json TEXT NOT NULL DEFAULT '{}',
  expected_behavior TEXT NOT NULL,
  training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(training_eligible = 0),
  dataset_version TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_adaptive_evaluation_cases_created
  ON adaptive_evaluation_cases(created_at DESC);

CREATE TABLE IF NOT EXISTS adaptive_useful_interaction_logs (
  id TEXT PRIMARY KEY,
  session_hash TEXT NOT NULL DEFAULT '',
  turn_id TEXT,
  interaction_id TEXT,
  purpose TEXT NOT NULL,
  minimal_snapshot_json TEXT NOT NULL DEFAULT '{}',
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_adaptive_useful_logs_created
  ON adaptive_useful_interaction_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_adaptive_useful_logs_interaction
  ON adaptive_useful_interaction_logs(interaction_id);

CREATE TABLE IF NOT EXISTS adaptive_audit_log (
  id TEXT PRIMARY KEY,
  actor_id TEXT NOT NULL,
  action TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id TEXT,
  details_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_adaptive_audit_log_created
  ON adaptive_audit_log(created_at DESC);
