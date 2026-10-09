AIGAR MEMORY LAB v1
===================

PURPOSE
This is an isolated, repository-backed experiment for three memory layers.
The main AIGAR reasoning core remains separate. Documents are retrieved as
evidence; their presence does not mean the model has permanently learned them.

FOLDERS
- memoria_imediata/: every .txt is discovered and loaded during Memory Lab
  initialization. The module reports ready only when all discovered immediate
  TXT files load successfully.
- memoria_curto_prazo/: documents are ranked for relevant retrieval during
  ordinary questions.
- memoria_longo_prazo/: fallback knowledge, queried when the immediate and
  short-term layers produce no lexical matches.

HOW TO ADD DOCUMENTS
Add a UTF-8 .txt file to the desired folder in this repository. The Worker
reads the GitHub tree and raw document contents at runtime. New documents on
the main branch are discovered after the refresh interval (60 seconds by
default) or on the next cold initialization. Changes in a feature branch are
not visible to a Worker configured to read "main" until merged or configured
to use that branch.

IMPORTANT LIMITATIONS
- The initial retrieval method is lexical overlap, not semantic embeddings.
- "Immediate" means loaded into the Memory Lab cache at initialization, not
  automatically inserted in every answer.
- Long-term fallback currently triggers when earlier layers yield no lexical
  matches; later versions should also use explicit confidence/evidence checks.
- GitHub API rate limits and network errors can prevent loading. Check the
  memory status endpoint and errors rather than assuming a successful load.
- The existing AIGAR API must continue working when this optional module fails.
- Do not place secrets or private user information in public repository TXT files.

CONFIG
Edit config.json for enabled, repository, ref, root, result limits and refresh
interval. This version ships defaults in engine.py as well, so the runtime
configuration must be wired in by the integration code before edits to config
take effect.
