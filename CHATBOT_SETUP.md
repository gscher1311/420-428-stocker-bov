# LAAA BOV AI Chatbot - Setup Guide

Everything is built. Follow these steps to go live.

---

## Step 1: Create Accounts and Get API Keys (15 min)

You need keys from 2 new services (you already have Anthropic and Cloudflare).

### Voyage AI (free)
1. Go to https://dash.voyageai.com
2. Sign up / log in
3. Go to API Keys, click "Create API Key"
4. Copy the key (starts with `pa-`)

### Pinecone (free)
1. Go to https://app.pinecone.io
2. Sign up / log in
3. Click "Create Index" with these settings:
   - **Name:** `laaa-bov`
   - **Dimensions:** `1024`
   - **Metric:** `cosine`
   - **Cloud:** AWS
   - **Region:** `us-east-1` (free tier)
4. Go to API Keys, copy your key (starts with `pcsk_`)
5. On the index page, copy the **Host URL** (looks like `https://laaa-bov-xxxxxxx.svc.aped-xxxx.pinecone.io`)

---

## Step 2: Set Up Your .env File (2 min)

Copy the example and fill in your keys:

```
copy .env.example .env
```

Edit `.env` with your actual keys:

```
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
VOYAGE_API_KEY=pa-YOUR_KEY_HERE
PINECONE_API_KEY=pcsk_YOUR_KEY_HERE
PINECONE_INDEX_HOST=https://laaa-bov-YOUR_INDEX.svc.aped-XXXX.pinecone.io
```

---

## Step 3: Install Python Dependencies (2 min)

```
pip install -r requirements.txt
```

This installs: pymupdf, python-docx, openpyxl, voyageai, pinecone, tiktoken, python-dotenv

---

## Step 4: Deploy the Cloudflare Worker (5 min)

```
cd laaa-chat-worker
npm install
npx wrangler login          # if not already logged in
npx wrangler secret put ANTHROPIC_API_KEY     # paste your Anthropic key
npx wrangler secret put VOYAGE_API_KEY        # paste your Voyage key
npx wrangler secret put PINECONE_API_KEY      # paste your Pinecone key
npx wrangler secret put PINECONE_INDEX_HOST   # paste your Pinecone host URL
npx wrangler deploy
```

Note the deployed URL (e.g., `https://laaa-chat-worker.laaa-team.workers.dev`).
If it differs from what's in `build_bov_v2.py`, update `CHAT_WORKER_URL`.

### Set Up Rate Limiting (recommended)
In the Cloudflare dashboard:
1. Go to Security > WAF > Rate limiting rules
2. Add a rule: 30 requests per minute per IP to your worker URL
3. This prevents abuse and controls API costs

---

## Step 5: Build the BOV with Chatbot (5 min)

```
cd C:\Users\gscher\stocker-bov-clone
python build_bov_v2.py
```

This will:
1. Build the BOV HTML (as before)
2. Parse all 26 source documents in `docs/`
3. Chunk them into ~100-150 pieces
4. Generate embeddings via Voyage AI
5. Upload vectors to Pinecone (namespace: `stocker-420`)
6. Inject the chat widget into `index.html`
7. Write the final file

You'll see progress messages for each step.

---

## Step 6: Push to GitHub and Go Live

```
git add -A
git commit -m "Add AI chatbot with RAG pipeline"
git push
```

Visit https://420428stocker.laaa.com and click the chat bubble!

---

## For Future BOVs

When you create a new BOV, just change 3 lines in `build_bov_v2.py`:

```python
BOV_NAMESPACE = "beach-2341"              # unique per property
PROPERTY_DISPLAY_NAME = "2341 Beach Ave"  # shown in chat header
STARTER_QUESTIONS = [...]                 # tailored to that property
```

Also update the `build_data` dict with that property's financials and comps.

Then run the build script. The Cloudflare Worker serves all properties
automatically (it routes by namespace). No Worker changes needed.

---

## Troubleshooting

**Build fails with "RAG dependencies not installed"**
- Run `pip install -r requirements.txt`
- The build will still generate the website without the chatbot

**Build fails with API errors**
- Check your `.env` keys are correct
- The build will still generate the website without the chatbot
- Check: `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('VOYAGE_API_KEY')[:10])"`

**Chat widget appears but responses fail**
- Check the browser console (F12) for error messages
- Verify the Worker is deployed: visit `https://laaa-chat-worker.laaa-team.workers.dev/` (should return 404 JSON)
- Verify Worker secrets are set correctly

**Scanned PDFs return no content**
- The assessor portal PDFs are likely scanned images
- Option A: Install Tesseract OCR (https://github.com/tesseract-ocr/tesseract) and add to PATH
- Option B: Manually export the key info to a .txt file in `docs/` (simpler)

**To disable the chatbot temporarily**
- Set `ENABLE_CHATBOT = False` in `build_bov_v2.py` and rebuild

---

## Cost Reference

| Service | Monthly Cost | Per-Question Cost |
|---------|-------------|-------------------|
| Voyage AI | $0 (free tier: 50M tokens/mo) | ~$0.0001 |
| Pinecone | $0 (free tier: 100K vectors) | $0 |
| Cloudflare Worker | $0 (free tier: 100K req/day) | $0 |
| Claude Haiku | Pay-per-use | ~$0.003/question |
| Claude Sonnet | Pay-per-use | ~$0.015/question |

To switch to Sonnet, change `CLAUDE_MODEL` in `laaa-chat-worker/src/index.js`.
