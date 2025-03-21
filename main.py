from email.message import Message
import os
from dotenv import load_dotenv

from database import CSVDatabase
from mailListener import EmailClient



# Load environment variables from .env file
load_dotenv()

# Access variables
EMAIL_USER = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Database instance
db = CSVDatabase()



def check_stock_inventory(product_name: str = 'Ibuprofen') -> bool:
    """Check the stock inventory for a specific product."""
    df = db.stock_inventory.data
    filter = (df['Product Name'] == product_name) & (df['Expiry Status'] != 'Expired') & (df['Quantity'] > 0)
    # print(stock[filter])
    return len(df[filter]) > 0


def add_prescription_to_database(message: Message) -> None:
    """Add a prescription to the database."""

    # Extract the prescription details from the email message
    # TODO: Implement a more robust method to extract the prescription details
    newPrescriptionReceived = {
        'Patient Name': message['From'],
        'Email': message['From'],
        'Doctor Name': message['To'],
        'Product Name': message['Subject'],
        'Quantity': 1,
        'Expiry Date': message['Date']
    }
    
    df = db.prescriptions.data

    # Check if the prescription already exists in the database
    filter = (df['Patient Name'] == message['From']) & (df['Product Name'] == message['Subject'])
    
    if (len(df[filter]) > 0):
        print("Prescription already exists in the database.")
        return
    
    # Add the prescription to the database
    db.prescriptions.insert(newPrescriptionReceived)
    db.prescriptions.save_changes()
    print("Prescription added to the database.")


def email_received(message: Message) -> None:
    """
    Callback function to handle incoming email messages.
    Prints the subject and content of the email.
    """
    print("\nSubject: " + message.subject)
    print("Content: " + message.text if message.text else message.html)

    # add_prescription_to_database(message)



def main() -> None:
    client = EmailClient()
        
    if (EMAIL_USER == None or EMAIL_PASSWORD == None):
        client.register()
    else:
        client.login(EMAIL_USER, EMAIL_PASSWORD)
    print("Email Adress: " + str(client.address))


    client.start(email_received)
    print("Waiting for new emails...")

    print("Press Ctrl+C to stop the listener.")    
    # client.stop()


if __name__ == '__main__':
    main()

    # check_stock_inventory()
