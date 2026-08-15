const express = require("express");
const path = require("path");
require("dotenv").config({ path: path.join(__dirname, "..", ".env") });

const app = express();
const PORT = process.env.PORT || 3000;
const API_URL = process.env.API_URL || "http://localhost:8000";

const frontendPath = path.join(__dirname, "..", "frontend");

app.use("/api", async (req, res) => {
  try {
    const headers = { ...req.headers };
    delete headers.host;
    delete headers.connection;

    const init = {
      method: req.method,
      headers,
    };

    if (!["GET", "HEAD"].includes(req.method)) {
      const chunks = [];
      for await (const chunk of req) {
        chunks.push(chunk);
      }
      init.body = Buffer.concat(chunks);
    }

    const targetUrl = `${API_URL}${req.originalUrl}`;
    const targetResponse = await fetch(targetUrl, init);

    const responseHeaders = {};
    targetResponse.headers.forEach((value, key) => {
      const lower = key.toLowerCase();
      if (!["content-encoding", "transfer-encoding", "connection", "content-length"].includes(lower)) {
        responseHeaders[key] = value;
      }
    });

    res.status(targetResponse.status);
    Object.entries(responseHeaders).forEach(([key, value]) => {
      res.setHeader(key, value);
    });

    const buffer = Buffer.from(await targetResponse.arrayBuffer());
    if (buffer.length > 0) {
      res.send(buffer);
    } else {
      res.end();
    }
  } catch (error) {
    console.error("API proxy error:", error);
    res.status(502).json({ detail: "Unable to reach backend service" });
  }
});

app.use(express.static(frontendPath));

app.get("/", (_req, res) => {
  res.sendFile(path.join(frontendPath, "index.html"));
});

app.listen(PORT, () => {
  console.log(`Hackathon site running at http://localhost:${PORT}`);
  console.log(`Proxying /api/* to ${API_URL}`);
});
