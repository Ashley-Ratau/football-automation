const fs = require("fs");
const https = require("https");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const TOKEN_PATH = path.join(ROOT, "work", "secrets", "youtube_token_youtube_only.json");
const CLIENT_PATH = path.join(ROOT, "work", "secrets", "youtube_oauth_client.json");
const CHUNK_SIZE = 2 * 1024 * 1024;

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function request({ method, hostname, path: requestPath, headers = {}, body }) {
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        method,
        hostname,
        path: requestPath,
        headers: {
          "User-Agent": "football-channel-resumable-uploader",
          ...headers,
        },
      },
      (res) => {
        const chunks = [];
        res.on("data", (chunk) => chunks.push(chunk));
        res.on("end", () => {
          const text = Buffer.concat(chunks).toString("utf8");
          resolve({ statusCode: res.statusCode, headers: res.headers, text });
        });
      },
    );
    req.setTimeout(120000, () => req.destroy(new Error("Request timed out")));
    req.on("error", reject);
    if (body) req.write(body);
    req.end();
  });
}

function parseJsonResponse(res) {
  if (!res.text) return {};
  try {
    return JSON.parse(res.text);
  } catch {
    return res.text;
  }
}

async function requestJson(options) {
  const res = await request(options);
  const data = parseJsonResponse(res);
  if (res.statusCode < 200 || res.statusCode >= 300) {
    throw new Error(`HTTP ${res.statusCode}: ${typeof data === "string" ? data : JSON.stringify(data)}`);
  }
  return data;
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
  if (!token.refresh_token) throw new Error("Saved YouTube token is missing refresh_token.");
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

async function startSession(token, metadata, fileSize) {
  const body = JSON.stringify(metadata);
  const res = await request({
    method: "POST",
    hostname: "www.googleapis.com",
    path: "/upload/youtube/v3/videos?part=snippet,status&uploadType=resumable",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json; charset=UTF-8",
      "Content-Length": Buffer.byteLength(body),
      "X-Upload-Content-Type": "video/mp4",
      "X-Upload-Content-Length": fileSize,
    },
    body,
  });
  if (res.statusCode < 200 || res.statusCode >= 300) {
    throw new Error(`Session start failed HTTP ${res.statusCode}: ${res.text}`);
  }
  const location = res.headers.location;
  if (!location) throw new Error("YouTube did not return a resumable upload location.");
  return new URL(location);
}

async function uploadChunk(sessionUrl, token, chunk, start, end, total) {
  const res = await request({
    method: "PUT",
    hostname: sessionUrl.hostname,
    path: `${sessionUrl.pathname}${sessionUrl.search}`,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Length": chunk.length,
      "Content-Type": "video/mp4",
      "Content-Range": `bytes ${start}-${end}/${total}`,
    },
    body: chunk,
  });
  if (res.statusCode === 308) return null;
  if (res.statusCode >= 200 && res.statusCode < 300) return parseJsonResponse(res);
  throw new Error(`Chunk upload failed HTTP ${res.statusCode}: ${res.text}`);
}

async function upload() {
  const [, , videoArg, titleArg, descriptionArg = "", tagsArg = "", privacyArg = "public"] = process.argv;
  if (!videoArg || !titleArg) {
    throw new Error("Usage: node work/upload_youtube_resumable_node.js <video> <title> [description] [comma,tags] [privacy]");
  }
  const privacy = ["private", "unlisted", "public"].includes(privacyArg) ? privacyArg : "public";
  const videoPath = path.resolve(videoArg);
  if (!fs.existsSync(videoPath)) throw new Error(`Video not found: ${videoPath}`);
  const file = fs.readFileSync(videoPath);
  const token = await accessToken();
  const metadata = {
    snippet: {
      title: titleArg,
      description: descriptionArg,
      categoryId: "17",
    },
    status: {
      privacyStatus: privacy,
      selfDeclaredMadeForKids: false,
    },
  };
  const tags = tagsArg.split(",").map((tag) => tag.trim()).filter(Boolean);
  if (tags.length) metadata.snippet.tags = tags;

  const sessionUrl = await startSession(token, metadata, file.length);
  let result = null;
  for (let start = 0; start < file.length; start += CHUNK_SIZE) {
    const end = Math.min(start + CHUNK_SIZE, file.length) - 1;
    const chunk = file.subarray(start, end + 1);
    result = await uploadChunk(sessionUrl, token, chunk, start, end, file.length);
    console.error(`uploaded ${end + 1}/${file.length}`);
  }
  if (!result || !result.id) throw new Error("Upload finished without a video id.");
  console.log(JSON.stringify({
    id: result.id,
    privacyStatus: result.status && result.status.privacyStatus,
    title: result.snippet && result.snippet.title,
    url: `https://www.youtube.com/watch?v=${result.id}`,
  }, null, 2));
}

upload().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
