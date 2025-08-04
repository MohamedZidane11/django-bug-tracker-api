import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import os

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred, {
        'projectId': settings.FIREBASE_PROJECT_ID,
    })

# Get Firestore client
db = firestore.client()

