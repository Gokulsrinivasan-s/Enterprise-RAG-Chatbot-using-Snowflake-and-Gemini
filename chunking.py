from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 1. Read PDF
reader = PdfReader("downloads/HR_Policy_Document.pdf")


text = ""

for page in reader.pages:
    text += page.extract_text()


# 2. Create text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)


# 3. Split text
chunks = text_splitter.split_text(text)


# 4. Print chunks
print("Total Chunks:", len(chunks))


for i, chunk in enumerate(chunks):
    print("\n----------------")
    print("Chunk", i+1)
    print(chunk)