import json
import re

from services.openai_service import OpenAIService
from tools.knowledge_tool import KnowledgeTool
from tools.calculator_tool import CalculatorTool

class AgentService:

    def __init__(self):
        self.llm = OpenAIService()

        self.tools = {
            "knowledge": KnowledgeTool(),
            "calculator": CalculatorTool()
        }

    def select_tool(self, question):

        prompt = f"""
You are a tool selection agent.

Available tools:

knowledge:
Search airline policies and internal documents.

calculator:
Perform mathematical calculations.

Select the best tool for the user question.

Return ONLY JSON.

Example:
{{"tool": "knowledge"}}

USER QUESTION:
{question}
"""

        response = self.llm.ask(prompt)

        return json.loads(response)

    def ask(self, question):

        if re.fullmatch(
            r"\s*(what is\s+)?[\d\s+\-*/().]+\??\s*",
            question.lower()
        ):
            return self.calculator.execute(question)

        decision = self.select_tool(question)

        tool_name = decision["tool"]

        tool = self.tools.get(tool_name)

        if not tool:
            return {
                "answer": "No suitable tool is available.",
                "sources": []
            }

        return tool.execute(question)