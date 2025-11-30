from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

from agents.base_agent import BaseAgent

import os

class ForecastAgent(BaseAgent):
    def __init__(self):
        super().__init__("ForecastAgent")

        self.retry_config = types.HttpRetryOptions(
            attempts=3,
            exp_base=2,
            initial_delay=1
        )
        
        api_key = os.environ.get("GOOGLE_API_KEY")

        self.forecast_llm_agent = Agent(
            name="Forecast_LLM",
            model=Gemini(
                model="gemini-2.0-flash-lite-preview-02-05",
                retry_options=self.retry_config,
                api_key=api_key
            ),
            instruction="""
            You are a Predictive Analyst.
            Based on the provided data, provide a brief forecast or trend analysis.
            If the data is not time-series or suitable for forecasting, explain why.
            """,
            tools=[]
        )

        self.runner = InMemoryRunner(
            app_name="agents",
            agent=self.forecast_llm_agent
        )

    def run(self, shared_state):
        rows = shared_state.get("sql_result", {}).get("rows", [])
        columns = shared_state.get("sql_result", {}).get("columns", [])

        if not rows:
            return {"forecast_agent": {"forecast_text": "No data available for forecasting."}}

        # Limit rows for context
        sample_rows = rows[:20]
        
        llm_input = self.build_llm_input(
            shared_state,
            extra_context=f"""
            Columns: {columns}
            Data Sample (first 20 rows): {sample_rows}
            """
        )

        response = self.run_llm(self.forecast_llm_agent, llm_input)
        
        return {"forecast_agent": {"forecast_text": response}}