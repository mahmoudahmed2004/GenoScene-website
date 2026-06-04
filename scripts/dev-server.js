import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

import { handleRequest } from "../api/analyze.js";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const port = Number(process.env.PORT || 3000);
const mimeTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".jpeg": "image/jpeg",
  ".jpg": "image/jpeg",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
};

async function proxyApi(request, response) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  const webRequest = new Request(`http://localhost:${port}${request.url}`, {
    method: request.method,
    headers: request.headers,
    body: chunks.length ? Buffer.concat(chunks) : undefined,
  });
  const apiResponse = await handleRequest(webRequest);
  response.writeHead(apiResponse.status, Object.fromEntries(apiResponse.headers.entries()));
  response.end(Buffer.from(await apiResponse.arrayBuffer()));
}

async function serveStatic(request, response) {
  const pathname = decodeURIComponent(new URL(request.url, `http://localhost:${port}`).pathname);
  const requested = pathname === "/" ? "/index.html" : pathname;
  const filePath = resolve(root, `.${requested}`);

  if (!filePath.startsWith(`${root}${sep}`)) {
    response.writeHead(403).end("Forbidden");
    return;
  }

  try {
    const fileStat = await stat(filePath);
    if (!fileStat.isFile()) throw new Error("Not a file");
    response.writeHead(200, {
      "Content-Type": mimeTypes[extname(filePath).toLowerCase()] || "application/octet-stream",
    });
    response.end(await readFile(filePath));
  } catch {
    response.writeHead(404).end("Not found");
  }
}

createServer(async (request, response) => {
  try {
    if (request.url.startsWith("/api/analyze")) {
      await proxyApi(request, response);
    } else {
      await serveStatic(request, response);
    }
  } catch (error) {
    console.error(error);
    response.writeHead(500).end("Internal server error");
  }
}).listen(port, () => {
  console.log(`GenoScene development server: http://localhost:${port}`);
});
