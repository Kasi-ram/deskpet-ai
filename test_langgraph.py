from services.langgraph_agent import LangGraphAgent


agent = LangGraphAgent()


questions = [
    "Can I change my travel after commencement?",
    "What is 25 * 18?",
    (
        "What is 25 * 18 and can I change "
        "my travel after commencement?"
    )
]


for question in questions:

    print("\nQUESTION")
    print(question)

    response = agent.ask(question)

    print("\nANSWER")
    print(response["answer"])

    print("\nSOURCES")
    print(response["sources"])

    print("-" * 60)