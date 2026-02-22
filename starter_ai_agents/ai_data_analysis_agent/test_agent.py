import sys
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckdb import DuckDbTools
from agno.tools.pandas import PandasTools
import logging
logging.basicConfig(level=logging.DEBUG)

# Initialize DuckDbTools
duckdb_tools = DuckDbTools()

try:
    data_analyst_agent = Agent(
        model=Gemini(
            id="gemini-2.0-flash-001",
            vertexai=True,
            project_id="ai-agents-practice-488122",
            location="us-central1"
        ),
        tools=[duckdb_tools, PandasTools()],
        system_message="Test",
        markdown=True,
    )

    response = data_analyst_agent.run("What is 2+2?")
    print("SUCCESS:", response.content)
except Exception as e:
    print("ERROR CAUGHT", e)
