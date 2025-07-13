# 🧭 Family Travel Planner – System Overview

## 🏗 Architecture Overview

### Conversational & Multi-Agent Handling
- Modular agent-based system orchestrated by LangGraph
- Conditional routing with LLM-driven task distribution
- Central state model (`HybridState`) holds:
  - Conversation context
  - History and memory logs
  - Intermediate agent data
- Agents as `RunnableLambda` functions for discrete tasks

### RAG-based Document QA Agent
- RAG retrieval with FAISS + OpenAIEmbeddings
- Recommendation generation using LLM
- Image generation via OPENAI based on:
  - User profile
  - Activity, location, and weather

### Other Agents
- **SQLite Agent**: Saves user profile from LLM-parsed prompts
- **Weather Agent**: Extracts location and checks weather
- **Summary Agent**: Summarizes and handles exceptions

### UI & API
- Gradio-based chat interface
- Uses OPEN APIs for NLP and image output

---

## 🔄 Workflow Routing Logic

```text
Router
├─ seed_data → Summarize
│   └─ # I’m 42—into museums and food...
│
├─ create_rag → Summarize
│   └─ # Ingest TripAdvisor URL...
│
├─ fetch_family
│   └─ rag_retrieve
│       └─ rag_recommend
│           └─ extract_location
│               └─ weather_check
│                   ├─ “weather” → Summarize
│                   └─ else → photo_memory
│                       ├─ “photo” → photo_generate → Summarize
│                       └─ else → Summarize
│
├─ extract_location → weather_check (same as above)
├─ photo_memory → photo_generate → Summarize
└─ summarize → end

🚀 Getting Started
Ensure all API keys are configured in utils/config.py
Run cells in notebooks/FamilyTravelPlannerv3.ipynb

📁 Project Structure
family_travel_planner/
├─ notebooks/
│   ├─ FamilyTravelPlanner.ipynb         # V1 - all-in-one test notebook
│   ├─ FamilyTravelPlannerv2.ipynb       # V2 - functionally grouped
│   └─ FamilyTravelPlannerv3.ipynb       # V3 - Gradio interface
│
├─ controller/
│   ├─ shared_types.py                   # HybridState Pydantic model
│   └─ controller.py                     # Main loop integration
│
├─ agents/
│   ├─ llm_router_agent.py               # Task distribution
│   ├─ seed_data_agent.py                # SQL insert
│   ├─ fetch_family_agent.py             # SQL fetch
│   ├─ sql_agents.py                     # Raw SQL operations
│   ├─ create_rag_agents.py              # RAG DB creation
│   ├─ rag_agents.py                     # RAG retrieval
│   ├─ recommender_agents.py             # Trip recommendations
│   ├─ extract_location_agent.py         # Location parsing
│   ├─ weather_agent.py                  # Weather retrieval
│   ├─ photo_memory_agent.py             # Contextual photo setup
│   ├─ photo_generation_agent.py         # Image generation
│   └─ summarize_agent.py                # Final summaries
│
├─ utils/
│   ├─ config.py                         # API keys and paths
│   ├─ rag_utils.py                      # RAG ingestion
│   └─ utils.py                          # User loading
│
├─ travelguide/
│   └─ Americas_compressed.pdf          # Sample brochure
│
├─ scripts/
│   ├─ create_rag.py                     # RAG ingestion
│   ├─ create_database.py                # SQL setup
│   └─ seed_data.py                      # Initial user seeding
│
├─ image_gen/
│   └─ image_generator.py               # Local display tool
│
├─ family_travel_planner.db             # SQLite DB
├─ family_travel_rag.index              # FAISS index
└─ session_state.json                   # Persistent session state

🧪 Debug & Testing
Debug flag added to LLM calls and DB ops via print()

Agent functions verified via standalone tests

Sanity checks for callable returns

OpenAI responses inspected manually

Migrated model.dict() to model_dump() to avoid deprecation

🧱 Challenges & Resolutions
Missing HybridState imports: Moved to shared_types.py

Agent response hang: Added try/except, ensured state return

Graph builder returning None: Sanity assertions applied

Pydantic schema mismatch: Default fallbacks + validations

Gradio history issues: Refactored to only return assistant messages

🛠️ Future Improvements
Multi-level debug logs with variable snapshots

API caching for weather lookups via requests_cache

Memory compression for historical context summarization

Multi-destination planning via graph loop

Long-term user preference persistence

GUI upgrades: preview cards, itinerary links, export options

Interactive error UI for malformed LLM outputs
