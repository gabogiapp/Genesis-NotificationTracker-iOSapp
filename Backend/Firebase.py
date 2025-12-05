import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import firestore
import os
from typing import Any, List, Optional
from dataclasses import dataclass


@dataclass
class Student:
    """In-memory representation of a student document from Firestore.

    Fields map to commonly-used document keys. Values may be None when the
    corresponding field is missing in Firestore.
    """
    email: Optional[str]
    password: Optional[str]
    student_id: Optional[str]
    fcm_token: Optional[str]
    grades_length: Optional[List[int]]
    average_grades: Optional[List[str]]
    check: Optional[Any]


class Firebase:
    """Helper wrapper around Firebase Admin SDK operations used by the app.

    This class provides small convenience methods for reading commonly used
    fields from the `Students` collection and for sending notifications.

    Initialization uses `ServiceAccountKey.json` from the repository root. If
    the file is missing the class will attempt to initialize the SDK with
    default credentials (useful on CI or when running in Cloud environments).
    """

    # Initialize Firebase SDK once when module is loaded.
    try:
        cred_path = os.path.join(os.path.dirname(__file__), "ServiceAccountKey.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fall back to default credentials if present in environment
            firebase_admin.initialize_app()
    except Exception:
        # Initialization may already be done or fail in some environments; let calls fail later with a clear error
        pass

    @staticmethod
    def send_notif(device_token: str, title: str, body: str) -> None:
        """Send a push notification using Firebase Cloud Messaging.

        Args:
            device_token: The recipient device FCM token.
            title: Notification title.
            body: Notification body text.
        """
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body), token=device_token
        )
        response = messaging.send(message)
        print("Successfully sent message:", response)

    @staticmethod
    def _get_collection_field(field_name: str) -> List[Any]:
        """Return a list containing `field_name` from every document in `Students`.

        This helper removes the repeated boilerplate used by many getters.
        """
        db = firestore.client()
        collection_ref = db.collection("Students")
        docs = collection_ref.get()
        values: List[Any] = []
        for doc in docs:
            data = doc.to_dict() or {}
            values.append(data.get(field_name))
        return values

    # Public getters that use the common helper to reduce duplication.
    @staticmethod
    def get_emails() -> List[Any]:
        # Backwards-compatible: return raw field list
        return Firebase._get_collection_field("encrypted_email")

    @staticmethod
    def get_passwords() -> List[Any]:
        return Firebase._get_collection_field("encrypted password")

    @staticmethod
    def get_student_ids() -> List[Any]:
        return Firebase._get_collection_field("studentID")

    @staticmethod
    def get_old_assignment_grade_lengths() -> List[Any]:
        return Firebase._get_collection_field("grades length")

    @staticmethod
    def get_average_grades() -> List[Any]:
        return Firebase._get_collection_field("average grades")

    @staticmethod
    def get_tokens() -> List[Any]:
        return Firebase._get_collection_field("encrypted fcm token")

    @staticmethod
    def get_checks() -> List[Any]:
        return Firebase._get_collection_field("check")

    @staticmethod
    def get_students() -> List[Student]:
        """Return a list of `Student` dataclass instances built from the
        `Students` collection in Firestore.

        This centralizes the mapping from Firestore documents into a
        typed structure the rest of the code can consume.
        """
        db = firestore.client()
        collection_ref = db.collection("Students")
        docs = collection_ref.get()
        students: List[Student] = []
        for doc in docs:
            data = doc.to_dict() or {}
            students.append(
                Student(
                    email=data.get("encrypted_email"),
                    password=data.get("encrypted password"),
                    student_id=data.get("studentID"),
                    fcm_token=data.get("encrypted fcm token"),
                    grades_length=data.get("grades length"),
                    average_grades=data.get("average grades"),
                    check=data.get("check"),
                )
            )
        return students