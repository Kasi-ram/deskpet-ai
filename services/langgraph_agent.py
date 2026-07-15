import json
import datetime

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from services.groq_service import GroqService
from tools.knowledge_tool import KnowledgeTool
from tools.calculator_tool import CalculatorTool


class AgentState(TypedDict, total=False):

    question: str
    conversation_history: list

    selected_tools: list

    knowledge_query: str
    calculator_expression: str

    knowledge_answer: str
    calculator_answer: str

    answer: str
    sources: list


class LangGraphAgent:

    def __init__(self):

        self.llm = GroqService()

        self.knowledge_tool = KnowledgeTool()
        self.calculator_tool = CalculatorTool()

        graph = StateGraph(AgentState)

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
                "calculator": "calculator",
                "general": "general"
            }
        )

        graph.add_conditional_edges(
            "knowledge",
            self.route_after_knowledge,
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


    def planner_node(self, state):

        question = state["question"]

        conversation_history = state.get(
            "conversation_history",
            []
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
You are the planning node for DeskPet AI.

DeskPet AI is primarily an airline policy assistant.

You have EXACTLY TWO tools.

TOOL: knowledge

Purpose:
Search airline policies, travel rules,
booking rules and internal documents.

Use knowledge for questions about:

- travel changes
- flight changes
- route changes
- date changes
- booking changes
- passenger names
- departure
- commencement of travel
- airline policies
- airline rules
- group bookings
- refunds
- payments
- ticket issuance

TOOL: calculator

Purpose:
Perform mathematical calculations.

IMPORTANT RULES:

1. The ONLY valid tools are:

knowledge
calculator

2. Conversation history is NOT a tool.

3. If the current question is a follow-up,
use conversation history to understand
what the user is referring to.

4. Follow-up phrases include:

"What about before?"
"What about after?"
"What about that?"
"Can I do it before?"
"And after departure?"
"What about before commencement?"

5. If the previous conversation was about
an airline policy and the current question
is a follow-up about that topic,
use the knowledge tool.

6. Rewrite follow-up questions into complete
standalone knowledge questions.

7. Preserve the meaning and subject from the
conversation history.

8. knowledge_query must NEVER be empty when
knowledge is selected.

9. calculator_expression must NEVER be empty
when calculator is selected.

10. Select ALL tools required for compound
questions.

11. If the question does not require airline
knowledge or calculation, return an empty
tools list.

Return ONLY JSON.

Return EXACTLY this structure:

{{
    "tools": [],
    "knowledge_query": "",
    "calculator_expression": ""
}}

EXAMPLE 1

Question:

Can I change my travel after commencement?

Response:

{{
    "tools": ["knowledge"],
    "knowledge_query":
        "Can I change my travel after commencement?",
    "calculator_expression": ""
}}

EXAMPLE 2

Conversation history:

user: Can I change my travel after commencement?

assistant: No date, flight or route changes are
allowed once travel has commenced.

Current question:

What about before commencement?

Response:

{{
    "tools": ["knowledge"],
    "knowledge_query":
        "Can I change my travel before commencement?",
    "calculator_expression": ""
}}

EXAMPLE 3

Question:

What is 25 * 18?

Response:

{{
    "tools": ["calculator"],
    "knowledge_query": "",
    "calculator_expression": "25 * 18"
}}

EXAMPLE 4

Question:

What is 25 * 18 and can I change my travel
after commencement?

Response:

{{
    "tools": ["knowledge", "calculator"],
    "knowledge_query":
        "Can I change my travel after commencement?",
    "calculator_expression": "25 * 18"
}}

EXAMPLE 5

Question:

What is the date today?

Response:

{{
    "tools": [],
    "knowledge_query": "",
    "calculator_expression": ""
}}

CONVERSATION HISTORY:

{history_text}

CURRENT USER QUESTION:

{question}
"""

        response = self.llm.ask_json(prompt)

        print("\nPLANNER RESPONSE")
        print(response)

        decision = json.loads(response)

        allowed_tools = {
            "knowledge",
            "calculator"
        }

        selected_tools = [
            tool
            for tool in decision.get(
                "tools",
                []
            )
            if tool in allowed_tools
        ]

        knowledge_query = (
            decision.get(
                "knowledge_query",
                ""
            )
            or ""
        ).strip()

        calculator_expression = (
            decision.get(
                "calculator_expression",
                ""
            )
            or ""
        ).strip()

        if (
            "knowledge" in selected_tools
            and not knowledge_query
        ):

            knowledge_query = question

        if (
            "calculator" in selected_tools
            and not calculator_expression
        ):

            calculator_expression = question

        return {
            "selected_tools": selected_tools,
            "knowledge_query": knowledge_query,
            "calculator_expression": (
                calculator_expression
            ),

            # clear previous turn data
            "knowledge_answer": "",
            "calculator_answer": "",
            "answer": "",
            "sources": []
        }


    def route_after_planner(self, state):

        tools = state.get(
            "selected_tools",
            []
        )

        if "knowledge" in tools:
            return "knowledge"

        if "calculator" in tools:
            return "calculator"

        return "general"


    def knowledge_node(self, state):

        query = state.get(
            "knowledge_query",
            ""
        )

        if not query.strip():

            return {
                "knowledge_answer": (
                    "I could not determine the "
                    "knowledge question."
                ),
                "sources": []
            }

        print("\nKNOWLEDGE QUERY")
        print(query)

        result = self.knowledge_tool.execute(
            query
        )

        return {
            "knowledge_answer": result["answer"],
            "sources": result["sources"]
        }


    def route_after_knowledge(self, state):

        selected_tools = state.get(
            "selected_tools",
            []
        )

        if "calculator" in selected_tools:
            return "calculator"

        return "final_answer"


    def calculator_node(self, state):

        expression = state.get(
            "calculator_expression",
            ""
        )

        if not expression.strip():

            return {
                "calculator_answer": (
                    "No calculation expression "
                    "was provided."
                )
            }

        print("\nCALCULATOR EXPRESSION")
        print(expression)

        result = self.calculator_tool.execute(
            expression
        )

        return {
            "calculator_answer": result["answer"]
        }


    def general_node(self, state):

        question = state["question"]

        today = datetime.date.today()

        conversation_history = state.get(
            "conversation_history",
            []
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
You are DeskPet AI.

Answer the user's general question directly.

Do not invent airline policy information.

If an airline policy question reaches this node,
say that airline policy knowledge must be searched.

Today's system date is:

{today.strftime("%d %B %Y")}

CONVERSATION HISTORY:

{history_text}

USER QUESTION:

{question}
"""

        answer = self.llm.ask(prompt)

        return {
            "answer": answer
        }


    def final_answer_node(self, state):

        selected_tools = state.get(
            "selected_tools",
            []
        )

        knowledge_answer = state.get(
            "knowledge_answer",
            ""
        )

        calculator_answer = state.get(
            "calculator_answer",
            ""
        )

        if selected_tools == ["knowledge"]:

            answer = knowledge_answer

        elif selected_tools == ["calculator"]:

            answer = calculator_answer

        elif (
            "knowledge" in selected_tools
            and "calculator" in selected_tools
        ):

            answer = (
                f"{knowledge_answer}\n\n"
                f"The calculation result is "
                f"{calculator_answer}."
            )

        else:

            answer = state.get(
                "answer",
                ""
            )

        history = state.get(
            "conversation_history",
            []
        )

        updated_history = history + [
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
            "conversation_history": updated_history,
            "sources": state.get(
                "sources",
                []
            )
        }


    def ask(
        self,
        question,
        thread_id="default"
    ):

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # IMPORTANT:
        # Do not pass conversation_history=[]
        # LangGraph restores it using the checkpointer.

        result = self.graph.invoke(
            {
                "question": question,

                "selected_tools": [],

                "knowledge_query": "",
                "calculator_expression": "",

                "knowledge_answer": "",
                "calculator_answer": "",

                "answer": "",
                "sources": []
            },
            config=config
        )

        return {
            "answer": result.get(
                "answer",
                ""
            ),
            "sources": result.get(
                "sources",
                []
            )
        }
    
    def stream(
    self,
    question,
    thread_id="default"
    ):

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        input_state = {
            "question": question,

            "selected_tools": [],

            "knowledge_query": "",
            "calculator_expression": "",

            "knowledge_answer": "",
            "calculator_answer": "",

            "answer": "",
            "sources": []
        }

        final_result = None

        for event in self.graph.stream(
            input_state,
            config=config,
            stream_mode="updates"
        ):

            for node_name, update in event.items():

                yield {
                    "type": "node",
                    "node": node_name
                }

                if node_name == "final_answer":

                    final_result = update

        if final_result:

            yield {
                "type": "result",
                "answer": final_result.get(
                    "answer",
                    ""
                ),
                "sources": final_result.get(
                    "sources",
                    []
                )
            }