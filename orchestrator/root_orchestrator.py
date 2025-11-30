import concurrent.futures
import copy
import sys
import os

# Ensure root import visibility
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.sql_agent import SQLAgent
from agents.chart_agent import ChartAgent
from agents.insight_agent import InsightAgent
from agents.forecast_agent import ForecastAgent
from agents.aggregator_agent import AggregatorAgent
from agents.report_agent import ReportAgent
from tools.sql_tool import run_sql_tool

class RootOrchestrator:
    def __init__(self):
        self.sql_agent = SQLAgent()
        self.chart_agent = ChartAgent()
        self.insight_agent = InsightAgent()
        self.forecast_agent = ForecastAgent()
        self.aggregator_agent = AggregatorAgent()
        self.report_agent = ReportAgent()

    def _run_parallel_agents(self, shared_state):
        """
        Runs Chart, Insight, and Forecast agents in parallel.
        Uses deepcopy to prevent state pollution.
        Merges results safely.
        """
        agents = [self.chart_agent, self.insight_agent, self.forecast_agent]
        updated_state = {}

        # Safely run thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Deepcopy to prevent shared state race conditions during reads
            # We map future -> agent_name for error reporting
            futures = {
                executor.submit(agent.run, copy.deepcopy(shared_state)): agent.name
                for agent in agents
            }

            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    res = future.result()
                    # Merge specific agent outputs back
                    # We expect agents to return a dict with their specific key
                    # e.g. {"chart_agent": ...}
                    for k, v in res.items():
                        if k.endswith("_agent"):
                            updated_state[k] = v
                except Exception as e:
                    print(f"Agent {name} failed: {e}")

        return updated_state

    def run_discovery(self, shared_state: dict):
        """
        Runs agents in discovery mode to generate initial insights and charts.
        """
        print("--- Discovery Mode Start ---")
        shared_state["discovery_mode"] = True
        
        # Run Chart and Insight agents in parallel
        # Note: We skip SQLAgent and ForecastAgent for discovery as we just want overview
        agents = [self.chart_agent, self.insight_agent]
        updated_state = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(agent.run, copy.deepcopy(shared_state)): agent.name
                for agent in agents
            }

            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    res = future.result()
                    for k, v in res.items():
                        if k.endswith("_agent"):
                            updated_state[k] = v
                except Exception as e:
                    print(f"Discovery Agent {name} failed: {e}")

        shared_state.update(updated_state)
        print("--- Discovery Mode End ---")
        return shared_state

    def run(self, user_query: str, history: list = []):
        print("--- Pipeline Start ---")
        shared_state = {"user_query": user_query, "discovery_mode": False, "history": history}

        # 1. SQL
        print("Running SQLAgent...")
        shared_state = self.sql_agent.run(shared_state)
        
        print("Running SQL Tool...")
        shared_state = run_sql_tool(shared_state)
        
        if shared_state.get("sql_result", {}).get("error"):
            print("SQL Execution failed. Stopping pipeline.")
            return shared_state

        # 2. Parallel Analysis
        print("Running Parallel Agents...")
        p_results = self._run_parallel_agents(shared_state)
        shared_state.update(p_results)

        # 3. Aggregate
        print("Running AggregatorAgent...")
        shared_state = self.aggregator_agent.run(shared_state)

        # 4. Report
        print("Running ReportAgent...")
        shared_state = self.report_agent.run(shared_state)

        print("--- Pipeline End ---")
        return shared_state