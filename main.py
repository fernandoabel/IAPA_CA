import os
import uuid
from dotenv import load_dotenv

from database import CSVDatabase
from mailListener import EmailClient
from mailListener.models.message import MailMessage
from pdfReader.pdfReader import readPdf



# Load environment variables from .env file
load_dotenv()

# Access variables
EMAIL_USER = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Database instance
db = CSVDatabase()



def check_stock_inventory(product_name: str, quantity_needed: str) -> bool:
    """Check the stock inventory for a specific product."""
    df = db.stock_inventory.data
    filter = (df['Product Name'] == product_name) & (df['Expiry Status'] != 'Expired') & (df['Quantity'] >= int(quantity_needed))
    return len(df[filter]) > 0



def add_prescription_to_database(message: MailMessage) -> None:
    """Add a prescription to the database."""

    # Extract the prescription details from the email message PDF
    pdfDetails = readPdf(message.attachment_fileName)
    newPrescriptionReceived = {}
    newPrescriptionReceived['Patient Name'] = pdfDetails['Patient Name']
    newPrescriptionReceived['Age'] = None
    newPrescriptionReceived['Identifier'] = str(uuid.uuid4())
    newPrescriptionReceived['Product Name'] = None
    newPrescriptionReceived['Quantity'] = None
    newPrescriptionReceived['Cost'] = None
    newPrescriptionReceived['Prescriber Name'] = pdfDetails['Prescriber Name']
    newPrescriptionReceived['Prescription Date'] = pdfDetails['Date Dispensed']
    newPrescriptionReceived['Healthcare Plan'] = pdfDetails['Scheme Type']
    newPrescriptionReceived['Email'] = message.fromAddress
    
    # Check if the prescription already exists in the database
    df = db.prescriptions.data
    filter = (df['Patient Name'] == newPrescriptionReceived['Patient Name']) & (df['Prescriber Name'] == newPrescriptionReceived['Prescriber Name']) & (df['Prescription Date'] == newPrescriptionReceived['Prescription Date'])
    if (len(df[filter]) > 0):
        print("Prescription already exists in the database.")
        return
    
    # Add the prescription to the database
    for product in pdfDetails['Products']:
        if (check_stock_inventory(product['Product Name'], product['Quantity']) == True):
            newPrescriptionReceived['Product Name'] = product['Product Name']
            newPrescriptionReceived['Quantity'] = product['Quantity']
            newPrescriptionReceived['Cost'] = product['Cost']
            db.prescriptions.insert(newPrescriptionReceived)
        else:
            print("Product is out of stock: " + product['Product Name'])

    db.prescriptions.save_changes()
    print("Prescription(s) added to the database.")



def main() -> None:
    """
    Callback function to handle incoming email messages.
    Prints the subject and content of the email.
    """
    def email_received(message: MailMessage) -> None:
        print("\nEmail from "+ message.fromAddress + ': ' + message.subject)
        add_prescription_to_database(message)

    client = EmailClient()

    # Register or login to the email client
    if (EMAIL_USER == None or EMAIL_PASSWORD == None):
        client.register()
    else:
        client.login(EMAIL_USER, EMAIL_PASSWORD)
    print("Email Adress: " + str(client.address))

    # Start the email listener
    client.start(email_received)
    print("Waiting for new emails...")

    print("Press Ctrl+C to stop the listener.")    
    # client.stop()


if __name__ == '__main__':
    main()
