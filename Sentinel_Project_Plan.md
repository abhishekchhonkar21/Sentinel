# SENTINEL
### Autonomous Incident-Investigation Agent
*An SRE Copilot Built on Small Models, Not Big Reasoning*

**Project Design Document & Build Roadmap**
Owner: Abhishek Singh
Version 2.0 — Living Document (Markdown edition)

> **How to use this document**
> This is a living reference, not a rigid spec. Treat every section as a default you can override once you're building and learn more. Section 12 (Future Scope) exists specifically so you can bolt on new capability — GraphRAG, A2A, a skill library, a model-cascade router — without re-architecting the core. Update this doc as decisions change; it should always reflect what you're actually building, not the original plan. Keep it in your repo root as `PLAN.md` and commit changes to it alongside code changes — a version-controlled plan doubles as a build log for future-you and for interviewers.

---

## Table of Contents

1. [The Real-World Problem](#1-the-real-world-problem)
2. [Project Vision & What "Done" Looks Like](#2-project-vision--what-done-looks-like)
3. [System Architecture](#3-system-architecture)
4. [Tech Stack](#4-tech-stack)
5. [The Toy System & Fault Injection Strategy](#5-the-toy-system--fault-injection-strategy)
6. [Agent Communication Contracts](#6-agent-communication-contracts)
7. [Evaluation Plan](#7-evaluation-plan-your-resume-numbers-live-here)
8. [Observability for the System Itself](#8-observability-for-the-system-itself)
9. [Detailed Build Roadmap (12 Weeks)](#9-detailed-build-roadmap-12-weeks)
10. [Resume Positioning](#10-resume-positioning)
11. [Scope Risks & How to Manage Them](#11-scope-risks--how-to-manage-them)
12. [Future Scope — Designed-In Extension Points](#12-future-scope--designed-in-extension-points)
13. [Appendix: MongoDB Data Model Reference](#13-appendix-mongodb-data-model-reference)

---

## 1. The Real-World Problem

On-call engineers get paged for anomalies that are already buried in logs, metrics, and traces. By the time a human has correlated the right signals — which service, which deploy, which downstream dependency — 20-30 minutes have often passed. In production environments this delay is measured in customer impact and revenue, which is why every major cloud/dev-tool vendor (Datadog, PagerDuty, New Relic, Honeycomb) is racing to build "AI-assisted incident response" right now.

Most portfolio "agentic AI" projects point an LLM at a chat interface and call it done. That fails here on purpose: this project is designed so the LLM is the last, thinnest layer in the pipeline — not the thing doing the hard cognitive work. That constraint is not a limitation you're hiding; it's the actual point of the project.

> **The core thesis**
> Detection and root-cause reasoning should be handled by small, purpose-built ML models and deterministic evidence-gathering. The LLM's only job is to turn already-correct evidence into a clear, human-readable report. This lets the system work well on free-tier models (Groq Llama 3.1 8B, Gemini Flash) because the LLM is never asked to do open-ended reasoning it isn't good at.

---

## 2. Project Vision & What "Done" Looks Like

Sentinel watches a toy but realistic microservice system, notices when something breaks, investigates why using evidence (not vibes), ranks the most likely root causes, and writes an incident report a human on-call engineer could act on immediately — complete with a confidence score and links to the exact logs/metrics that justify the conclusion.

### 2.1 Demo scenario (what you'll show in an interview)

1. You inject a fault into your toy system (e.g., a downstream service starts returning 500s after a bad deploy).
2. Within seconds, Sentinel's detector flags the anomaly.
3. The investigator agent pulls the deploy history, dependency graph, and correlated logs/metrics automatically.
4. The hypothesis-ranking agent scores 2-3 candidate root causes by evidence strength.
5. The narrator agent (free LLM) writes a 5-sentence incident summary with the top hypothesis, evidence trail, and suggested next action.
6. You show the same fault fed to a naive "dump logs into the LLM and ask what's wrong" baseline — and show it's slower, less accurate, and more token-hungry.

That last step is what makes this a systems-engineering story instead of an LLM-wrapper story.

---

## 3. System Architecture

### 3.1 High-level flow

```
Toy Microservices  --metrics/logs-->  Detector Layer (HF/classical ML)
                                            |
                                    anomaly + confidence
                                            v
                                   Investigator Agent  <-- Dependency Graph
                                            |                (Neo4j / NetworkX)
                                    evidence bundle       <-- Deploy history
                                            v                  (MongoDB)
                              Hypothesis-Ranking Agent   <-- Past incidents
                                            |                  (vector store,
                                    ranked root causes         backed by MongoDB
                                            v                  Atlas Vector Search
                                    Narrator Agent (free LLM)  or Chroma/Qdrant)
                                            |
                                    Incident Report (JSON + Markdown, stored in MongoDB)
                                            v
                          FastAPI API  -->  Grafana / simple frontend
```

### 3.2 Why each agent is a separate service, not a single LangGraph in-process node

Each stage below is designed to be an independently deployable FastAPI service with its own contract. This is what makes the A2A protocol meaningful later (Section 12) instead of decorative — the boundaries already exist; you're just formalizing the handshake.

| Agent | Core responsibility | Uses LLM? |
|---|---|---|
| Detector | Flag anomalies in logs/metrics with a confidence score | No — classical ML / small transformer |
| Investigator | Gather correlated evidence: deploys, dependency graph, related past incidents | No — deterministic retrieval |
| Hypothesis-Ranker | Score and rank candidate root causes against evidence | Optional, constrained (structured output only) |
| Narrator | Turn ranked evidence into a human-readable incident report | Yes — thin, well-scoped use of free LLM |
| Critic (v1.5) | Sanity-check narrator's claims against the evidence bundle before it reaches the user | Yes — constrained verifier prompt |

---

## 4. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Backend framework | FastAPI | One service per agent; shared Pydantic schemas |
| Agent orchestration | LangGraph | Orchestrates the pipeline; each node calls out to the corresponding FastAPI service |
| Detector models | Hugging Face (e.g., DistilBERT/LogBERT-style log classifier, Isolation Forest for metrics) | Fine-tune small, keep inference cheap |
| Dependency graph | Neo4j Aura free tier or NetworkX in-memory | NetworkX is enough for v1; Neo4j if you want graph-query practice |
| **Primary datastore** | **MongoDB (Atlas free tier, M0 cluster)** | Stores deploy history, anomaly events, evidence bundles, incident reports, and fault-catalogue ground truth. Document model fits this domain well since every evidence bundle and incident report is a naturally nested JSON-like document, not a fixed-schema row |
| **Similarity search (past incidents)** | **MongoDB Atlas Vector Search** on incident-report embeddings (fallback: Chroma/Qdrant local if you stay off Atlas) | One less moving part if you keep everything in Mongo; Atlas free tier supports vector search on M0/M10 |
| LLM | Groq (Llama 3.1 8B/70B free tier) primary, Gemini Flash as fallback | Keep prompts structured; never open-ended "figure it out" |
| Toy system under test | 3-5 tiny FastAPI services with Docker Compose | You need to control fault injection precisely |
| Metrics/logging | Prometheus + Grafana (free/self-hosted) or Grafana Cloud free tier | Also used for your own agent observability — token cost, latency, accuracy |
| Deployment | Render (free tier) for services, Render/local Docker Compose for the toy system | Consider resource limits on Render free tier; document as a known constraint |
| Eval harness | Custom pytest-based suite + a results dashboard | This is what produces your resume metrics — don't skip it |

> **Why MongoDB over a relational store here:** deploy diffs, evidence bundles, and incident reports are variable-shape nested JSON by nature (different fault types carry different evidence fields). Forcing that into normalized SQL tables adds migration overhead for no real benefit at this scale; a document store matches the actual data shape and lets your schemas (Section 6) map almost 1:1 onto MongoDB documents.

---

## 5. The Toy System & Fault Injection Strategy

You need ground truth to measure accuracy, which means you need to control what breaks and why. Build a small set of services you fully understand:

- **api-gateway** — routes requests to downstream services
- **orders-service** — depends on payments-service and inventory-service
- **payments-service** — depends on a mock external payment provider
- **inventory-service** — depends on a database (MongoDB collection acting as the service's own data store)
- A simple load generator that produces realistic traffic + logs continuously

### 5.1 Fault catalogue (your ground-truth eval set)

Define 15-25 fault scenarios up front, each with a known correct root cause, stored as documents in a MongoDB `fault_catalogue` collection so your eval harness can query it directly. Examples:

- Bad deploy introduces a null-pointer-style bug in payments-service → 500s cascade to orders-service
- MongoDB connection pool exhaustion in inventory-service → latency spike, not errors
- Downstream mock payment provider starts timing out → orders-service shows errors that look like its own bug but aren't
- Memory leak simulated in orders-service → gradual latency degradation, not a sharp anomaly
- Misconfigured rate limit at api-gateway → false-positive-looking spike in 429s

This catalogue is the backbone of your entire eval story — it's what lets you say "87% top-1 root-cause accuracy across 20 injected faults" instead of "it seemed to work when I tried it."

---

## 6. Agent Communication Contracts

Define these schemas early — they are the seams that let you swap or upgrade any single agent later without touching the others. These map directly onto MongoDB document shapes (insert as-is into their respective collections) and are also your first-draft A2A message shape (Section 12.1 formalizes it further).

### 6.1 Anomaly event (Detector → Investigator) — `anomaly_events` collection

```json
{
  "_id": "ObjectId",
  "anomaly_id": "uuid",
  "service": "payments-service",
  "signal_type": "log_pattern | metric_spike",
  "confidence": 0.91,
  "detected_at": "ISO-8601",
  "raw_evidence_ref": "pointer to raw log/metric window"
}
```

### 6.2 Evidence bundle (Investigator → Hypothesis-Ranker) — `evidence_bundles` collection

```json
{
  "_id": "ObjectId",
  "anomaly_id": "uuid",
  "affected_service": "payments-service",
  "dependency_context": ["orders-service", "external-payment-mock"],
  "recent_deploys": [ { "service": "...", "deployed_at": "...", "diff_summary": "..." } ],
  "related_past_incidents": [ { "incident_id": "...", "similarity": 0.83 } ],
  "correlated_logs": [ "..." ],
  "correlated_metrics": { "latency_p99": [], "error_rate": [] }
}
```

### 6.3 Ranked hypotheses (Hypothesis-Ranker → Narrator) — `hypotheses` collection

```json
{
  "_id": "ObjectId",
  "anomaly_id": "uuid",
  "hypotheses": [
    { "cause": "Bad deploy to payments-service introduced null deref",
      "evidence_score": 0.88, "supporting_evidence": ["deploy diff", "error log pattern"] },
    { "cause": "External payment provider outage",
      "evidence_score": 0.41, "supporting_evidence": ["timeout logs"] }
  ]
}
```

### 6.4 Incident report (Narrator output) — `incident_reports` collection

```json
{
  "_id": "ObjectId",
  "anomaly_id": "uuid",
  "summary": "human-readable paragraph",
  "top_cause": "...",
  "confidence": 0.88,
  "evidence_trail": [ "link/pointer", "..." ],
  "suggested_next_action": "..."
}
```

---

## 7. Evaluation Plan (Your Resume Numbers Live Here)

This section matters more than any single agent. Numbers are what separate this project from a demo GIF.

### 7.1 Metrics to track

- **Detection precision/recall** — against your fault catalogue's known injection points and timing.
- **Top-1 / Top-3 root-cause accuracy** — does the ranked hypothesis list contain the true cause, and at what rank.
- **Mean time to diagnosis (MTTD)** — wall-clock time from fault injection to final report, compared to a human baseline you time yourself and a naive-LLM baseline.
- **Token / cost efficiency** — tokens consumed per incident, compared to the naive "dump all logs into the LLM" baseline.
- **Citation/evidence grounding accuracy** — does every claim in the narrator's report trace back to something in the evidence bundle (this is where a Critic agent earns its keep).

### 7.2 The baseline you must build (don't skip this)

Build one deliberately naive comparison: dump raw logs/metrics for the incident window directly into the free LLM and ask "what's wrong and why?" with no agent pipeline. This is 1-2 days of work and gives you the single most persuasive artifact in the whole project — a side-by-side accuracy/cost/speed table showing why the architecture earns its complexity.

---

## 8. Observability for the System Itself

Beyond monitoring the toy microservices, instrument your own agent pipeline — this is the same observability discipline your resume already claims from your job, so build it for real here.

- Per-agent latency and token usage, exported to Prometheus and visualized in Grafana
- A running accuracy dashboard against your fault catalogue (accuracy over time as you improve prompts/models)
- Structured logs for every agent hop (input, output, decision) so any incident report is fully traceable end-to-end — store these as structured documents in a MongoDB `agent_traces` collection so you can query "show me every hop for anomaly X" without grepping log files

---

## 9. Detailed Build Roadmap (12 Weeks)

Each week below lists concrete tasks, deliverables, and an explicit exit criterion. Use this as your actual sprint board — copy each week into GitHub Issues/Projects if you want ticket-level tracking.

### Week 1 — Toy system skeleton
- Scaffold 4 FastAPI services (`api-gateway`, `orders-service`, `payments-service`, `inventory-service`) with minimal real logic (not stubs — actual request routing and a couple of realistic failure-prone code paths).
- Set up MongoDB Atlas free cluster (or local `mongod` via Docker for dev); create databases/collections for `deploys`, `service_registry`, `fault_catalogue`.
- Wire `inventory-service` to read/write from MongoDB so you have a genuine dependency to break later (e.g., connection pool exhaustion is a real failure mode against a real DB).
- Write Docker Compose bringing up all 4 services + MongoDB + a simple reverse proxy.
- **Deliverable:** `docker compose up` boots a working, if boring, 4-service system that handles a basic order-placement flow end to end.
- **Exit criterion:** you can `curl` a full order flow through all 4 services and see it succeed.

### Week 2 — Load generator + fault injection harness
- Build a load generator (simple Python script using `httpx`/`locust`) producing continuous, varied traffic against the toy system.
- Build a fault-injection CLI/API (`POST /inject-fault {type, service, params}`) that can programmatically trigger each of your cataloged failure modes (bad deploy simulation, artificial latency, forced exceptions, connection pool starvation, rate-limit misconfiguration).
- Draft the full fault catalogue (15-25 entries) as documents in the MongoDB `fault_catalogue` collection, each with: `fault_id`, `description`, `injected_service`, `true_root_cause`, `expected_signal_type`.
- **Deliverable:** a script that, given a `fault_id`, injects that fault and logs the exact injection timestamp.
- **Exit criterion:** you can inject any of the first 5 cataloged faults on demand and confirm (manually, by eyeballing logs) that the toy system visibly misbehaves in the expected way.

### Week 3 — Structured logging + metrics collection
- Standardize log format across all 4 toy services (structured JSON logs: timestamp, service, level, trace_id, message, latency_ms).
- Add Prometheus client instrumentation to each service (request count, error rate, latency histograms).
- Stand up Prometheus + Grafana locally (or Grafana Cloud free tier) scraping all 4 services.
- Persist raw logs into a MongoDB `raw_logs` time-series collection (Mongo's native time-series collections are a good fit here) so the Detector/Investigator can query historical windows, not just live tail.
- **Deliverable:** a Grafana dashboard showing live latency/error-rate per service, and a queryable log store.
- **Exit criterion:** injecting a fault from Week 2 produces a visible, correlated spike in the Grafana dashboard within seconds.

### Week 4 — Detector layer v1
- Start with classical statistical detection (z-score/EWMA on latency and error-rate metrics; simple regex/keyword-based log-pattern anomaly flags) to get an end-to-end pipeline working fast.
- In parallel, evaluate 1-2 Hugging Face options for log anomaly detection (e.g., a small pretrained sentence-embedding model + clustering, or a fine-tuned DistilBERT classifier on labeled log lines you generate from your own fault catalogue).
- Build the `detector` FastAPI service: consumes recent logs/metrics windows from MongoDB, outputs `anomaly_events` documents per Section 6.1.
- **Deliverable:** detector service running continuously (polling or triggered), writing anomaly events to MongoDB.
- **Exit criterion:** run all 5 initial fault injections; log precision/recall for each (even if it's rough) — this is your first real number.

### Week 5 — Detector layer v2 + dependency graph
- Improve the detector using the HF model chosen in Week 4; fine-tune on synthetic labeled data generated from your fault catalogue if time allows.
- Build the service dependency graph: either a NetworkX graph defined in code (fast) or a small Neo4j instance (if you want graph-query practice) — encode `api-gateway → orders-service → {payments-service, inventory-service} → external-payment-mock`.
- Store deploy history as documents in a MongoDB `deploys` collection (`service`, `deployed_at`, `diff_summary`, `commit_hash`); write a small script to simulate deploys (including "bad" ones tied to your fault catalogue).
- **Deliverable:** detector v2 with measurably improved precision/recall vs v1; queryable dependency graph; deploy history store.
- **Exit criterion:** given any service name, you can programmatically retrieve its upstream/downstream dependencies and its last 5 deploys.

### Week 6 — Investigator agent
- Build the `investigator` FastAPI service: given an `anomaly_id`, deterministically assembles an `evidence_bundle` (Section 6.2) by querying the dependency graph, MongoDB `deploys` collection, correlated logs/metrics windows around the anomaly timestamp, and (stub for now) related past incidents.
- Implement the past-incident similarity lookup as a simple placeholder (return empty list) — real implementation comes in Week 9 once you have incident reports to compare against.
- Wire investigator as a LangGraph node that calls the FastAPI service.
- **Deliverable:** for every anomaly event produced in Week 5, investigator produces a complete, correct evidence bundle.
- **Exit criterion:** manually verify 5 evidence bundles against ground truth — do they contain the actual relevant deploy and dependency context every time?

### Week 7 — Hypothesis-Ranking agent
- Design the scoring logic: start with an explicit, hand-written rule-based scorer (e.g., weight recent-deploy-to-affected-service highly, weight dependency-chain-timing-correlation, weight past-incident-similarity) before reaching for any LLM involvement.
- Build the `hypothesis-ranker` FastAPI service consuming an evidence bundle and producing ranked `hypotheses` (Section 6.3).
- Only if the rule-based scorer plateaus: add a constrained LLM call that must return structured JSON matching a fixed schema (validate with Pydantic; reject and retry on malformed output) to help weigh ambiguous evidence — never let it free-reason.
- **Deliverable:** ranker producing ranked, scored hypotheses for all faults injected so far.
- **Exit criterion:** run against your first 10 fault-catalogue entries; log top-1 accuracy — second real number for your eval story.

### Week 8 — Narrator agent
- Design a tightly structured prompt template for the free LLM (Groq Llama 3.1 or Gemini Flash) that takes the ranked hypotheses + evidence bundle and outputs the exact JSON shape in Section 6.4 — no open-ended "diagnose this" prompting.
- Add prompt-level guardrails: instruct the model to only reference facts present in the evidence bundle, and validate the output schema before accepting it.
- Build the `narrator` FastAPI service; wire it as the final LangGraph node.
- **Deliverable:** full end-to-end pipeline — fault injected → anomaly detected → evidence gathered → hypotheses ranked → incident report generated — for all cataloged faults.
- **Exit criterion:** run the complete fault catalogue through the full pipeline once, saving every incident report to MongoDB `incident_reports`.

### Week 9 — Naive baseline + comparison harness + past-incident similarity
- Build the deliberately naive baseline: raw logs/metrics for the incident window → directly into the same free LLM → "what's wrong and why?" with no structure.
- Build a comparison script that runs both pipelines against the full fault catalogue and outputs a side-by-side table: top-1/top-3 accuracy, tokens used, wall-clock latency, per approach.
- Now that `incident_reports` has real data, implement the past-incident similarity lookup for real: embed each report's summary (free embedding model, e.g., a small sentence-transformer from HF) and store vectors in MongoDB Atlas Vector Search (or Chroma if staying off Atlas); wire this back into the Investigator agent from Week 6.
- **Deliverable:** the single most important artifact in the project — your pipeline-vs-baseline comparison table with real numbers.
- **Exit criterion:** a reproducible script (`python eval/run_comparison.py`) that regenerates this table from scratch on demand.

### Week 10 — Critic/verifier agent
- Build a `critic` FastAPI service: takes the narrator's incident report + the original evidence bundle, and checks every factual claim in the report against the evidence (constrained LLM call, or even a simpler string/entity-matching check as a first pass).
- Wire it in as a post-narrator LangGraph step; if the critic flags an ungrounded claim, either regenerate the narrator output with a corrective prompt or flag the report for human review.
- Measure grounding accuracy before/after adding the critic — this is your third strong number.
- **Deliverable:** critic agent integrated into the pipeline with measured before/after grounding accuracy.
- **Exit criterion:** deliberately inject a hallucination-prone case (e.g., an ambiguous evidence bundle) and confirm the critic catches it.

### Week 11 — Full observability polish + full catalogue run
- Finalize Grafana dashboards: per-agent latency, token cost per incident, running accuracy against the fault catalogue over time, MongoDB query performance if relevant.
- Run the entire fault catalogue (all 15-25 scenarios) through the full pipeline end to end in one automated script; save all results to MongoDB and export a summary report (Markdown or HTML) with final metrics.
- Fix any stragglers — fault types the pipeline handles poorly — and document *why* honestly in this plan (this becomes useful interview material too: "here's a failure mode I identified and how I'd address it").
- **Deliverable:** `python eval/run_full_catalogue.py` reproduces your complete eval report in one command.
- **Exit criterion:** the eval report shows consistent, explainable results across the whole catalogue, not just cherry-picked cases.

### Week 12 — Deployment, documentation, demo, write-up
- Deploy all FastAPI services to Render (free tier); deploy MongoDB Atlas (already cloud-hosted); keep a local Docker Compose fallback for demo reliability against Render free-tier cold starts.
- Write a thorough `README.md`: architecture diagram, setup instructions, how to run the demo, how to reproduce the eval report.
- Record a 2-3 minute demo (fault injection → live report generation) as a video/GIF for your portfolio/LinkedIn.
- Write the Medium article: focus on the "why small models, not big reasoning" thesis and the baseline-comparison numbers — this is your most differentiated content, lean into it.
- **Deliverable:** publicly accessible deployed demo + polished README + published write-up.
- **Exit criterion:** a stranger can clone the repo, follow the README, and reproduce both the demo and the eval numbers without asking you anything.

> **If you're short on time:** Weeks 1-8 are the non-negotiable core — they alone produce a working, demoable agentic system with a genuine architecture story. Weeks 9-12 (baseline comparison, critic agent, observability polish) are what turn it from "a working project" into "a project with numbers I can defend in an interview." Protect Week 9 especially — the baseline comparison is your best single artifact.

---

## 10. Resume Positioning

### 10.1 Draft bullets (refine with real numbers once you have them)

- Designed and built Sentinel, a multi-agent incident-investigation system that separates anomaly detection (lightweight ML) from root-cause reasoning (evidence-scored agent pipeline) and report generation (LLM), reducing reliance on expensive/large-model reasoning.
- Benchmarked the agent pipeline against a naive LLM-only baseline across a 20+ scenario fault catalogue, improving top-1 root-cause accuracy from X% to Y% while cutting per-incident token cost by Z%.
- Built a deterministic evidence-gathering layer (dependency graph + MongoDB-backed deploy history + past-incident vector similarity) so the LLM never reasons over raw, unstructured signals — improving groundedness of generated incident reports to X% via a dedicated critic/verifier agent.
- Instrumented the full agent pipeline with Prometheus/Grafana, tracking per-agent latency, token cost, and live accuracy against a fault-injection test harness.

### 10.2 Interview narrative to rehearse

The story you want to tell is: "I didn't have access to a frontier model, so I designed the system to not need one — classical ML and deterministic retrieval do the hard reasoning, and the LLM only narrates conclusions that are already correct. I proved this works by benchmarking against a naive LLM-only baseline across a controlled fault catalogue."

---

## 11. Scope Risks & How to Manage Them

| Risk | Mitigation |
|---|---|
| Fine-tuning HF models eats too much time | Start with an off-the-shelf/pretrained anomaly model or even classical stats (z-score, Isolation Forest) for v1; upgrade later |
| Toy system becomes its own multi-week project | Cap it at 3-4 services; resist adding more — the fault catalogue matters more than system size |
| Free LLM rate limits stall development | Cache prompts/responses during dev (store cached responses in MongoDB keyed by prompt hash); keep a local small model (e.g., via Ollama) as an offline fallback for iteration |
| Eval harness feels like "extra work" and gets cut | Build it in week 9 at the latest — it's the single highest-leverage section of this whole document for your resume |
| Render free-tier cold starts hurt the demo | Keep a local Docker Compose demo path as backup; mention the constraint openly if asked |
| MongoDB Atlas free-tier (M0) storage/connection limits | M0 caps at 512MB storage and limited concurrent connections — fine for this project's scale, but purge old raw-log/trace documents periodically or use a TTL index on `raw_logs` and `agent_traces` |

---

## 12. Future Scope — Designed-In Extension Points

The architecture is deliberately service-boundary-based so each of these can be added without rewriting the core. Treat this as a backlog, not a requirement.

### 12.1 Formal A2A protocol layer
Replace the direct FastAPI-to-FastAPI calls between agents with an actual A2A-style handshake: capability discovery (each agent advertises what it can do), async task delegation, and status polling. Since your agent boundaries already exist (Section 3.2), this is a protocol change, not an architecture change.

### 12.2 GraphRAG for historical incident knowledge
As your incident history grows, replace the flat vector similarity search over past incidents with a proper knowledge graph (service → incident → root-cause-category → fix-applied), enabling queries like "what root causes have historically affected this service after a deploy to its dependency."

### 12.3 Model-cascade router
Add a router in front of the Hypothesis-Ranker and Narrator that classifies incident difficulty and only escalates genuinely ambiguous cases to a stronger model (if you ever get access to one), keeping simple/clear-cut incidents on the cheapest possible path. Track cost/accuracy tradeoffs per tier.

### 12.4 Skill/pattern library (self-improving agent)
Log every successfully diagnosed incident's evidence-to-conclusion path as a reusable "pattern" (stored as a MongoDB document with an embedding for retrieval). For new anomalies, retrieve the closest matching pattern first before running the full ranking pipeline — reducing reasoning cost over time and giving you a second strong metric: cost-per-incident trending down as the pattern library grows.

### 12.5 Multi-service / multi-team scaling
Expand the toy system to simulate a larger service mesh with multiple teams' worth of services, testing whether the dependency graph and evidence-gathering approach holds up at scale — useful if you want a v2 story about scalability specifically.

### 12.6 Human-in-the-loop feedback loop
Let a human mark a report's root cause as correct/incorrect after the fact (store the correction as a document in a MongoDB `feedback` collection, linked by `anomaly_id`), feeding back into both the eval harness and the pattern library — closing the loop from your existing HITL experience at work into this project.

---

## 13. Appendix: MongoDB Data Model Reference

A single reference for every collection used across this document, so schema decisions stay consistent as you build.

| Collection | Purpose | Key fields |
|---|---|---|
| `fault_catalogue` | Ground-truth fault definitions for eval | `fault_id`, `description`, `injected_service`, `true_root_cause`, `expected_signal_type` |
| `deploys` | Simulated deploy history per service | `service`, `deployed_at`, `diff_summary`, `commit_hash` |
| `raw_logs` (time-series collection) | Structured logs from toy services | `timestamp`, `service`, `level`, `trace_id`, `message`, `latency_ms` |
| `anomaly_events` | Detector output | see Section 6.1 |
| `evidence_bundles` | Investigator output | see Section 6.2 |
| `hypotheses` | Hypothesis-Ranker output | see Section 6.3 |
| `incident_reports` | Narrator output (+ embeddings for vector search) | see Section 6.4, plus `embedding` field |
| `agent_traces` | Full structured trace of every agent hop, for debugging/observability | `anomaly_id`, `agent_name`, `input`, `output`, `timestamp`, `latency_ms` |
| `feedback` (future) | Human corrections on incident reports | `anomaly_id`, `human_verdict`, `corrected_cause`, `reviewed_at` |

> **Indexing note:** at minimum, index `anomaly_id` across all collections that reference it (it's your join key across the whole pipeline, since MongoDB has no native cross-collection foreign keys), and add a TTL index on `raw_logs`/`agent_traces` if you're worried about the Atlas M0 512MB cap.

---

> **Closing note**
> Build the core (Sections 1-9) first and get it fully working end-to-end before touching anything in Section 12. A finished, well-measured v1 is worth more on a resume than an ambitious, half-finished v2. Come back to this document and update it as you make real decisions — it should track what you actually built, including the parts that didn't work and why.
