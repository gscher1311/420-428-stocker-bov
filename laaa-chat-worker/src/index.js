/**
 * LAAA BOV Chat Worker
 * ====================
 * Cloudflare Worker that powers the AI chatbot on every BOV website.
 * Handles: CORS, Voyage AI embedding, Pinecone vector search, Claude streaming.
 *
 * Secrets (set via `npx wrangler secret put <NAME>`):
 *   - ANTHROPIC_API_KEY
 *   - VOYAGE_API_KEY
 *   - PINECONE_API_KEY
 *   - PINECONE_INDEX_HOST
 *
 * Rate limiting: Use Cloudflare dashboard rate limiting rules (stateless Workers
 * cannot use in-memory counters). Configure: Security > WAF > Rate limiting rules.
 */

// ============================================================
// CONFIGURATION
// ============================================================

const CLAUDE_MODEL = "claude-3-5-haiku-20241022"; // fast + cheap
const CLAUDE_MAX_TOKENS = 1024;
const VOYAGE_MODEL = "voyage-3";
const PINECONE_TOP_K = 8;  // Number of chunks to retrieve
const REQUEST_TIMEOUT_MS = 15000; // 15s timeout per external API call
const MAX_HISTORY_TURNS = 6; // Keep last 6 turns (12 messages) max

const SYSTEM_PROMPT = `You are a knowledgeable real estate investment assistant for a specific Broker Opinion of Value (BOV) property prepared by the LAAA Team at Marcus & Millichap.

You have access to detailed property documents including financial analysis, rent rolls, comparable sales, zoning research, permit history, and market data.

Rules:
1. ONLY answer based on the provided document excerpts below.
2. If the answer is not in the provided context, say: "I don't have that specific information in the BOV materials. You may want to reach out to the LAAA Team directly for more details."
3. NEVER fabricate financial figures, prices, cap rates, or property details. Accuracy is critical for investment decisions.
4. When citing information, mention the source naturally (e.g., "According to the pricing model..." or "The assessor records show...").
5. Format financial figures clearly with dollar signs and commas (e.g., $9,350,000).
6. Be concise but thorough. Use bullet points for comparisons and lists.
7. Be professional and helpful. You represent the LAAA Team.`;


// ============================================================
// CORS HANDLING
// ============================================================

/**
 * Validate CORS origin. Allows any *.laaa.com subdomain so new BOV sites
 * don't require a Worker redeployment.
 */
function getCorsHeaders(request) {
    const origin = request.headers.get("Origin") || "";
    const allowed =
        origin.endsWith(".laaa.com") ||
        origin.endsWith(".github.io") ||
        origin === "http://localhost:8080" ||
        origin === "http://127.0.0.1:8080" ||
        origin.startsWith("http://localhost:") ||
        origin.startsWith("http://127.0.0.1:");

    return {
        "Access-Control-Allow-Origin": allowed ? origin : "",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "86400",
    };
}


// ============================================================
// FETCH WITH TIMEOUT
// ============================================================

async function fetchWithTimeout(url, options, timeoutMs = REQUEST_TIMEOUT_MS) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
        });
        return response;
    } finally {
        clearTimeout(timeout);
    }
}


// ============================================================
// VOYAGE AI: EMBED QUERY
// ============================================================

