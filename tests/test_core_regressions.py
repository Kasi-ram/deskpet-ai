import sys
import tempfile
import types
import unittest
from pathlib import Path

from services.document_registry import DocumentRegistry
from tools.calculator_tool import CalculatorTool


class FakeGroqService:

    def ask_json(self, prompt):
        return (
            '{"tools": ["knowledge"], '
            '"knowledge_query": "policy", '
            '"calculator_expression": ""}'
        )

    def ask(self, prompt):
        return "general answer"


class FakeKnowledgeTool:

    calls = []

    def execute(self, question, knowledge_base_id="default"):
        self.calls.append((question, knowledge_base_id))
        return {
            "answer": "knowledge answer",
            "found": True,
            "sources": []
        }


class FakeCalculatorTool:

    def execute(self, expression):
        return {"answer": expression, "sources": []}


def install_agent_stubs():

    for module_name, class_name, value in [
        ("services.groq_service", "GroqService", FakeGroqService),
        ("tools.knowledge_tool", "KnowledgeTool", FakeKnowledgeTool),
        ("tools.calculator_tool", "CalculatorTool", FakeCalculatorTool)
    ]:
        module = types.ModuleType(module_name)
        setattr(module, class_name, value)
        sys.modules[module_name] = module


install_agent_stubs()

from services.langgraph_agent import LangGraphAgent


class CalculatorToolTests(unittest.TestCase):

    def test_calculates_numeric_expression(self):

        result = CalculatorTool().execute("2 * (3 + 4)")

        self.assertEqual(result["answer"], "14")

    def test_rejects_non_numeric_literals(self):

        result = CalculatorTool().execute("'not a number'")

        self.assertEqual(
            result["answer"],
            "Unable to calculate the expression."
        )


class DocumentRegistryTests(unittest.TestCase):

    def test_documents_are_isolated_by_knowledge_base(self):

        original_file = DocumentRegistry.FILE

        with tempfile.TemporaryDirectory() as directory:
            DocumentRegistry.FILE = Path(directory) / "registry.json"

            try:
                registry = DocumentRegistry()
                registry.register("same-hash", "a.txt", 1, 1, "tenant-a")
                registry.register("same-hash", "b.txt", 1, 1, "tenant-b")

                self.assertEqual(registry.count("tenant-a"), 1)
                self.assertEqual(registry.count("tenant-b"), 1)
                self.assertEqual(
                    registry.list_documents("tenant-a")[0]["filename"],
                    "a.txt"
                )
            finally:
                DocumentRegistry.FILE = original_file


class LangGraphAgentTests(unittest.TestCase):

    def setUp(self):

        FakeKnowledgeTool.calls.clear()
        self.agent = LangGraphAgent()

    def test_checkpoint_memory_is_retained(self):

        self.agent.ask("1 + 1", thread_id="memory")
        self.agent.ask("2 + 2", thread_id="memory")

        state = self.agent.graph.get_state(
            {"configurable": {"thread_id": "memory"}}
        ).values

        self.assertEqual(len(state["conversation_history"]), 4)

    def test_knowledge_request_uses_the_given_namespace(self):

        self.agent.ask(
            "Tell me the policy",
            thread_id="namespace",
            knowledge_base_id="tenant-a"
        )

        self.assertEqual(
            FakeKnowledgeTool.calls,
            [("policy", "tenant-a")]
        )


if __name__ == "__main__":
    unittest.main()
