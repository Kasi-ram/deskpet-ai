import json
import hashlib
from pathlib import Path


class DocumentRegistry:

    FILE = Path("document_registry.json")

    def __init__(self):

        if not self.FILE.exists():

            self.FILE.write_text("{}")

    def _load(self):

        if not self.FILE.exists():

            self.FILE.write_text("{}")

        return json.loads(
            self.FILE.read_text()
        )

    def _save(self, data):

        self.FILE.write_text(
            json.dumps(
                data,
                indent=4
            )
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
            "chunks": chunks
        }

        self._save(data)