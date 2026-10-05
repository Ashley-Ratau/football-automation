const fs = require("fs");
const https = require("https");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const TOKEN_PATH = path.join(ROOT, "work", "secrets", "youtube_token_youtube_only.json");
const CLIENT_PATH = path.join(ROOT, "work", "secrets", "youtube_oauth_client.json");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function requestJson({ method, hostname, path: requestPath, headers = {}, body }) {
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        method,
        hostname,
        path: requestPath,
        headers: {
          "User-Agent": "football-channel-uploader",
          ...headers,
        },
      },
      (res) => {
        const chunks = [];
        res.on("data", (chunk) => chunks.push(chunk));
        res.on("end", () => {
          const text = Buffer.concat(chunks).toString("utf8");
          let data = text;
          try {
            data = text ? JSON.parse(text) : {};
          } catch {
            // Keep raw text for non-JSON error responses.
          }
          if (res.statusCode < 200 || res.statusCode >= 300) {
            reject(new Error(`HTTP ${res.statusCode}: ${typeof data === "string" ? data : JSON.stringify(data)}`));
            return;
          }
          resolve(data);
        });
      },
    );
    req.on("error", reject);
    if (body) req.write(body);
    req.end();
  });
}

function clientCredentials() {
  const raw = readJson(CLIENT_PATH);
  const client = raw.installed || raw.web;
  if (!client || !client.client_id || !client.client_secret) {
    throw new Error("OAuth client JSON is missing client_id/client_secret.");
  }
  return client;
}

async function accessToken() {
  const token = readJson(TOKEN_PATH);
  if (!token.refresh_token) {
    throw new Error("Saved YouTube token is missing refresh_token.");
  }
  const client = clientCredentials();
  const body = new URLSearchParams({
    client_id: client.client_id,
    client_secret: client.client_secret,
    refresh_token: token.refresh_token,
    grant_type: "refresh_token",
  }).toString();
  const data = await requestJson({
    method: "POST",
    hostname: "oauth2.googleapis.com",
    path: "/token",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "Content-Length": Buffer.byteLength(body),
    },
    body,
  });
  return data.access_token;
}

function multipartBody(metadata, videoPath) {
  const boundary = `codex_boundary_${Date.now()}`;
  const video = fs.readFileSync(videoPath);
  const head = Buffer.from(
    `--${boundary}\r\n` +
      "Content-Type: application/json; charset=UTF-8\r\n\r\n" +
      `${JSON.stringify(metadata)}\r\n` +
      `--${boundary}\r\n` +
      "Content-Type: video/mp4\r\n\r\n",
    "utf8",
  );
  const tail = Buffer.from(`\r\n--${boundary}--\r\n`, "utf8");
  return {
    boundary,
    body: Buffer.concat([head, video, tail]),
  };
}

async function upload() {
  const [, , videoArg, titleArg, descriptionArg, tagsArg] = process.argv;
  if (!videoArg || !titleArg) {
    throw new Error("Usage: node work/upload_youtube_node.js <video> <title> [description] [comma,tags]");
  }
  const videoPath = path.resolve(videoArg);
  if (!fs.existsSync(videoPath)) {
    throw new Error(`Video not found: ${videoPath}`);
  }
  const token = await accessToken();
  const metadata = {
    snippet: {
      title: titleArg,
      description: descriptionArg || "",
      tags: tagsArg ? tagsArg.split(",").map((tag) => tag.trim()).filter(Boolean) : undefined,
      categoryId: "17",
    },
    status: {
      privacyStatus: "public",
      selfDeclaredMadeForKids: false,
    },
  };
  if (!metadata.snippet.tags) delete metadata.snippet.tags;

  const { boundary, body } = multipartBody(metadata, videoPath);
  const result = await requestJson({
    method: "POST",
    hostname: "www.googleapis.com",
    path: "/upload/youtube/v3/videos?part=snippet,status&uploadType=multipart",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": `multipart/related; boundary=${boundary}`,
      "Content-Length": body.length,
    },
    body,
  });
  console.log(JSON.stringify({
    id: result.id,
    privacyStatus: result.status && result.status.privacyStatus,
    title: result.snippet && result.snippet.title,
    url: result.id ? `https://www.youtube.com/watch?v=${result.id}` : null,
  }, null, 2));
}

upload().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
