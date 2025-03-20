# IAPA_CA

### Listening to Mail Inbox

For the purpose of listening received emails, the disposable mail inbox [Mail.tm](https://mail.tm/en/) is being used.

Configure a `.env` file defining User and Password names to login to.

```
EMAIL_ADDRESS=johndoe@mailtm.com
EMAIL_PASSWORD=password
```

If you don't define `.env` file with existing credentials, a new email account will be created every time you run code.

Once existing email account is connected or created, the application reads the whole inbox and starts to listen for new received emails (and attachments).

### Email Processing
