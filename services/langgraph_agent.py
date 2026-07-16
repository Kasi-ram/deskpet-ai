import json
import re

from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.checkpoint.memory import (
    InMemorySaver
)

from services.groq_service import GroqService

from tools.knowledge_tool import KnowledgeTool
from tools.calculator_tool import CalculatorTool
from tools.weather_tool import WeatherTool

def is_math_expression(text):

            text = text.strip()

            return bool(
                re.fullmatch(
                    r"[0-9\.\+\-\*\/\(\)\s]+",
                    text
                )
            )

def extract_math_expression(text):

    matches = re.findall(
        r"[-+]?\d+(?:\.\d+)?(?:\s*[\+\-\*\/]\s*[-+]?\d+(?:\.\d+)?)+",
        text
    )

    if matches:
        return matches[0]

    return ""


def is_standalone_math_request(question, expression):

    if not expression:
        return False

    remainder = question.replace(expression, "", 1).strip().lower()

    return bool(
        re.fullmatch(
            r"(?:what(?:\s+is|'s)?|calculate|compute|solve|evaluate|"
            r"the\s+result\s+of|please|is)?[\s?:!.,=]*",
            remainder
        )
    )

class AgentState(TypedDict):

    question: str
    conversation_history: list

    knowledge_base_id: str

    selected_tools: list

    knowledge_query: str

    calculator_expression: str

    weather_location: str

    knowledge_answer: str
    knowledge_found: bool

    calculator_answer: str

    weather_answer: str

    answer: str

    sources: list


