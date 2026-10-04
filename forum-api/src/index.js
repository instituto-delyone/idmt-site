const CATEGORIES = new Set([
  "Clínica",
  "Diagnóstico",
  "Terapêutica",
  "Evidências",
  "Educação médica",
  "Perguntas de pesquisa"
]);

const MAX = {
  name: 100,
  title: 180,
  question: 1200,
  context: 4000,
  content: 8000,
  comment: 5000
};

function json(data, status = 200, origin = "*") {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": origin,
      "access-control-allow-methods": "GET,POST,OPTIONS",
      "access-control-allow-headers": "Content-Type"
    }
  });
}

function clean(value, max) {
  return String(value ?? "").trim().slice(0, max);
}

function id() {
  return crypto.randomUUID();
}

function now() {
  return new Date().toISOString();
}

function validateName(name) {
  return name.length >= 2 && name.length <= MAX.name;
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "*";

    if (request.method === "OPTIONS") {
      return json({ ok: true }, 204, origin);
    }

    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    try {
      if (request.method === "GET" && path === "/health") {
        return json({ ok: true, service: "idmt-forum-api" }, 200, origin);
      }

      if (request.method === "GET" && path === "/discussions") {
        const category = url.searchParams.get("category");
        let query = `SELECT id, title, author_name, category, question, created_at, updated_at
                     FROM discussions
                     WHERE status = 'published'`;
        const params = [];

        if (category && CATEGORIES.has(category)) {
          query += " AND category = ?";
          params.push(category);
        }

        query += " ORDER BY created_at DESC LIMIT 100";
        const result = await env.DB.prepare(query).bind(...params).all();
        return json({ discussions: result.results || [] }, 200, origin);
      }

      const discussionMatch = path.match(/^\/discussions\/([^/]+)$/);
      if (request.method === "GET" && discussionMatch) {
        const discussionId = discussionMatch[1];
        const discussion = await env.DB.prepare(
          `SELECT id, title, author_name, category, question, context, content, created_at, updated_at
           FROM discussions WHERE id = ? AND status = 'published'`
        ).bind(discussionId).first();

        if (!discussion) return json({ error: "Discussão não encontrada." }, 404, origin);

        const comments = await env.DB.prepare(
          `SELECT id, author_name, content, created_at
           FROM comments
           WHERE discussion_id = ? AND status = 'published'
           ORDER BY created_at ASC`
        ).bind(discussionId).all();

        return json({ discussion, comments: comments.results || [] }, 200, origin);
      }

      if (request.method === "POST" && path === "/discussions") {
        const body = await request.json();
        const authorName = clean(body.author_name, MAX.name);
        const title = clean(body.title, MAX.title);
        const category = clean(body.category, 80);
        const question = clean(body.question, MAX.question);
        const context = clean(body.context, MAX.context);
        const content = clean(body.content, MAX.content);

        if (!validateName(authorName) || !title || !question || !CATEGORIES.has(category)) {
          return json({ error: "Nome, título, categoria e pergunta são obrigatórios." }, 400, origin);
        }

        const timestamp = now();
        const discussionId = id();
        await env.DB.prepare(
          `INSERT INTO discussions
           (id, title, author_name, category, question, context, content, created_at, updated_at, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'published')`
        ).bind(
          discussionId,
          title,
          authorName,
          category,
          question,
          context,
          content,
          timestamp,
          timestamp
        ).run();

        return json({ ok: true, id: discussionId }, 201, origin);
      }

      const commentMatch = path.match(/^\/discussions\/([^/]+)\/comments$/);
      if (request.method === "POST" && commentMatch) {
        const discussionId = commentMatch[1];
        const discussion = await env.DB.prepare(
          "SELECT id FROM discussions WHERE id = ? AND status = 'published'"
        ).bind(discussionId).first();

        if (!discussion) return json({ error: "Discussão não encontrada." }, 404, origin);

        const body = await request.json();
        const authorName = clean(body.author_name, MAX.name);
        const content = clean(body.content, MAX.comment);

        if (!validateName(authorName) || !content) {
          return json({ error: "Nome e comentário são obrigatórios." }, 400, origin);
        }

        const commentId = id();
        const timestamp = now();
        await env.DB.prepare(
          `INSERT INTO comments
           (id, discussion_id, author_name, content, created_at, status)
           VALUES (?, ?, ?, ?, ?, 'published')`
        ).bind(commentId, discussionId, authorName, content, timestamp).run();

        await env.DB.prepare(
          "UPDATE discussions SET updated_at = ? WHERE id = ?"
        ).bind(timestamp, discussionId).run();

        return json({ ok: true, id: commentId }, 201, origin);
      }

      return json({ error: "Rota não encontrada." }, 404, origin);
    } catch (error) {
      console.error(error);
      return json({ error: "Erro interno do fórum." }, 500, origin);
    }
  }
};
