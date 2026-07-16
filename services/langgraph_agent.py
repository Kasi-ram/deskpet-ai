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
    knowledge_base_id: str
    conversation_history: list

    selected_tools: list

    knowledge_query: str
    calculator_expression: str

    knowledge_answer: str
    knowledge_found: bool

    calculator_answer: str

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
                "calculator": "calculator"
            }
        )

        graph.add_conditional_edges(
            "knowledge",
            self.route_after_knowledge,
            {
                "calculator": "calculator",
                "general": "general",
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
You are the planner for DeskPet AI.

DeskPet is primarily a document knowledge assistant.

Available tools:

knowledge
Search uploaded documents.

calculator
Perform mathematical calculations.

Rules:

1. Use calculator when mathematical calculation
   is requested.

2. For every non-mathematical factual question,
   use knowledge first.

3. A question may use both tools.

4. Use conversation history only to rewrite
   follow-up questions into standalone questions.

Example:

Previous:
Can I change travel after commencement?

Current:
What about before commencement?

knowledge_query:
Can I change travel before commencement?

Return JSON exactly:

{{
    "tools": [],
    "knowledge_query": "",
    "calculator_expression": ""
}}

CONVERSATION HISTORY:

{history_text}

CURRENT QUESTION:

{question}
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
            if tool in {"knowledge", "calculator"}
        ]

        knowledge_query = decision.get(
            "knowledge_query",
            ""
        ).strip()

        calculator_expression = decision.get(
            "calculator_expression",
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
            "knowledge_answer": "",
            "knowledge_found": False,
            "calculator_answer": "",
            "answer": "",
            "sources": []
        }

    def route_after_planner(
        self,
        state
    ):

        if (
            "knowledge"
            in state["selected_tools"]
        ):

            return "knowledge"

        if "calculator" in state["selected_tools"]:

            return "calculator"

        return "knowledge"

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

        if (
            "calculator"
            in state["selected_tools"]
        ):

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

        if (
            "knowledge" in selected_tools
            and "calculator" in selected_tools
        ):

            answer_parts = []

            if state["knowledge_found"]:
                answer_parts.append(knowledge_answer)
            else:
                answer_parts.append(
                    "I could not find the requested information "
                    "in the available knowledge base."
                )

            answer_parts.append(
                f"The calculation result is {calculator_answer}."
            )

            answer = "\n\n".join(answer_parts)

        elif "calculator" in selected_tools:

            answer = calculator_answer

        elif "knowledge" in selected_tools:

            answer = knowledge_answer

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
        
