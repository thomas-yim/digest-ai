# importing required modules
from PyPDF2 import PdfReader

def read_pdf(filename):
    allText = []
    
    reader = PdfReader(filename)
    
    for page in reader.pages:
        curText = page.extract_text()
        curText = curText.lstrip('0123456789.- ')
        allText.append(curText)
    return "\n".join(allText)