const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = Number(process.env.PORT) || 3000;
const HOST = process.env.HOST || "0.0.0.0";

const physiologyDirectory = path.join(
  __dirname,
  "..",
  "Engines",
  "Aurora",
  "Bibliotecas",
  "Medicina",
  "Fisiologia"
);

function getLibraryStatus() {
  try {
    const files = fs
      .readdirSync(physiologyDirectory, { withFileTypes: true })
      .filter((entry) => entry.isFile() && entry.name.toLowerCase().endsWith(".md"));

    return {
      available: true,
      markdown_files: files.length,
      directory: "Engines/Aurora/Bibliotecas/Medicina/Fisiologia"
    };
  } catch (error) {
    return {
      available: false,
      markdown_files: 0,
      directory: "Engines/Aurora/Bibliotecas/Medicina/Fisiologia",
      error: error.code || "LIBRARY_UNAVAILABLE"
    };
  }
}

app.disable("x-powered-by");

app.get("/", (_request, response) => {
  response.status(200).json({
    service: "aigar-railway-backend",
    status: "running",
    health: "/health"
  });
});

app.get("/health", (_request, response) => {
  const library = getLibraryStatus();
  const healthy = library.available && library.markdown_files > 0;

  response.status(healthy ? 200 : 503).json({
    ok: healthy,
    service: "aigar-railway-backend",
    library
  });
});

const server = app.listen(PORT, HOST, () => {
  const library = getLibraryStatus();
  console.log(`AIGAR backend listening on http://${HOST}:${PORT}`);
  console.log(
    library.available
      ? `Physiology library available: ${library.markdown_files} Markdown files`
      : `Physiology library unavailable: ${library.error}`
  );
});

function shutdown(signal) {
  console.log(`${signal} received; closing AIGAR backend.`);
  server.close((error) => {
    if (error) {
      console.error("Error while closing server:", error);
      process.exitCode = 1;
    }
  });
}

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));
