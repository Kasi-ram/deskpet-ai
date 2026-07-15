import json
import re

from services.groq_service import GroqService
from tools.knowledge_tool import KnowledgeTool
from tools.calculator_tool import CalculatorTool


class AgentService:

    def __init__(self):
        self.llm = GroqService()

        self.tools = {
            "knowledge_search": KnowledgeTool(),
            "calculator": CalculatorTool()
        }

        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "knowledge_search",
                    "description": (
                        "Search airline policies and internal "
                        "knowledge base documents."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string"
                            }
                        },
                        "required": ["question"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": (
                        "Perform mathematical calculations."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]

    def ask(self, question):

        response = self.llm.client.chat.completions.create(
            model=self.llm.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are DeskPet AI. "
                        "Use the available tools to answer "
                        "the user's request."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            tools=self.tool_definitions,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if not message.tool_calls:
            return {
                "answer": message.content,
                "sources": []
            }

        tool_call = message.tool_calls[0]

        tool_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        if tool_name == "knowledge_search":

            return self.tools[
                "knowledge_search"
            ].execute(
                arguments["question"]
            )

        if tool_name == "calculator":

            return self.tools[
                "calculator"
            ].execute(
                arguments["expression"]
            )

        return {
            "answer": "No suitable tool is available.",
            "sources": []
        }