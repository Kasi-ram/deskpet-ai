from services.langgraph_agent import LangGraphAgent


agent = LangGraphAgent()

thread_id = "kasiraman-test"


questions = [
    "Can I change my travel after commencement?",
    "What about before commencement?"
]


for question in questions:

    print("\nQUESTION")
    print(question)

    response = agent.ask(
        question,
        thread_id=thread_id
    )

    print("\nANSWER")
    print(response["answer"])

    print("-" * 60)