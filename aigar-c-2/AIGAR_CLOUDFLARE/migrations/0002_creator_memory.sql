-- Apply to the existing AIGAR D1 database before enabling Creator Memory imports.
-- Idempotent: safe to apply more than once.
CREATE TABLE IF NOT EXISTS creator_memory_records (
  id TEXT PRIMARY KEY,
  source_interaction_id TEXT,
  source_turn_id TEXT,
  schema_version TEXT NOT NULL,
  r2_key TEXT NOT NULL UNIQUE,
  sha256 TEXT NOT NULL UNIQUE,
  size_bytes INTEGER NOT NULL,
  imported_by TEXT NOT NULL,
  imported_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'stored'
    CHECK(status IN ('stored','invalidated','archived')),
  metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_creator_memory_imported
  ON creator_memory_records(imported_at DESC);
CREATE INDEX IF NOT EXISTS idx_creator_memory_source_interaction
  ON creator_memory_records(source_interaction_id);
CREATE INDEX IF NOT EXISTS idx_creator_memory_status
  ON creator_memory_records(status, imported_at DESC);
