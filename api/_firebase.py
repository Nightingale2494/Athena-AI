import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os
import json

private_key = os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n")

def get_firebase_credentials():
    """Load Firebase credentials from environment variables."""
    if os.environ.get('FIREBASE_PROJECT_ID'):
        return credentials.Certificate({
            'type': os.environ.get('FIREBASE_TYPE', 'service_account'),
            'project_id': os.environ['FIREBASE_PROJECT_ID'],
            'private_key_id': os.environ['FIREBASE_PRIVATE_KEY_ID'],
            'private_key': os.environ['FIREBASE_PRIVATE_KEY'].replace('\\n', '\n'),
            'client_email': os.environ['FIREBASE_CLIENT_EMAIL'],
            'client_id': os.environ['FIREBASE_CLIENT_ID'],
            'auth_uri': os.environ.get('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
            'token_uri': os.environ.get('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
            'auth_provider_x509_cert_url': os.environ.get('FIREBASE_AUTH_PROVIDER_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
            'client_x509_cert_url': os.environ.get('FIREBASE_CLIENT_CERT_URL', ''),
        })
    raise ValueError("Firebase credentials not found in environment variables")

if not firebase_admin._apps:
    cred = get_firebase_credentials()
    storage_bucket = os.environ.get('FIREBASE_STORAGE_BUCKET', 'athena-fc81f.firebasestorage.app')
    firebase_admin.initialize_app(cred, {
        'storageBucket': storage_bucket
    })

db = firestore.client()
storage_bucket = storage.bucket()
