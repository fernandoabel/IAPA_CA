import time
from threading import Thread

from config import ATTACHMENTS_FOLDER
from mailListener.models.message import MailMessage

class Listen:
    listen = False
    message_ids = []

    def message_list(self):
        url = "https://api.mail.tm/messages"
        headers = { 'Authorization': 'Bearer ' + self.token }
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return  [
                    msg for i, msg in enumerate(data['hydra:member']) 
                        if data['hydra:member'][i]['id'] not in self.message_ids
                ]

    def message(self, idx):
        url = "https://api.mail.tm/messages/" + idx
        headers = { 'Authorization': 'Bearer ' + self.token }
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def download_message_pdf_attachments(self, idx, attachments):
        attachments = [a for a in attachments if a["contentType"] == "application/pdf"]
        for attachment in attachments:
            attachment_response = self.session.get(
                f"https://api.mail.tm{attachment["downloadUrl"]}",
                headers={
                    "Authorization": "Bearer " + self.token,
                    "Content-Type": attachment["contentType"],
                }
            )
            
            fileName = ATTACHMENTS_FOLDER + idx + '.pdf'

            if attachment_response.status_code == 200:
                with open(fileName, "wb") as file:
                    file.write(attachment_response.content)
            else:
                print(f"Error downloading {fileName}: {attachment_response.status_code} - {attachment_response.text}")

    def run(self):
        while self.listen:
            for message in self.message_list():
                self.message_ids.append(message['id'])
                message = self.message(message['id'])
                self.download_message_pdf_attachments(message['id'], message["attachments"])
                self.listener(MailMessage(message))

            time.sleep(self.interval)

    def start(self, listener, interval=3):
        if self.listen:
            self.stop()

        self.listener = listener
        self.interval = interval
        self.listen = True

        # Start listening thread
        self.thread = Thread(target=self.run)
        self.thread.start()
    
    def stop(self):
        self.listen = False
        self.thread.join()