import fitz


class PDFService:

    def extract_pages(self, pdf_path):
        pages = []

        with fitz.open(pdf_path) as doc:

            for page_number, page in enumerate(
                doc,
                start=1
            ):
                pages.append({
                    "page": page_number,
                    "text": page.get_text()
                })

        return pages