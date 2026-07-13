import fitz  # PyMuPDF


class PDFService:

    def extract_text(self, pdf_path):
        doc = fitz.open(pdf_path)
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return "\n".join(pages)