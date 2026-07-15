import json
import hashlib

from pathlib import Path
from datetime import datetime


class DocumentRegistry:

    FILE = Path("document_registry.json")

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

            return json.loads(
                self.FILE.read_text(
                    encoding="utf-8"
                )
            )

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
        file_hash
    ):

        data = self._load()

        return file_hash in data

    def register(
        self,
        file_hash,
        filename,
        pages,
        chunks
    ):

        data = self._load()

        data[file_hash] = {
            "filename": filename,
            "pages": pages,
            "chunks": chunks,
            "uploaded_at": (
                datetime.now()
                .strftime("%Y-%m-%d %H:%M:%S")
            )
        }

        self._save(data)

    def list_documents(self):

        return list(
            self._load().values()
        )

    def count(self):

        return len(
            self._load()
        )

    def clear(self):

        self._save({})