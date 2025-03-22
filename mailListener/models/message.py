from config import ATTACHMENTS_FOLDER


class MailMessage:
    def __init__(self, emailJson):        
        self.id = emailJson["id"]
        self.fromAddress = emailJson["from"]["address"]
        self.toAddress = []
        for receiver in emailJson["to"]:
            self.toAddress.append(receiver["address"])
        self.fromName = emailJson["from"]["name"]
        self.subject = emailJson["subject"]
        self.seen = emailJson["seen"]
        self.isDeleted = emailJson["isDeleted"]
        self.size = emailJson["size"]
        self.text = emailJson["text"] if 'text' in emailJson else emailJson["html"]
        self.attachments = [a for a in emailJson["attachments"] if a["contentType"] == "application/pdf"]
        self.hasAttachments = emailJson["hasAttachments"] & len(self.attachments)
        self.attachment_fileName = ATTACHMENTS_FOLDER + self.id + '.pdf'
