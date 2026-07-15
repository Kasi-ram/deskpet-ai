from pathlib import Path
import shutil
from datetime import datetime


PROJECT_ROOT = Path(__file__).parent

SERVICE_FILES = [
    PROJECT_ROOT / "services" / "rag_service.py",
    PROJECT_ROOT / "services" / "evidence_service.py",
    PROJECT_ROOT / "services" / "agent_service.py",
]

BACKUP_DIR = PROJECT_ROOT / (
    "backup_before_groq_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)


def backup_files():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in SERVICE_FILES:

        if not file_path.exists():
            print(f"SKIP: {file_path}")
            continue

        relative_path = file_path.relative_to(PROJECT_ROOT)
        backup_path = BACKUP_DIR / relative_path

        backup_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(
            file_path,
            backup_path
        )

        print(f"BACKUP: {relative_path}")


def create_groq_service():

    file_path = (
        PROJECT_ROOT
        / "services"
        / "groq_service.py"
    )

    content = '''import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class GroqService:

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.model = os.getenv(
            "GROQ_MODEL",
            "llama-3.1-8b-instant"
        )

    def ask(self, prompt):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    def stream(self, prompt):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        for chunk in response:

            content = chunk.choices[0].delta.content

            if content:
                yield content
'''

    file_path.write_text(
        content,
        encoding="utf-8"
    )

    print("CREATED: services/groq_service.py")


def replace_in_file(relative_path, replacements):

    file_path = PROJECT_ROOT / relative_path

    if not file_path.exists():
        print(f"SKIP: {relative_path}")
        return

    content = file_path.read_text(
        encoding="utf-8"
    )

    original_content = content

    for old, new in replacements:
        content = content.replace(old, new)

    if content == original_content:
        print(f"NO CHANGE: {relative_path}")
        return

    file_path.write_text(
        content,
        encoding="utf-8"
    )

    print(f"UPDATED: {relative_path}")


def update_rag_service():

    replace_in_file(
        "services/rag_service.py",
        [
            (
                "from services.openai_service import OpenAIService",
                "from services.groq_service import GroqService"
            ),
            (
                "self.llm_service = OpenAIService()",
                "self.llm_service = GroqService()"
            ),
        ]
    )


def update_evidence_service():

    replace_in_file(
        "services/evidence_service.py",
        [
            (
                "from services.openai_service import OpenAIService",
                "from services.groq_service import GroqService"
            ),
            (
                "self.llm_service = OpenAIService()",
                "self.llm_service = GroqService()"
            ),
        ]
    )


def update_agent_service():

    replace_in_file(
        "services/agent_service.py",
        [
            (
                "from services.openai_service import OpenAIService",
                "from services.groq_service import GroqService"
            ),
            (
                "self.llm = OpenAIService()",
                "self.llm = GroqService()"
            ),
        ]
    )


def update_env():

    env_path = PROJECT_ROOT / ".env"

    if not env_path.exists():
        env_path.touch()

    content = env_path.read_text(
        encoding="utf-8"
    )

    if "GROQ_API_KEY=" not in content:
        content += (
            "\nGROQ_API_KEY=YOUR_GROQ_API_KEY\n"
        )

    if "GROQ_MODEL=" not in content:
        content += (
            "GROQ_MODEL=llama-3.1-8b-instant\n"
        )

    env_path.write_text(
        content,
        encoding="utf-8"
    )

    print("UPDATED: .env")


def main():

    print("\nDESKPET AI - GROQ MIGRATION")
    print("=" * 50)

    backup_files()

    create_groq_service()

    update_rag_service()

    update_evidence_service()

    update_agent_service()

    update_env()

    print("\n" + "=" * 50)

    print("Migration completed.")

    print(f"\nBackup: {BACKUP_DIR}")

    print("\nNEXT:")
    print("1. pip install groq")
    print("2. Create Groq API key")
    print("3. Update GROQ_API_KEY in .env")
    print("4. python test_agent.py")


if __name__ == "__main__":
    main()