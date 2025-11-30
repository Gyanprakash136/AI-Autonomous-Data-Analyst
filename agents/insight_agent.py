from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

from agents.base_agent import BaseAgent

import os

class InsightAgent(BaseAgent):
    def __init__(self):
        super().__init__("InsightAgent")

        self.retry_config = types.HttpRetryOptions(
            attempts=3,
            exp_base=2,
            initial_delay=1
        )
        
        api_key = os.environ.get("GOOGLE_API_KEY")

        self.insight_llm_agent = Agent(
            name="Insight_LLM",
            model=Gemini(
                model="gemini-2.0-flash-lite-preview-02-05",
                retry_options=self.retry_config,
                api_key=api_key
            ),
            instruction="""
            You are a Senior Data Analyst.
            Analyze the provided data and User Query to provide 3-5 key insights.
            Be concise and professional.
            """,
            tools=[]
        )

        self.runner = InMemoryRunner(
            app_name="agents",
            agent=self.insight_llm_agent
        )

    def run(self, shared_state):
        rows = shared_state.get("sql_result", {}).get("rows", [])
        columns = shared_state.get("sql_result", {}).get("columns", [])

        if not rows:
            return {"insight_agent": {"insights": "No data available for insights."}}

        # Limit rows for context
        sample_rows = rows[:20] 
        
        # Check if we are in discovery mode (no user query)
        is_discovery = shared_state.get("discovery_mode", False)
        
        if is_discovery:
            prompt = f"""
            Columns: {columns}
            Data Sample (first 20 rows): {sample_rows}
            
            Task: Generate 3-5 interesting questions that a user might want to ask about this data.
            Return ONLY a JSON list of strings. Example: ["Question 1?", "Question 2?"]
            """
            response = self.run_llm(self.insight_llm_agent, prompt)
            
            # Extract JSON list
            import json
            import re
            try:
                text = re.sub(r'```json\s*', '', response, flags=re.IGNORECASE)
                text = re.sub(r'```', '', text).strip()
                questions = json.loads(text)
                if not isinstance(questions, list):
                    questions = []
            except:
                questions = []
                
            return {"insight_agent": {"recommended_questions": questions}}
        
        else:
            # Normal insight generation
            llm_input = self.build_llm_input(
                shared_state,
                extra_context=f"""
                Columns: {columns}
                Data Sample (first 20 rows): {sample_rows}
                Total Rows: {len(rows)}
                """
            )

            response = self.run_llm(self.insight_llm_agent, llm_input)
            
            return {"insight_agent": {"insights": response}}