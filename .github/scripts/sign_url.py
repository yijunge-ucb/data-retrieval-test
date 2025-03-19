import os
import json
from google.auth import credentials
from google.cloud import storage
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError
import datetime

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
        
        env_file = os.getenv('GITHUB_ENV')
        existing_urls = os.getenv("signedURL", "")
        updated_urls = f"{existing_urls},{url}" if existing_urls else url
        with open(env_file, "a") as myfile:
            myfile.write(f"signedURL={updated_urls}\n")
        

    except DefaultCredentialsError as e:
        print(f"Error: Unable to authenticate with Google Cloud. {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None



extracted_link = os.getenv('EXTRACTED_LINK')
all_links = extracted_link.split(',')
for link in all_links:
    # Your bucket and object details
    bucket_name = link.split('//')[1].split('/')[0]
    object_name = '/'.join(link.split('//')[1].split('/')[1:])

    # Generate signed URL
    generate_signed_url(bucket_name, object_name)
