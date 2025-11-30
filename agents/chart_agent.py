import json
import re
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

from agents.base_agent import BaseAgent
from tools.chart_tool import generate_chart_tool

import os

class ChartAgent(BaseAgent):
    def __init__(self):
        super().__init__("ChartAgent")

        self.retry_config = types.HttpRetryOptions(
            attempts=3,
            exp_base=2,
            initial_delay=1
        )
        
        api_key = os.environ.get("GOOGLE_API_KEY")

        self.chart_llm_agent = Agent(
            name="Chart_LLM",
            model=Gemini(
                model="gemini-2.0-flash-lite-preview-02-05",
                retry_options=self.retry_config,
                api_key=api_key
            ),
            instruction="""
            You are a Visualization Expert.
            Analyze data sample and return a JSON LIST of chart specs.
            Format: [{"type": "bar|line|scatter|pie", "x_col": "col1", "y_col": "col2", "title": "..."}]
            Return ONLY strict JSON.
            Do not include any text outside the JSON.
            """,
            tools=[]
        )

        self.runner = InMemoryRunner(
            app_name="agents",
            agent=self.chart_llm_agent
        )

    def _extract_json(self, text):
        """
        Robust JSON extraction.
        """
        try:
            # Remove markdown code blocks
            text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'```', '', text)
            text = text.strip()
            
            # Try to find the JSON list
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            
            # Fallback: try parsing the whole text
            return json.loads(text)
        except Exception as e:
            print(f"[ChartAgent] JSON Extraction Failed: {e}")
            return []

    def run(self, shared_state):
        rows = shared_state.get("sql_result", {}).get("rows", [])
        columns = shared_state.get("sql_result", {}).get("columns", [])

        if not rows:
            print("[ChartAgent] No data to visualize.")
            return {"chart_agent": {"charts": []}}

        # Limit rows for context window
        sample_rows = rows[:5]
        
        # Check discovery mode
        is_discovery = shared_state.get("discovery_mode", False)
        
        if is_discovery:
            llm_input = f"""
            Columns: {columns}
            Data Sample: {sample_rows}
            Task: Generate 2-3 general overview charts (e.g., distribution of key numerical columns, or counts of categorical columns).
            """
        else:
            llm_input = self.build_llm_input(
                shared_state,
                extra_context=f"""
                Columns: {columns}
                Data Sample: {sample_rows}
                """
            )

        response = self.run_llm(self.chart_llm_agent, llm_input)
        specs = self._extract_json(response)
        
        charts = []
        for spec in specs:
            try:
                # Validate spec keys
                if not all(k in spec for k in ("type", "x_col", "y_col", "title")):
                    print(f"[ChartAgent] Invalid spec: {spec}")
                    continue

                png = generate_chart_tool(
                    rows, columns, 
                    spec.get('type'), spec.get('x_col'), spec.get('y_col'), 
                    spec.get('title')
                )
                if png:
                    charts.append({"spec": spec, "png": png})
            except Exception as e:
                print(f"[ChartAgent] Chart gen failed: {e}")

        # Return ONLY the agent's specific output key
        return {"chart_agent": {"charts": charts}}