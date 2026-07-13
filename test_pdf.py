from services.pdf_service import PDFService

pdf = PDFService()

text = pdf.extract_text("data/airline_policy.pdf")

print(text)