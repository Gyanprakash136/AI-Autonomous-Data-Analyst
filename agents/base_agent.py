from google.genai import types
import uuid
import asyncio
import threading

class BaseAgent:
    _lock = threading.Lock()

    def __init__(self, name: str):
        self.name = name

    def build_llm_input(self, shared_state: dict, extra_context: str = "") -> str:
        user_query = shared_state.get("user_query", "")
        return f"""
        USER QUESTION:
        {user_query}

        CONTEXT:
        {extra_context}
        """

    def run_llm(self, agent_template, llm_input: str) -> str:
        """
        Executes LLM call using the correct ADK 2025 Runner API.
        Creates a FRESH stack (Model, Agent, Runner) for each call to ensure thread safety.
        """
        from google.adk.runners import InMemoryRunner
        from google.adk.agents import Agent
        from google.adk.models.google_llm import Gemini
        import os
        
        # 1. Generate Session ID
        current_session_id = str(uuid.uuid4())
        
        # 2. Reconstruct Agent & Model to ensure fresh genai.Client
        # We assume agent_template has the config we need
        original_model = agent_template.model
        
        # Get API Key (from env or model if accessible)
        api_key = os.environ.get("GOOGLE_API_KEY")
        
        # Create fresh Model
        new_model = Gemini(
            model="gemini-2.0-flash-lite-preview-02-05", # Hardcoded or extracted
            retry_options=getattr(original_model, "retry_options", None),
            api_key=api_key
        )
        
        # Create fresh Agent
        new_agent = Agent(
            name=agent_template.name,
            model=new_model,
            instruction=agent_template.instruction,
            tools=agent_template.tools
        )
        
        # 3. Create FRESH Runner
        runner = InMemoryRunner(app_name="agents", agent=new_agent)
        
        # 4. Create Session
        try:
            if hasattr(runner, "session_service"):
                asyncio.run(runner.session_service.create_session(
                    session_id=current_session_id, 
                    user_id="user",
                    app_name="agents"
                ))
            
            # Correct ADK 2025 API: types.Content with parts
            new_message = types.Content(parts=[types.Part(text=llm_input)])
            
            # 5. Run Runner
            # runner.run returns a generator yielding events
            events = runner.run(
                user_id="user",
                session_id=current_session_id,
                new_message=new_message
            )
            
            # 5. Extract Text
            collected = []
            for event in events:
                # Handle streaming text chunks
                if hasattr(event, "text") and isinstance(event.text, str):
                    collected.append(event.text)
                # Handle content parts
                if hasattr(event, "content") and event.content:
                    parts = getattr(event.content, "parts", None)
                    if parts:
                        for p in parts:
                            if hasattr(p, "text"):
                                collected.append(p.text)
            
            full_text = "".join(collected).strip()
            return full_text

        except Exception as e:
            print(f"[{self.name}] Runner Execution Failed: {e}")
            # Proceed to fallback below
            pass

        # ---------------------------------------------------------
        # FALLBACK: Direct Model Access
        # ---------------------------------------------------------
        try:
            print(f"[{self.name}] Using Direct Model Fallback...")
            
            # runner.agent.model is likely the ADK Gemini wrapper.
            # It might have a .model property for the underlying google.genai model
            # or we might need to instantiate a client.
            
            model = runner.agent.model
            
            # Check if it has generate_content directly (it failed before)
            if hasattr(model, "generate_content"):
                response = model.generate_content(contents=llm_input)
            elif hasattr(model, "_model") and hasattr(model._model, "generate_content"):
                 # Access protected member if wrapper hides it
                response = model._model.generate_content(contents=llm_input)
            else:
                # Last resort: try to find the client or model
                print(f"[{self.name}] Debug: model dir: {dir(model)}")
                return ""

            if hasattr(response, "text"):
                return response.text.strip()
            return str(response)

        except Exception as e2:
            print(f"[{self.name}] Critical Failure: {e2}")
            return ""

    def run(self, shared_state: dict):
        raise NotImplementedError