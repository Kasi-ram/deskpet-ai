from pathlib import Path
import shutil
from datetime import datetime


PROJECT_ROOT = Path(__file__).parent

FILES_TO_UPDATE = [
    PROJECT_ROOT / "services" / "rag_service.py",
    PROJECT_ROOT / "services" / "evidence_service.py",
    PROJECT_ROOT / "services" / "agent_service.py",
]

BACKUP_DIR = PROJECT_ROOT / (
    "backup_before_openai_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)


def backup_files():
    print("\nCreating backup...")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in FILES_TO_UPDATE:

        if not file_path.exists():
            print(f"SKIP: {file_path} not found")
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


def create_openai_service():

    file_path = (
        PROJECT_ROOT
        / "services"
        / "openai_service.py"
    )

    content = '''import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class OpenAIService:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5-mini"
        )

    def ask(self, prompt):

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return response.output_text

    def stream(self, prompt):

        with self.client.responses.stream(
            model=self.model,
            input=prompt
        ) as stream:

            for event in stream:

                if (
                    event.type
                    == "response.output_text.delta"
                ):
                    yield event.delta
'''

    file_path.write_text(
        content,
        encoding="utf-8"
    )

    print(
        "CREATED: services/openai_service.py"
    )


def replace_in_file(
    relative_path,
    replacements
):

    file_path = PROJECT_ROOT / relative_path

    if not file_path.exists():

        print(
            f"SKIP: {relative_path} not found"
        )

        return

    content = file_path.read_text(
        encoding="utf-8"
    )

    original_content = content

    for old, new in replacements:

        content = content.replace(
            old,
            new
        )

    if content == original_content:

        print(
            f"NO CHANGE: {relative_path}"
        )

        return

    file_path.write_text(
        content,
        encoding="utf-8"
    )

    print(
        f"UPDATED: {relative_path}"
    )


def update_rag_service():

    replace_in_file(
        "services/rag_service.py",
        [
            (
                "from services.gemini_service "
                "import GeminiService",
                "from services.openai_service "
                "import OpenAIService"
            ),
            (
                "self.gemini_service = GeminiService()",
                "self.llm_service = OpenAIService()"
            ),
            (
                "self.gemini_service.ask(prompt)",
                "self.llm_service.ask(prompt)"
            ),
            (
                "self.gemini_service.stream(prompt)",
                "self.llm_service.stream(prompt)"
            ),
        ]
    )


def update_evidence_service():

    replace_in_file(
        "services/evidence_service.py",
        [
            (
                "from services.gemini_service "
                "import GeminiService",
                "from services.openai_service "
                "import OpenAIService"
            ),
            (
                "self.gemini_service = GeminiService()",
                "self.llm_service = OpenAIService()"
            ),
            (
                "self.gemini_service.ask(prompt)",
                "self.llm_service.ask(prompt)"
            ),
        ]
    )


def update_agent_service():

    replace_in_file(
        "services/agent_service.py",
        [
            (
                "from services.gemini_service "
                "import GeminiService",
                "from services.openai_service "
                "import OpenAIService"
            ),
            (
                "self.gemini = GeminiService()",
                "self.llm = OpenAIService()"
            ),
            (
                "self.gemini.ask(prompt)",
                "self.llm.ask(prompt)"
            ),
        ]
    )


def update_env():

    env_path = PROJECT_ROOT / ".env"

    if not env_path.exists():

        print(
            "SKIP: .env not found"
        )

        return

    content = env_path.read_text(
        encoding="utf-8"
    )

    if "OPENAI_API_KEY=" not in content:

        content += (
            "\n"
            "OPENAI_API_KEY=YOUR_OPENAI_API_KEY\n"
        )

    if "OPENAI_MODEL=" not in content:

        content += (
            "OPENAI_MODEL=gpt-5-mini\n"
        )

    env_path.write_text(
        content,
        encoding="utf-8"
    )

    print("UPDATED: .env")


def main():

    print(
        "\nDESKPET AI - OPENAI MIGRATION"
    )

    print("=" * 50)

    backup_files()

    create_openai_service()

    update_rag_service()

    update_evidence_service()

    update_agent_service()

    update_env()

    print("\n" + "=" * 50)

    print("Migration completed.")

    print(
        f"\nBackup location:\n{BACKUP_DIR}"
    )

    print(
        "\nNEXT STEPS:"
    )

    print(
        "1. pip install openai"
    )

    print(
        "2. Add OPENAI_API_KEY to .env"
    )

    print(
        "3. python test_agent.py"
    )


if __name__ == "__main__":
    main()