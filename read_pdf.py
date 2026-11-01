from pypdf import PdfReader

# Read PDF
reader = PdfReader("downloads/HR_Policy_Document.pdf")

print("Total Pages:", len(reader.pages))

print("\n========== PDF CONTENT ==========\n")

for page_no, page in enumerate(reader.pages, start=1):
    print(f"\n----- Page {page_no} -----\n")

    text = page.extract_text()

    print(text)