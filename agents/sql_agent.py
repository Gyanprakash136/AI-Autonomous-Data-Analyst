from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
import re

from agents.base_agent import BaseAgent

import os

class SQLAgent(BaseAgent):
    def __init__(self):
        super().__init__("SQLAgent")
        
        self.retry_config = types.HttpRetryOptions(
            attempts=3,
            exp_base=2,
            initial_delay=1
        )
        
        api_key = os.environ.get("GOOGLE_API_KEY")

        self.sql_llm_agent = Agent(
            name="SQL_LLM",
            model=Gemini(
                model="gemini-2.0-flash-lite-preview-02-05",
                retry_options=self.retry_config,
                api_key=api_key
            ),
            instruction="""
            You are an Expert SQL Analyst.
            Your task is to convert the User's Question into a valid SQLite query.
            The table name is 'data_table'.
            
            Rules:
            1. Return ONLY the SQL query.
            2. Do NOT include markdown formatting (like ```sql).
            3. Do NOT include explanations.
            4. Use 'data_table' as the table name.
            5. Ensure the SQL is valid SQLite syntax.
            """,
            tools=[]
        )

        # Correct ADK 2025: app_name="agents"
        self.runner = InMemoryRunner(
            app_name="agents",
            agent=self.sql_llm_agent
        )

    def _clean_sql(self, text: str) -> str:
        """
        Removes markdown code blocks and extra whitespace.
        Also attempts to remove common non-SQL prefixes.
        """
        # Remove ```sql ... ``` or ```sqlite ... ``` or just ``` ... ```
        text = re.sub(r'```[a-zA-Z]*\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```', '', text)
        text = text.strip()
        
        # Remove common prefixes if they exist (e.g. "sql", "sqlite")
        # but be careful not to remove valid SQL starts like "SELECT"
        if text.lower().startswith("sqlite"):
            text = text[6:].strip()
        elif text.lower().startswith("sql"):
            text = text[3:].strip()
            
        return text

    def _get_table_schema(self):
        try:
            import sqlite3
            import os
            DB_PATH = os.path.join(os.path.dirname(__file__), '../db/analyst.db')
            if not os.path.exists(DB_PATH):
                return "Table 'data_table' columns: Unknown (DB not found)"
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(data_table)")
            columns = [info[1] for info in cursor.fetchall()]
            conn.close()
            if columns:
                return f"Table 'data_table' columns: {', '.join(columns)}"
            return "Table 'data_table' columns: Unknown (Table not found)"
        except Exception as e:
            print(f"[SQLAgent] Schema fetch failed: {e}")
            return "Table 'data_table' columns: Unknown"

    def run(self, shared_state: dict) -> dict:
        """
        Generates SQL based on user_query and updates shared_state.
        """
        schema_info = self._get_table_schema()
        
        llm_input = self.build_llm_input(
            shared_state, 
            extra_context=f"{schema_info}\nRules: Use 'data_table' as table name."
        )

        response = self.run_llm(self.sql_llm_agent, llm_input)
        sql_query = self._clean_sql(response)
        
        print(f"[SQLAgent] Generated SQL: {sql_query}")
        
        shared_state["sql_agent"] = {"sql": sql_query}
        return shared_state