import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import json
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = None

        # Method 1: Try to load from JSON string (for Railway deployment)
        if hasattr(settings, 'FIREBASE_CREDENTIALS_JSON') and settings.FIREBASE_CREDENTIALS_JSON:
            try:
                logger.info("Loading Firebase credentials from JSON string")
                cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
                cred = credentials.Certificate(cred_dict)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing Firebase credentials JSON: {e}")
                raise

        # Method 2: Try to load from file path (for local development)
        elif (hasattr(settings, 'FIREBASE_CREDENTIALS_PATH') and
              settings.FIREBASE_CREDENTIALS_PATH and
              os.path.exists(settings.FIREBASE_CREDENTIALS_PATH)):
            logger.info("Loading Firebase credentials from file")
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)

        # Method 3: Try environment variables directly
        elif os.environ.get('FIREBASE_CREDENTIALS_JSON'):
            logger.info("Loading Firebase credentials from environment variable")
            cred_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS_JSON'))
            cred = credentials.Certificate(cred_dict)

        else:
            error_msg = (
                "No valid Firebase credentials found. Please set one of:\n"
                "- FIREBASE_CREDENTIALS_JSON (JSON string)\n"
                "- FIREBASE_CREDENTIALS_PATH (file path)\n"
                "- Ensure Firebase credentials are properly configured"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Initialize Firebase Admin SDK
        firebase_admin.initialize_app(cred, {
            'projectId': settings.FIREBASE_PROJECT_ID,
        })

        logger.info("Firebase Admin SDK initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise

# Get Firestore client
try:
    db = firestore.client()
    logger.info("Firestore client created successfully")
except Exception as e:
    logger.error(f"Failed to create Firestore client: {e}")
    raise