class LangGraphAgent:

    def __init__(self):

        self.llm = GroqService()

        self.knowledge_tool = (
            KnowledgeTool()
        )

        self.calculator_tool = (
            CalculatorTool()
        )

        self.weather_tool = (
            WeatherTool()
        )

        graph = StateGraph(
            AgentState
        )

        graph.add_node(
            "planner",
            self.planner_node
        )

        graph.add_node(
            "knowledge",
            self.knowledge_node
        )

        graph.add_node(
            "weather",
            self.weather_node
        )

        graph.add_node(
            "calculator",
            self.calculator_node
        )

        graph.add_node(
            "general",
            self.general_node
        )

        graph.add_node(
            "final_answer",
            self.final_answer_node
        )

        graph.add_edge(
            START,
            "planner"
        )

        graph.add_conditional_edges(
            "planner",
            self.route_after_planner,
            {
                "knowledge": "knowledge",
                "calculator": "calculator",
                "weather": "weather"
            }
        )

        graph.add_conditional_edges(
            "knowledge",
            self.route_after_knowledge,
            {
                "weather": "weather",
                "calculator": "calculator",
                "general": "general",
                "final_answer": "final_answer"
            }
        )

        graph.add_conditional_edges(
            "weather",
            self.route_after_weather,
            {
                "calculator": "calculator",
                "final_answer": "final_answer"
            }
        )

        graph.add_edge(
            "calculator",
            "final_answer"
        )

        graph.add_edge(
            "general",
            "final_answer"
        )

        graph.add_edge(
            "final_answer",
            END
        )

        self.memory = InMemorySaver()

        self.graph = graph.compile(
            checkpointer=self.memory
        )

    def weather_node(
            self,
            state
        ):

            result = self.weather_tool.execute(
                state["weather_location"]
            )

            return {

                "weather_answer": result["answer"]
            }

    def planner_node(
        self,
        state
    ):

        question = state["question"]

        expression = extract_math_expression(question)

        has_math = expression != ""
        pure_math = bool(expression) and (
            expression == question.strip()
            or is_standalone_math_request(
                question,
                expression
            )
        )

        if pure_math:

            return {
                "selected_tools": ["calculator"],
                "knowledge_query": "",
                "calculator_expression": expression,
                "knowledge_answer": "",
                "knowledge_found": False,
                "weather_location":"",
                "calculator_answer": "",
                "answer": "",
                "sources": []
            }
        
        if has_math:

            question_without_math = question.replace(
                expression,
                ""
            ).strip()

            return {
                "selected_tools": [
                    "knowledge",
                    "calculator"
                ],
                "knowledge_query": question_without_math,
                "calculator_expression": expression,
                "knowledge_answer": "",
                "knowledge_found": False,
                "weather_location":"",
                "calculator_answer": "",
                "answer": "",
                "sources": []
            }

        if is_math_expression(question):

            return {
                "selected_tools": [
                    "calculator"
                ],
                "knowledge_query": "",
                "calculator_expression": question,
                "knowledge_answer": "",
                "knowledge_found": False,
                "weather_location":"",
                "calculator_answer": "",
                "answer": "",
                "sources": []
            }

        conversation_history = (
                state.get("conversation_history")
                or []
            )

        history_text = "\n".join(
            [
                (
                    f'{message["role"]}: '
                    f'{message["content"]}'
                )
                for message
                in conversation_history[-6:]
            ]
        )

        prompt = f"""
            You are the Planner for DeskPet AI.

            Your job is ONLY to determine:

            1. Which tools are required.
            2. Rewrite follow-up questions into standalone questions.
            3. Extract structured tool inputs.

            Do NOT answer the user's question.

            ------------------------------------
            AVAILABLE TOOLS
            ------------------------------------

            knowledge
            - Search uploaded documents.
            - Use for:
            - airline policies
            - baggage rules
            - ticket rules
            - travel rules
            - company documents
            - PDFs
            - manuals
            - FAQs
            - SOPs
            - uploaded knowledge

            calculator
            - Perform mathematical calculations.
            - Use ONLY when arithmetic or mathematical computation is requested.

            weather
            - Get live weather information.
            - Use for:
            - weather
            - forecast
            - temperature
            - humidity
            - rainfall
            - wind
            - climate

            ------------------------------------
            RULES
            ------------------------------------

            1.
            Every document-related question MUST use knowledge.

            2.
            Use calculator ONLY for mathematical expressions.

            3.
            Use weather ONLY for weather-related questions.

            4.
            A question may require multiple tools.

            5.
            If a follow-up question depends on previous conversation,
            rewrite it into a complete standalone question.

            Example:

            Previous:
            Can I change travel after commencement?

            Current:
            What about before commencement?

            knowledge_query:
            Can I change travel before commencement?

            6.
            For weather questions return ONLY the city/location name.

            DO NOT return latitude or longitude.

            ------------------------------------
            EXAMPLES
            ------------------------------------

            User:
            How many complimentary bags can infants receive?

            Output:

            {{
                "tools":["knowledge"],
                "knowledge_query":"How many complimentary bags can infants receive?",
                "calculator_expression":"",
                "weather_location":""
            }}

            ------------------------------------

            User:
            25 * 18

            Output:

            {{
                "tools":["calculator"],
                "knowledge_query":"",
                "calculator_expression":"25*18",
                "weather_location":""
            }}

            ------------------------------------

            User:
            What is 10 + 5 and how many complimentary bags can infants receive?

            Output:

            {{
                "tools":["knowledge","calculator"],
                "knowledge_query":"How many complimentary bags can infants receive?",
                "calculator_expression":"10+5",
                "weather_location":""
            }}

            ------------------------------------

            User:
            What's the weather in Berlin?

            Output:

            {{
                "tools":["weather"],
                "knowledge_query":"",
                "calculator_expression":"",
                "weather_location":"Berlin"
            }}

            ------------------------------------

            User:
            What is the weather in Chennai tomorrow and what is 250 * 12?

            Output:

            {{
                "tools":["weather","calculator"],
                "knowledge_query":"",
                "calculator_expression":"250*12",
                "weather_location":"Chennai"
            }}

            ------------------------------------

            CONVERSATION HISTORY

            {history_text}

            ------------------------------------

            CURRENT QUESTION

            {question}

            ------------------------------------

            Return ONLY valid JSON.

            {{
                "tools": [],
                "knowledge_query": "",
                "calculator_expression": "",
                "weather_location": ""
            }}
            """

        response = self.llm.ask_json(
            prompt
        )

        decision = json.loads(
            response
        )

        print("\nPLANNER DECISION")
        print(json.dumps(decision, indent=2))

        selected_tools = [
            tool
            for tool in decision.get("tools", [])
            if tool in {"knowledge", "calculator", "weather"}
        ]

        knowledge_query = decision.get(
            "knowledge_query",
            ""
        ).strip()

        calculator_expression = decision.get(
            "calculator_expression",
            ""
        ).strip()

        weather_location = decision.get(
            "weather_location",
            ""
        ).strip()

        # -----------------------------
        # Force correct routing
        # -----------------------------

        # Validate calculator output

        # -------------------------------------------------
        # Validate calculator tool
        # -------------------------------------------------

        # Empty expression -> remove calculator
        if not calculator_expression:

            if "calculator" in selected_tools:
                selected_tools.remove("calculator")

        # Non-empty but invalid expression -> remove calculator
        elif not is_math_expression(calculator_expression):

            calculator_expression = ""

            if "calculator" in selected_tools:
                selected_tools.remove("calculator")

        # A valid expression must always be calculated, even if the
        # planner omitted calculator from its tools list.
        elif "calculator" not in selected_tools:

            selected_tools.append("calculator")

        # Knowledge should always be used when
        # a knowledge query exists
        if knowledge_query:

            if "knowledge" not in selected_tools:
                selected_tools.append("knowledge")

        # If no tool remains,
        # default to knowledge
        if not selected_tools:

            selected_tools = ["knowledge"]

        # If knowledge query is empty,
        # use original question
        if (
            "knowledge" in selected_tools
            and not knowledge_query
        ):
            knowledge_query = question

        return {
            "selected_tools": selected_tools,
            "knowledge_query": knowledge_query,
            "calculator_expression": calculator_expression,
            "weather_location": weather_location,
            "knowledge_answer": "",
            "knowledge_found": False,
            "calculator_answer": "",
            "answer": "",
            "sources": []
        }

    def route_after_planner(self, state):

        tools = state["selected_tools"]

        if "knowledge" in tools:
            return "knowledge"

        if "weather" in tools:
            return "weather"

        return "calculator"

    def knowledge_node(
        self,
        state
    ):

        result = (
            self.knowledge_tool.execute(
                state["knowledge_query"],
                state.get("knowledge_base_id", "default")
            )
        )

        return {
            "knowledge_answer": result["answer"],
            "knowledge_found": result["found"],
            "sources": result["sources"]
        }

    def route_after_knowledge(
        self,
        state
    ):

        tools = state["selected_tools"]

        if "weather" in tools:
            return "weather"

        if "calculator" in tools:
            return "calculator"

        if not state.get("knowledge_found", False):
            return "general"

        return "final_answer"

    def route_after_weather(
        self,
        state
    ):

        tools = state["selected_tools"]

        if "calculator" in tools:
            return "calculator"

        return "final_answer"

    def calculator_node(
        self,
        state
    ):

        result = (
            self.calculator_tool.execute(
                state[
                    "calculator_expression"
                ]
            )
        )

        return {
            "calculator_answer": result["answer"]
        }

    def general_node(
        self,
        state
    ):

        question = state["question"]

        prompt = f"""
You are DeskPet AI.

The uploaded knowledge base was searched first
and did not contain an answer.

Answer only if this is a general knowledge,
casual, or utility question.

If the question appears to ask about an airline
policy, internal rule, uploaded document, baggage,
booking, ticket, travel rule, or company-specific
information, respond exactly:

"I could not find this information in the available knowledge base."

USER QUESTION:

{question}
"""

        answer = self.llm.ask(
            prompt
        )

        return {
            "answer": answer
        }

    def final_answer_node(
        self,
        state
    ):

        selected_tools = state[
            "selected_tools"
        ]

        knowledge_answer = state.get(
            "knowledge_answer",
            ""
        )

        calculator_answer = state.get(
            "calculator_answer",
            ""
        )

        current_answer = state.get(
            "answer",
            ""
        )

        if len(selected_tools) > 1:

            answer_parts = []

            if "knowledge" in selected_tools:

                if state.get("knowledge_found"):
                    answer_parts.append(knowledge_answer)
                else:
                    answer_parts.append(
                        "I could not find the requested information "
                        "in the available knowledge base."
                    )

            if "weather" in selected_tools:

                weather_answer = state.get("weather_answer", "")
                if weather_answer:
                    answer_parts.append(weather_answer)

            if "calculator" in selected_tools:

                if calculator_answer:
                    answer_parts.append(
                        f"The calculation result is {calculator_answer}."
                    )

            answer = "\n\n".join(answer_parts)

        elif "knowledge" in selected_tools:

            if not state.get("knowledge_found", False) and current_answer:
                answer = current_answer
            else:
                answer = knowledge_answer

        elif "weather" in selected_tools:

            answer = state.get("weather_answer", "")

        elif "calculator" in selected_tools:

            answer = calculator_answer

        else:

            answer = current_answer

        history = (
            state.get("conversation_history")
            or []
        )

        history = history + [
            {
                "role": "user",
                "content": state["question"]
            },
            {
                "role": "assistant",
                "content": answer
            }
        ]

        return {
            "answer": answer,
            "conversation_history": history
        }

    def ask(
        self,
        question,
        thread_id="default",
        knowledge_base_id="default"
    ):

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        result = self.graph.invoke(
            {
                "question": question,
                "knowledge_base_id": knowledge_base_id
            },
            config=config
        )

        return {
            "answer": result["answer"],
            "sources": result["sources"]
        }
    
    def stream(
        self,
        question,
        thread_id="default",
        knowledge_base_id="default"
    ):

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        initial_state = {
            "question": question,
            "knowledge_base_id": knowledge_base_id
        }

        result = initial_state.copy()
        received_update = False

        for update in self.graph.stream(
            initial_state,
            config=config,
            stream_mode="updates"
        ):

            node = next(iter(update.keys()))

            state = update[node]

            result.update(state)
            received_update = True

            yield {
                "type": "node",
                "node": node,
                "state": state
            }

        if not received_update:

            result = self.graph.invoke(
                initial_state,
                config=config
            )

        yield {
            "type": "result",
            "answer": result.get("answer", ""),
            "sources": result.get("sources", [])
        }
        
