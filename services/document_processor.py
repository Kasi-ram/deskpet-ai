import os

from services.pdf_service import PDFService
from services.text_service import TextService

class DocumentProcessor:

    def __init__(self):

        self.pdf_service = PDFService()
        self.text_service = TextService()

    def process(
            self,
            uploaded_file
        ):

        extension = (
                uploaded_file.name
                .split(".")[-1]
                .lower()
            )

        if extension == "pdf":

             return self.pdf_service.extract_pages(
                 uploaded_file.getvalue()
             )
        
        if extension == "txt":

            return self.text_service.extract_pages(
                uploaded_file.getvalue()
            )

        raise Exception(
            f"Unsupported file type: {extension}"
        )