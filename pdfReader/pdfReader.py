import pdfplumber


def readPdf(pdfPath):
    with pdfplumber.open(pdfPath) as pdf:
        text = ""
        dict = {}
        for page in pdf.pages:

            text += page.extract_text()
            # tables = page.extract_tables()
            # print(tables)
            # print(len(tables))
            # for (table, i) in enumerate(tables):
            #     print(table, i)
            #     print(dict)
    return text


if __name__ == "__main__":
    # text = readPdf("./attachments/67dbfeed589f2d479fd92b0d.pdf")
    text = readPdf("./templates/Form Example 1.pdf")
    print(text)