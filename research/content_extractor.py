from bs4 import BeautifulSoup
from readability import Document


def extract_content(html):

    try:

        doc = Document(html)

        summary = doc.summary()

        soup = BeautifulSoup(summary, "html.parser")

        return soup.get_text()

    except:

        return ""