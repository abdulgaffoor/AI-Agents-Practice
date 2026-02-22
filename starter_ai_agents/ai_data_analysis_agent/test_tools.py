import json
from agno.agent import Agent
from agno.tools.duckdb import DuckDbTools
from agno.models.google import Gemini

model = Gemini(id="gemini-2.0-flash-001", vertexai=True, project_id="con-alma-478303", location="us-central1")
agent = Agent(model=model, tools=[DuckDbTools()])
print("Tools enabled:", len(agent.tools))
for tool in agent.tools:
    print(tool)
from agno.utils.gemini import format_function_definitions
gemini_tools = format_function_definitions(agent.get_tool_dicts())
print("Gemini formatted tools:")
print(gemini_tools)
