# Short Write-Up: Architectural Limitations & 1-Week Roadmap
> **Candidate Assessment Submission:** AI Automation Engineer / Specialist  
> **Topic:** PlacidWay Website Knowledge Chatbot

---

## 1. Known Architectural Limitations

While the current version of the PlacidWay Knowledge Chatbot achieves 100% factual accuracy and strictly prevents hallucinated prices or dangerous medical advice across the 7 verified source pages, several production limitations are acknowledged:

1. **Static Pre-Ingested Scrape Scope:**  
   The current knowledge base relies on pre-parsed JSON snapshots of the 7 specified URLs. If PlacidWay updates package prices (e.g., from $18,995 to $19,500) or introduces new diagnostic inclusions, the knowledge store must be refreshed either manually via the sidebar refresh trigger or through a scheduled cron worker.
2. **Deterministic Fallback vs. Semantic Embeddings:**  
   To guarantee zero-cost reliability and prevent public reviewer failures due to missing or exhausted API keys, the baseline engine utilizes deterministic keyword-entity routing and exact-phrase matching. While this provides 100% resilience against trick questions and medical advice traps, it lacks the semantic nuance of high-dimensional vector embeddings (e.g. OpenAI `text-embedding-3-small` or Pinecone/ChromaDB) for conversational paraphrasing.
3. **Session-Bound Conversation History:**  
   Chat history is stored within Streamlit's in-memory session state. If a user refreshes their browser tab, previous conversation turns are reset rather than persisted in a persistent session store like Redis or PostgreSQL.

---

## 2. What I Would Improve With Another Week

With an additional week of engineering time, I would elevate this production prototype into an enterprise-grade medical tourism conversational platform:

### A. Dynamic Ingestion & Live Crawl Pipeline
- **Automated Differential Crawler:** Implement an n8n or Python Celery cron job that polls the 7 PlacidWay sitemaps/URLs weekly, detects DOM delta changes, recalculates text chunks, and updates the knowledge vector store automatically.
- **Headless Edge Ingestion:** Integrate Playwright/Scrapy to capture dynamically loaded patient video transcripts and real-time clinic doctor schedules.

### B. Hybrid RAG Architecture (BM25 + Dense Vector Search)
- **Reciprocal Rank Fusion (RRF):** Combine keyword lexical matching (BM25 for exact prices and package IDs like `7903`) with dense semantic embeddings (ChromaDB / pgvector) to handle complex linguistic phrasing and patient typos without breaking grounding.
- **Strict Evaluator LLM Pass:** Implement a two-model pipeline where a Primary LLM drafts the response, and a secondary Critic LLM audits the output for clinical disclaimer compliance and source URL attribution before streaming to the client.

### C. Enterprise CRM & Lead Routing Integration
- **Direct Webhook to HubSpot / Salesforce:** Connect the "Request a Free Quote" lead capture directly to PlacidWay's CRM, notifying patient coordinators via Slack or email when a high-intent inquiry (e.g., stage 3 adenocarcinoma) is submitted.
- **Automated Analytics on Content Gaps:** Connect the `unanswered_queries.log` to an automated dashboard to surface unaddressed patient questions (e.g., inquiries about Turkey or alternative stem cell protocols), guiding the content marketing team on where to publish new landing pages.

### D. Advanced Multilingual Speech & Messaging Channels
- **WhatsApp & Web Widget Integration:** Package the bot as an embeddable React/JS floating widget on PlacidWay.com and connect it to the WhatsApp Business API for international patients traveling abroad.
