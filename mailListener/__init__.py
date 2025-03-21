import string
import random
import requests

from mailListener.listen import Listen


def username_gen(length=24, chars= string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))  

def password_gen(length=8, chars= string.ascii_letters + string.digits + string.punctuation):
    return ''.join(random.choice(chars) for _ in range(length))  


class EmailClient(Listen):
    token = ""
    domain = ""
    address = ""
    session = requests.Session()

    def __init__(self):
        if not self.domains():
            print("Failed to get domains")

    def domains(self):
        url = "https://api.mail.tm/domains"
        response = self.session.get(url)
        response.raise_for_status()

        try:
            data = response.json()
            for domain in data['hydra:member']:
                if domain['isActive']:
                    self.domain = domain['domain']
                    return True

            raise Exception("No Domain")
        except:
            return False

    def register(self, address=None, password=None, domain=None):
        self.domain = domain if domain else self.domain
        address = address if address else username_gen()
        password = password if password else password_gen()

        url = "https://api.mail.tm/accounts"
        payload = {
            "address": address,
            "password": password
        }
        headers = { 'Content-Type': 'application/json' }
        response = self.session.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        try:
            self.address = data['address']
        except:
            self.address = address

        self.get_token(password)

        if not self.address:
            raise Exception("Failed to make an address")

    def login(self, address, password):
        res = self.session.post(
            "https://api.mail.tm/token",
            json={
                "address": address,
                "password": password,
            }
        )
        res.raise_for_status()
        try:
            self.token = res.json()['token']
            self.address = address
        except:
            raise Exception("Failed to get token")
        
    def get_token(self, password):
        response = self.session.post(
            "https://api.mail.tm/token",
            headers={
                'Content-Type': 'application/json'
                },
            json={
                "address": self.address,
                "password": password
            })
        response.raise_for_status()
        try:
            self.token = response.json()['token']
        except:
            raise Exception("Failed to get token")


if __name__ == "__main__":
    def listener(message):
        print("\nSubject: " + message['subject'])
        print("Content: " + message['text'] if message['text'] else message['html'])

    test = EmailClient()
    print("Domain: " + test.domain)

    test.register()
    print("Email Adress: " + str(test.address))

    test.start(listener)
    print("Waiting for new emails...")

    # test.stop()