import os
from dotenv import load_dotenv

from mailListener.emailClient import EmailClient


# Load environment variables from .env file
load_dotenv()

# Access variables
EMAIL_USER = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")



def listener(message):
    """
    Callback function to handle incoming email messages.
    Prints the subject and content of the email.
    """
    print("\nSubject: " + message.subject)
    print("Content: " + message.text if message.text else message.html)


def main() -> None:

    client = EmailClient()
        
    if (EMAIL_USER == None or EMAIL_PASSWORD == None):
        client.register()
    else:
        client.login(EMAIL_USER, EMAIL_PASSWORD)
    print("Email Adress: " + str(client.address))

    client.start(listener)
    print("Waiting for new emails...")

    print("Press Ctrl+C to stop the listener.")    
    # client.stop()


if __name__ == '__main__':
    main()
