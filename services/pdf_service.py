import fitz


class PDFService:

    def extract_text(self, pdf_path):

        doc = fitz.open(pdf_path)

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        return text

    def extract_pages(self, pdf_path):

        doc = fitz.open(pdf_path)

        pages = []

        try:

            for page_number, page in enumerate(
                doc,
                start=1
            ):

                text = page.get_text()

                if text and text.strip():

                    pages.append(
                        (
                            page_number,
                            text.strip()
                        )
                    )

        finally:

            doc.close()

        return pages