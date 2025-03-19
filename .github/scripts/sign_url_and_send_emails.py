import os
import base64
import json
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64


from google.auth import credentials
from google.cloud import storage
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError
import datetime


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

def generate_signed_url(bucket_name, object_name):
    try:
        # Get the service account JSON from the GitHub secret (as environment variable)
        service_account_json = os.getenv('GCP_SERVICE_ACCOUNT_KEY')

        if not service_account_json:
            raise ValueError("Service account key is not set in environment variables.")

        # Parse the JSON from the environment variable
        credentials_info = json.loads(service_account_json)

        # Load the credentials from the parsed JSON
        credentials = service_account.Credentials.from_service_account_info(credentials_info)

        # Initialize Google Cloud Storage client with the loaded credentials
        storage_client = storage.Client(credentials=credentials, project=credentials.project_id)

        # Get the bucket
        bucket = storage_client.bucket(bucket_name)

        # Get the blob (file in GCS)
        blob = bucket.blob(object_name)
        # Generate a signed URL for the object
        url = blob.generate_signed_url(
            expiration=datetime.timedelta(days=7),  # Set the expiration time (e.g., 7 days)
            method='GET',  # Specify the HTTP method (e.g., GET for download)
        )
        
        return url
        

    except DefaultCredentialsError as e:
        print(f"Error: Unable to authenticate with Google Cloud. {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    # Sign URLs
    extracted_link = os.getenv('EXTRACTED_LINK')
    all_links = extracted_link.split(',')
    results = []
    for link in all_links:
        # Your bucket and object details
        bucket_name = link.split('//')[1].split('/')[0]
        object_name = '/'.join(link.split('//')[1].split('/')[1:])

        # Generate signed URL
        url = generate_signed_url(bucket_name, object_name)
        results.append(url)


    # Authenticate and build the Gmail API service
    service = authenticate_gmail_api()
    issue_url = os.getenv('ISSUE_URL')
    
    if service:
        sender = 'datahub-dataretrieval@berkeley.edu'  # Replace with your email address
        recipient = os.getenv('RECEIVER_EMAIL')  # Replace with recipient's email
        subject = 'Your Request for Retrieving Old Files'
        
        # Format the message
        body = f"\n In response to your request [{issue_url}], please find the URL(s) to the files you requested:\n\n"
     
        for url in results:
            body += f"{url}\n\n"

        # Send the email
        send_email(service, sender, recipient, subject, body)
