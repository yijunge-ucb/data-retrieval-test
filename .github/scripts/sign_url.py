import os
from google.cloud import storage
from google.oauth2 import service_account
import datetime

# Load service account credentials
credentials = service_account.Credentials.from_service_account_file('${HOME}/gcp-service-account.json')

# Initialize the Google Cloud Storage client
storage_client = storage.Client(credentials=credentials)

extracted_link = os.getenv('EXTRACTED_LINK')
# Your bucket and object details
bucket_name = link.split('//')[1].split('/')[0]
object_name = '/'.join(link.split('//')[1].split('/')[1:])

# Create the bucket and object blob references
bucket = storage_client.get_bucket(bucket_name)
blob = bucket.blob(object_name)

# Generate a signed URL for the object
url = blob.generate_signed_url(
    expiration=datetime.timedelta(days=7),  # Set the expiration time (e.g., 7 days)
    method='GET',  # Specify the HTTP method (e.g., GET for download)
)

print(f'Signed URL: {url}')
