from services.agent_service import AgentService


agent = AgentService()


questions = [
    "Can I change my travel after commencement?",
    "What is 25 * 18?"
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