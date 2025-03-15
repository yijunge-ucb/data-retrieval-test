import os
import base64
import json
import time
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64


def decode_and_save_token(encoded_token, output_file_path):
    try:
        # Decode the base64-encoded token
        decoded_token = base64.b64decode(encoded_token)
        
        # Write the decoded token to a file
        with open(output_file_path, 'wb') as output_file:
            output_file.write(decoded_token)
        
        print(f"Decoded token successfully saved to {output_file_path}")
    except Exception as e:
        print(f"Error occurred while decoding the token and saving it to a file: {e}")


# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail_api():
    """Authenticate and return the Gmail API service."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    encoded_token = os.getenv('TOKEN_PICKLE')
    output_file_path = "token.pickle"  # File where the decoded token will be saved
    decode_and_save_token(encoded_token, output_file_path)
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        # Build the Gmail API client
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as error:
        print(f'An error occurred: {error}')
        return None

def create_message(sender, to, subject, body):
    """Create an email message."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(body)
    message.attach(msg)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(service, sender, to, subject, body):
    """Send an email message."""
    try:
        message = create_message(sender, to, subject, body)
        message = service.users().messages().send(userId='me', body=message).execute()
        print(f'Message sent! Message Id: {message["id"]}')
    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    # Authenticate and build the Gmail API service
    service = authenticate_gmail_api()
    issue_url = os.getenv('ISSUE_URL')
    
    if service:
        sender = 'yijunge@berkeley.edu'  # Replace with your email address
        recipient = os.getenv('RECEIVER_EMAIL')  # Replace with recipient's email
        subject = 'Your Request for Retrieving Old Files'
        body = 'In response to your request {issue_url}, please find the URL to the files you requested. \n ' + os.getenv('SIGNEDURL')
        

        # Send the email
        send_email(service, sender, recipient, subject, body)
