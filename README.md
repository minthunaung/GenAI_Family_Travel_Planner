•Architecture overview 
    •	Conversational & Multi-Agent handling: 
		•	Modular, agent-based system orchestrated by LangGraph with conditions and LLM router for agent task distributions
		•	Central state model (HybridState) holds conversation context, history, memory logs, and intermediate data
		•	Agents implemented as RunnableLambda functions perform discrete tasks
    •	RAG-based Document QA agent: 
		•	RAG storage, retrieval with FAISS + OpenAIEmbeddings and recommendation with LLM
		•	Text-to-Image Generation Agent
		•	Photo idea generation based on user profile, activity, location, weather and image creation with OPENAI
    •	SQLite Agent:
    •		Save user profile to from user prompt with llm
    •	Weather Agent: 
    •		Location extraction with LLM and weather checking
    •	Summary Agent: 
		• Summarization, memory logging and exception handling
    •	Chat Interface:
		•	Gradio for Chat interface
    •	LLM:
		•	OPEN APIs for natural-language and visual outputs

•Key implementation and decisions
    •	Router dispatches to one of six entry nodes based on state.next.
    •	seed_data & create_rag shortcut directly to Summarize.
    •	fetch_family kicks off the RAG?recommendation?location?weather?photo subflow.
    •	weather_check branches: “weather” queries go straight to summary, others go to photo_memory.
    •	photo_memory then either invokes photo_generate (if a “photo” request) or ends in Summarize.
    •	Summarize is the single finish point across all paths.
    Router
    +- seed_data #Userprompt: I’m 42—into museums and food. My wife is 40, she likes the beach and shopping. Our son is 12, loves video games and drawing. My daughter is 10, like to play at beach and love animals.
    ¦   +- Summarize (end)
    ¦
    +- create_rag #Userprompt: Please ingest the TripAdvisor URL https://www.klook.com/en-SG/blog/cheapest-holidays-from-singapore/
    ¦   +- Summarize (end) 
    ¦
    +- fetch_family #Userprompt: Plan a family trip
    ¦   +- rag_retrieve
    ¦       +- rag_recommend
    ¦           +- extract_location
    ¦               +- weather_check
    ¦                   +- if “weather” in input ? Summarize (end)
    ¦                   +- else ? photo_memory
    ¦                        +- if “photo” in input ? photo_generate
    ¦                        ¦    +- Summarize (end)
    ¦                        +- else ? Summarize (end)
    ¦
    +- extract_location #Userprompt: How is the weather there?
    ¦   +- weather_check  ? (same as above under fetch_family)
    ¦
    +- photo_memory # Userprompt: Where can I take good photo there?
    ¦   +- photo_generate
    ¦        +- Summarize (end)
    ¦
    +- summarize (end)

•How to start?

1.	Make sure all API keys are available as per utils/config.py.               
2.	Run all cells with notebooks/FamilyTravelPlannerv3.ipynb.

    family_travel_planner/	 	# project_root
    +-- notebooks/  
    ¦   +-- FamilyTravelPlanner.ipynb #V1: Test all codes in one notebook
    ¦   +-- FamilyTravelPlannerv2.ipynb #V2: Group code as per function in specific folders, handle 3 prompts (Plan,Photo,Weather)
    ¦   +-- FamilyTravelPlannerv3.ipynb #V3: Final version with Gradio to handle User prompts: Register Users, Rag upload, Plan,Photo,Weather etc.
    +-- controller/  
    ¦   +-- shared_types.py       # HybridState Pydantic model  
    ¦   +-- controller.py         # Gradio integration and main loop  
    +-- agents/  
    ¦   +-- llm_router_agent.py    # Agent task distributions
    ¦   +-- seed_data_agent.py     # User profile update to SQL with LLM
    ¦   +-- fetch_family_agent.py  # User profile retrieval from SQL 
    ¦   +-- sql_agents.py  	# Query SQL 
    ¦   +-- create_rag_agents.py   # create rag DB from URL or PDF with LLM  
    ¦   +-- rag_agents.py          # retrieval from RAG  
    ¦   +-- recommender_agents.py  # Trip recommendation  
    ¦   +-- extract_location_agent.py      # extract location with LLM  
    ¦   +-- weather_agent.py       # get weather + check weather   
    ¦   +-- photo_memory_agent.py  # Users SQL + location + weather 
    ¦   +-- photo_generation_agent.py  #Generate photo
    ¦   +-- summarize_agent.py     #handle Trip,Photo,Weather & fallback
    +-- utils/  
    ¦   +-- config.py             # API keys, DB/RAG paths  
    ¦   +-- rag_utils.py          # ingest_documents  
    ¦   +-- utils.py              # load User from SQL  
    +-- travelguide/  
    ¦   +-- Americas_compressed.pdf    # travel brochure
    +-- scripts/  
    ¦   +-- create_rag.py             # standalone RAG ingestion script  
    ¦   +-- create_database.py        # standalone create db script  
    ¦   +-- seed_data.py              # standalone SQL update script  
    +-- image_gen/  
    ¦   +-- image_generator.py    # display as small 512x512 image in notebook  
    +-- family_travel_planner.db  # SQLite family_members table  
    +-- family_travel_rag.index   # RAG FAISS DB  
    +-- session_state.json        # persisted HybridState

•Debugging and testing process
    •	Added debug flag with print() statements around each LLM call and database operation. 
    •	Verified agent return types using standalone unit tests before wiring into LangGraph
    •	Asserted all agent-builder functions return callables to catch NoneType errors
    •	Inspected raw OpenAI responses and JSON parsing steps to resolve silent failures
    •	Migrated Pydantic’s dict() ? model_dump() to suppress deprecation warnings
    
•Challenges faced and how they were resolved
    •	Missing HybridState imports in agent modules due to recursive call from controller
		•	Fixed by placing HybridState in shared_types and call by agents, controller
    •	Agents not returning state after LLM hang
		•	Instrumented try/except with verbose logging and ensured final return state
    •	Graph builder returning None
		•	Added sanity assertions to confirm each builder returns a compiled graph
    •	Pydantic schema mismatches on load_state
		•	Added default field fallbacks and validation error handling for robust state loading
    •	Gradio history format mismatch
		•	Refactored chat_interface to return only assistant messages; let Gradio manage history

•Future Improvements
    •	Different debug mode: To log different level of logging to understand the problem better. E.g. Variable/State before/after call.
    •	API calls: Save cost with  repeated API call in requests_cache. e.g. weather lookups for the same location.
    •	Contextual memory compression: periodically summarize history for cost-efficient prompts
    •	Multi-destination loop: plan, check weather, and summarize per location in a subgraph
    •	User profile management: persist user preferences and session metadata across days
    •	GUI enhancements: image previews, clickable itinerary links, exportable PDF reports
    •	Error-handling UI: interactive prompts to correct malformed LLM outputs before seeding or ingestion
