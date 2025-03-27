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

def check_regulatory_requirements(product_name: str) -> bool:
    """Check the regulatory requirements for a specific product."""
    df = db.regulations.data
    filter = (df['Product Name'] == product_name) & (df['Meets Requirements'] == 'TRUE')
    return len(df[filter]) > 0


def add_prescription_to_database(message: MailMessage) -> None:
    """Add a prescription to the database."""

    # Extract the prescription details from the email message PDF
    pdfDetails = readPdf(message.attachment_fileName)
    newPrescriptionReceived = {}
    # Patient Details
    newPrescriptionReceived['Patient Name'] = pdfDetails['Patient Name']
    newPrescriptionReceived['Healthcare Plan'] = pdfDetails['Scheme Type']
    if 'Patient Email' in pdfDetails:
        newPrescriptionReceived['Patient Email'] =  pdfDetails['Patient Email']
    else:
        newPrescriptionReceived['Patient Email'] = None
    # Product Details
    newPrescriptionReceived['Product Name'] = None
    newPrescriptionReceived['Quantity'] = None
    newPrescriptionReceived['Cost'] = None
    # Prescriber Details
    newPrescriptionReceived['Prescriber Name'] = pdfDetails['Prescriber Name']
    newPrescriptionReceived['Prescription Date'] = pdfDetails['Date Dispensed']
    newPrescriptionReceived['Prescriber Email'] = message.fromAddress
    newPrescriptionReceived['Approval Status'] = 'Pending'
    newPrescriptionReceived['In Stock'] = None

    # Check if the prescription already exists in the database
    df = db.prescriptions.data
    filter = (df['Patient Name'] == newPrescriptionReceived['Patient Name']) & (df['Prescriber Name'] == newPrescriptionReceived['Prescriber Name']) & (df['Prescription Date'] == newPrescriptionReceived['Prescription Date'])
    if (len(df[filter]) > 0):
        print("Prescription already exists in the database.")
        return
    
    # Add the prescription to the database
    for product in pdfDetails['Products']:
        newPrescriptionReceived['Product Name'] = product['Product Name']
        newPrescriptionReceived['Quantity'] = product['Quantity']
        newPrescriptionReceived['Cost'] = product['Cost']

        db.prescriptions.insert(newPrescriptionReceived)            
        print(f"New Prescription - {newPrescriptionReceived['Patient Name']} ({newPrescriptionReceived['Prescription Date']}) - Product {newPrescriptionReceived['Product Name']} - {newPrescriptionReceived['Approval Status']}")

    db.prescriptions.save_changes()

def automated_regulatory_check() -> None:
    """Automated regulatory check for all received prescriptions which are in Pending Status."""

    df = db.prescriptions.data
    filter = df['Approval Status'] == 'Pending'

    for index, prescription in df[filter].iterrows():

        # TODO - Check if the product is in stock and meets regulatory requirements
        if check_regulatory_requirements(prescription['Product Name']):
            print('111Approved')
        else:
            print('222Not approved')
            
        status =  'Approved' if check_regulatory_requirements(prescription['Product Name']) else 'Not approved'
        print(status)
        prescription['Approval Status'] = status
        db.prescriptions.update(prescription['ID'], prescription)
        print(f"New Prescription - {prescription['Patient Name']} ({prescription['Prescription Date']}) - Product {prescription['Product Name']} - {prescription['Approval Status']} due to regulatory requirements")
    
    db.prescriptions.save_changes()

        
def automated_stock_check() -> None:
    """Automated stock check for all received prescriptions which are in Approved Status."""

    df = db.prescriptions.data
    filter = df['Approval Status'] == 'Approved'
    
    for index, prescription in df[filter].iterrows():    

        if check_stock_inventory(prescription['Product Name'], prescription['Quantity']) == False:
            prescription['In Stock'] = 'FALSE'
            print("Product is out of stock: " + prescription['Product Name'])
        else:
            prescription['In Stock'] = 'TRUE'
        db.prescriptions.update(prescription['ID'], prescription)
    
    db.prescriptions.save_changes()


def main() -> None:
    """
    Callback function to handle incoming email messages.
    Prints the subject and content of the email.
    """
    def email_received(message: MailMessage) -> None:
        print("\nEmail from "+ message.fromAddress + ': ' + message.subject)

        # Process the email received, extracts the attachment details and adds the prescription to the database
        add_prescription_to_database(message)

        # Automated verification against the regulatory database (for Pending prescriptions only)
        automated_regulatory_check()

        # Automated verification against the stock inventory (for Approved prescriptions only)
        automated_stock_check()

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
