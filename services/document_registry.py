import json
import hashlib

from pathlib import Path
from datetime import datetime


class DocumentRegistry:

    FILE = Path(__file__).resolve().parents[1] / "document_registry.json"

    def __init__(self):

        self._ensure_file()

    def _ensure_file(self):

        if not self.FILE.exists():

            self.FILE.write_text(
                "{}",
                encoding="utf-8"
            )

    def _load(self):

        self._ensure_file()

        try:

            data = json.loads(
                self.FILE.read_text(
                    encoding="utf-8"
                )
            )

            # Migrate the legacy flat registry in memory. It will be
            # persisted in this namespaced format on the next write.
            if data and all(
                "filename" in value
                for value in data.values()
                if isinstance(value, dict)
            ):
                return {"default": data}

            return data

        except json.JSONDecodeError:

            return {}

    def _save(self, data):

        self.FILE.write_text(
            json.dumps(
                data,
                indent=4
            ),
            encoding="utf-8"
        )

    def calculate_hash(
        self,
        file_bytes
    ):

        return hashlib.sha256(
            file_bytes
        ).hexdigest()

    def exists(
        self,
        file_hash,
        knowledge_base_id="default"
    ):

        data = self._load()

        return file_hash in data.get(
            knowledge_base_id,
            {}
        )

    def register(
        self,
        file_hash,
        filename,
        pages,
        chunks,
        knowledge_base_id="default"
    ):

        data = self._load()

        documents = data.setdefault(
            knowledge_base_id,
            {}
        )

        documents[file_hash] = {
            "filename": filename,
            "pages": pages,
            "chunks": chunks,
            "uploaded_at": (
                datetime.now()
                .strftime("%Y-%m-%d %H:%M:%S")
            )
        }

        self._save(data)

    def list_documents(self, knowledge_base_id="default"):

        return list(
            self._load().get(
                knowledge_base_id,
                {}
            ).values()
        )

    def count(self, knowledge_base_id="default"):

        return len(
            self._load().get(
                knowledge_base_id,
                {}
            )
        )

    def clear(self, knowledge_base_id="default"):

        data = self._load()
        data.pop(knowledge_base_id, None)
        self._save(data)