async function embedQuestion(question, env) {
    const response = await fetchWithTimeout(
        "https://api.voyageai.com/v1/embeddings",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${env.VOYAGE_API_KEY}`,
            },
            body: JSON.stringify({
                model: VOYAGE_MODEL,
                input: [question],
                input_type: "query",
            }),
        }
    );

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`Voyage AI error (${response.status}): ${text}`);
    }

    const data = await response.json();
    return data.data[0].embedding;
}


// ============================================================
// PINECONE: VECTOR SEARCH
// ============================================================

async function searchVectors(embedding, namespace, env) {
    const host = env.PINECONE_INDEX_HOST;

    const response = await fetchWithTimeout(
        `${host}/query`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Api-Key": env.PINECONE_API_KEY,
            },
            body: JSON.stringify({
                namespace: namespace,
                vector: embedding,
                topK: PINECONE_TOP_K,
                includeMetadata: true,
            }),
        }
    );

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`Pinecone error (${response.status}): ${text}`);
    }

    const data = await response.json();
    return data.matches || [];
}


// ============================================================
// CLAUDE: STREAMING RESPONSE WITH PROMPT CACHING
// ============================================================

async function streamClaude(question, context, history, env) {
    // Build the context block from retrieved chunks
    const contextText = context
        .map((match, i) => {
            const m = match.metadata || {};
            return `[Source: ${m.source || "Unknown"} | ${m.page || ""}]\n${m.text || ""}`;
        })
        .join("\n\n---\n\n");

    // Trim history to max turns
    let trimmedHistory = history || [];
    if (trimmedHistory.length > MAX_HISTORY_TURNS * 2) {
        trimmedHistory = trimmedHistory.slice(-(MAX_HISTORY_TURNS * 2));
    }

    // Build messages array
    const messages = [
        ...trimmedHistory,
        {
            role: "user",
            content: `Here are the relevant document excerpts for this question:\n\n${contextText}\n\n---\n\nQuestion: ${question}`,
        },
    ];

    const response = await fetchWithTimeout(
        "https://api.anthropic.com/v1/messages",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": env.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "anthropic-beta": "prompt-caching-2024-07-31",
            },
            body: JSON.stringify({
                model: CLAUDE_MODEL,
                max_tokens: CLAUDE_MAX_TOKENS,
                stream: true,
                system: [
                    {
                        type: "text",
                        text: SYSTEM_PROMPT,
                        cache_control: { type: "ephemeral" },
                    },
                ],
                messages: messages,
            }),
        },
        25000 // Claude streaming gets a longer timeout
    );

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`Claude error (${response.status}): ${text}`);
    }

    return response;
}


// ============================================================
// SSE STREAM TRANSFORMER
// ============================================================

/**
 * Transform Claude's SSE stream into our simplified client format.
 * Client receives:
 *   data: {"type": "sources", "sources": [...]}
 *   data: {"type": "text", "content": "..."}
 *   data: [DONE]
 */
function createStreamTransformer(sources) {
    let buffer = "";

    return new TransformStream({
        start(controller) {
            // Send sources first so the client has them before text starts
            const sourcesData = sources.map((m) => ({
                source: m.metadata?.source || "",
                page: m.metadata?.page || "",
            }));
            controller.enqueue(
                `data: ${JSON.stringify({ type: "sources", sources: sourcesData })}\n\n`
            );
        },

        transform(chunk, controller) {
            buffer += new TextDecoder().decode(chunk);
            const lines = buffer.split("\n");
            buffer = lines.pop() || ""; // Keep incomplete line in buffer

            for (const line of lines) {
                if (!line.startsWith("data: ")) continue;
                const data = line.substring(6).trim();
                if (!data || data === "[DONE]") continue;

                try {
                    const parsed = JSON.parse(data);

                    // Extract text delta from Claude's streaming format
                    if (parsed.type === "content_block_delta" && parsed.delta?.text) {
                        controller.enqueue(
                            `data: ${JSON.stringify({ type: "text", content: parsed.delta.text })}\n\n`
                        );
                    }

                    // Handle stop
                    if (parsed.type === "message_stop") {
                        controller.enqueue("data: [DONE]\n\n");
                    }
                } catch (e) {
                    // Skip malformed JSON
                }
            }
        },

        flush(controller) {
            // Process any remaining buffer
            if (buffer.trim()) {
                const line = buffer.trim();
                if (line.startsWith("data: ")) {
                    const data = line.substring(6).trim();
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.type === "content_block_delta" && parsed.delta?.text) {
                            controller.enqueue(
                                `data: ${JSON.stringify({ type: "text", content: parsed.delta.text })}\n\n`
                            );
                        }
                    } catch (e) {}
                }
            }
            controller.enqueue("data: [DONE]\n\n");
        },
    });
}


// ============================================================
// REQUEST HANDLER
// ============================================================

export default {
    async fetch(request, env) {
        const corsHeaders = getCorsHeaders(request);

        // Handle CORS preflight
        if (request.method === "OPTIONS") {
            return new Response(null, {
                status: 204,
                headers: corsHeaders,
            });
        }

        // Only accept POST to /chat
        const url = new URL(request.url);
        if (request.method !== "POST" || url.pathname !== "/chat") {
            return new Response(JSON.stringify({ error: "Not found" }), {
                status: 404,
                headers: { ...corsHeaders, "Content-Type": "application/json" },
            });
        }

        // Check CORS
        if (!corsHeaders["Access-Control-Allow-Origin"]) {
            return new Response(JSON.stringify({ error: "Origin not allowed" }), {
                status: 403,
                headers: { "Content-Type": "application/json" },
            });
        }

        try {
            // Parse request body
            const body = await request.json();
            const { question, namespace, history } = body;

            if (!question || !namespace) {
                return new Response(
                    JSON.stringify({ error: "Missing 'question' or 'namespace'" }),
                    {
                        status: 400,
                        headers: { ...corsHeaders, "Content-Type": "application/json" },
                    }
                );
            }

            // Validate question length
            if (question.length > 2000) {
                return new Response(
                    JSON.stringify({ error: "Question too long (max 2000 characters)" }),
                    {
                        status: 400,
                        headers: { ...corsHeaders, "Content-Type": "application/json" },
                    }
                );
            }

            // Step 1: Embed the question
            const embedding = await embedQuestion(question, env);

            // Step 2: Search Pinecone
            const matches = await searchVectors(embedding, namespace, env);

            if (matches.length === 0) {
                // No relevant documents found - return a direct response
                const noContextMsg =
                    "I don't have any information about that in the BOV materials for this property. " +
                    "Could you try rephrasing your question, or ask about the property's financials, " +
                    "comparable sales, development potential, or location details?";
                return new Response(
                    `data: ${JSON.stringify({ type: "sources", sources: [] })}\n\ndata: ${JSON.stringify({ type: "text", content: noContextMsg })}\n\ndata: [DONE]\n\n`,
                    {
                        headers: {
                            ...corsHeaders,
                            "Content-Type": "text/event-stream",
                            "Cache-Control": "no-cache",
                            Connection: "keep-alive",
                        },
                    }
                );
            }

            // Step 3: Stream Claude response
            const claudeResponse = await streamClaude(
                question,
                matches,
                history || [],
                env
            );

            // Transform Claude's stream into our client format
            const transformer = createStreamTransformer(matches);
            const transformedStream = claudeResponse.body.pipeThrough(transformer);

            // Encode to bytes for Response
            const encoder = new TextEncoder();
            const encodedStream = transformedStream.pipeThrough(
                new TransformStream({
                    transform(chunk, controller) {
                        controller.enqueue(
                            typeof chunk === "string" ? encoder.encode(chunk) : chunk
                        );
                    },
                })
            );

            return new Response(encodedStream, {
                headers: {
                    ...corsHeaders,
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    Connection: "keep-alive",
                },
            });
        } catch (error) {
            console.error("Chat Worker error:", error);

            // Determine user-friendly error message
            let errorMsg = "Sorry, something went wrong. Please try again in a moment.";
            if (error.name === "AbortError") {
                errorMsg = "The request took too long. Please try a simpler question.";
            }

            // Return error as SSE so the client can display it nicely
            return new Response(
                `data: ${JSON.stringify({ type: "error", message: errorMsg })}\n\ndata: [DONE]\n\n`,
                {
                    headers: {
                        ...corsHeaders,
                        "Content-Type": "text/event-stream",
                        "Cache-Control": "no-cache",
                    },
                }
            );
        }
    },
};
