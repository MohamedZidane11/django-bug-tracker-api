import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import json
import os

# Initialize Firebase
if not firebase_admin._apps:
    # Try to load from JSON string (for Render deployment)
    if settings.FIREBASE_CREDENTIALS_JSON:
        try:
            # Parse JSON string from environment variable
            cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
            cred = credentials.Certificate(cred_dict)
        except json.JSONDecodeError as e:
            print(f"Error parsing Firebase credentials JSON: {e}")
            raise
    # Fallback to file path (for local development)
    elif settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    else:
        raise ValueError(
            "No valid Firebase credentials found. Set either FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_PATH")

    firebase_admin.initialize_app(cred, {
        'projectId': settings.FIREBASE_PROJECT_ID,
    })

# Get Firestore client
db = firestore.client()