from agents.base_agent import BaseAgent

class AggregatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("AggregatorAgent")

    def run(self, shared_state: dict) -> dict:
        """
        Aggregates results from all agents.
        In this monolithic design, the shared_state already holds the keys.
        This agent is a placeholder for any complex merging logic if needed.
        For now, it simply passes the state through, ensuring all keys exist.
        """
        # Ensure keys exist for the report agent
        shared_state.setdefault("chart_agent", {"charts": []})
        shared_state.setdefault("insight_agent", {"insights": "No insights."})
        shared_state.setdefault("forecast_agent", {"forecast_text": "No forecast."})
        
        print("[AggregatorAgent] Aggregated results.")
        return shared_state