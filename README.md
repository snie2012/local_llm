# Qwen + llama.cpp Internet-Enabled Gateway

This repo is a small, incremental setup that:

1. Runs a Qwen GGUF model with `llama.cpp`.
2. Adds a lightweight gateway that exposes an OpenAI-compatible endpoint.
3. Enables a simple `web_fetch` tool call so the model can access the internet.
4. Makes it easy to share the service with your phone or friends.

## Step 1: Download a Qwen GGUF model

Place a Qwen GGUF file in `./models`. Example (edit for the exact model/version you want):

```
models/qwen2.5-7b-instruct-q4_k_m.gguf
```

## Step 2: Start the stack (simple)

```
docker compose up --build
```

This starts:

- `llama` on `http://localhost:8080`
- `gateway` on `http://localhost:8000`

## Step 3: Run a quick chat

```
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Say hello in 5 words."}
    ]
  }'
```

## Step 4: Let the model use the internet

The gateway exposes a `web_fetch` tool. When the model calls it, the gateway fetches the URL and returns the response body.

```
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen",
    "messages": [
      {"role": "system", "content": "Use tools when needed."},
      {"role": "user", "content": "Fetch https://example.com and summarize it."}
    ]
  }'
```

## Step 5: Share the service with your phone/friends

You can expose the gateway port (`8000`) using a tunnel such as:

- **Cloudflare Tunnel** (recommended for stability)
- **ngrok** or **localtunnel**

Example (ngrok):

```
ngrok http 8000
```

Then call the public URL from your phone:

```
https://<your-ngrok-subdomain>.ngrok-free.app/v1/chat/completions
```

## Next increments (optional)

- Add authentication to the gateway (API key).
- Add a more structured web search tool (SerpAPI, Tavily, etc.).
- Persist logs and chat history.
