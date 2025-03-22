import pdfplumber

def extractContent(col, colNext):
    match col:
        case 'FORM NO.':
            return colNext
        case 'Scheme Type':
            return colNext
        case 'Date Dispensed':
            return colNext
        case 'Patient Name':
            return colNext
        case 'Prescriber Name':
            return colNext
        case 'Patient Address':
            return colNext
        case 'Prescriber':
            return colNext
        case 'Address':
            return colNext
        case _:
            return None

def extractProduct(row):
    if (row[0] == ''):
        return None
    return {
        'Product Name': row[0],
        'Quantity': row[6],
        'Cost': row[9]
    }

def readPdf(pdfPath) -> dict:
    with pdfplumber.open(pdfPath) as pdf:
        dict = {}
        for page in pdf.pages:
            for table in page.extract_tables():
                product_list = False
                for row in list(table):
                    if ('DRUG NAME AND STRENGTH' in row):
                        product_list = True
                    elif product_list:
                        product = extractProduct(row)
                        if product:
                            if 'Products' in dict:
                                dict['Products'].append(product)
                            else:
                                dict['Products'] = [product]
                    else:
                        for col in range(len(row)-1):        
                            value = extractContent(row[col], row[col+1])
                            if value:
                                dict[row[col]] = value
    return dict


if __name__ == "__main__":
    # text = readPdf("./attachments/67dbfeed589f2d479fd92b0d.pdf")
    text = readPdf("./templates/Form Example 1.pdf")
    print(text)