import firebase_admin
from firebase_admin import credentials, firestore

# Function to initialize Firebase and get Firestore client
def initialize_firebase(firebase_credentials_path):
    """
    Initializes Firebase Admin SDK and returns the Firestore client.
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials_path)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Function to get the document from Firestore
def get_document(collection_name, document_id, firebase_credentials_path):
    """
    Retrieves a document from Firestore. If the document exists, returns its data.
    If the document doesn't exist, returns None.

    :param collection_name: The Firestore collection where the document is stored
    :param document_id: The ID of the document to retrieve
    :param firebase_credentials_path: Path to the Firebase service account credentials JSON file
    :return: The document data if it exists, otherwise None
    """
    db = initialize_firebase(firebase_credentials_path)
    doc_ref = db.collection(collection_name).document(document_id)
    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()
    else:
        return None

# Function to add or update (upsert) the document in Firestore with modifications
def upsert_doc(collection_name, document_id, data, firebase_credentials_path):
    db = initialize_firebase(firebase_credentials_path)
    doc_ref = db.collection(collection_name).document(document_id)

    # Retrieve existing document data
    existing_data = get_document(collection_name, document_id, firebase_credentials_path)

    if existing_data:
        print(f"Document found: {existing_data}")
        for item, qty in data['items'].items():
            if item in existing_data['items']:
                existing_value = existing_data['items'][item]
                
                if isinstance(existing_value, dict):
                    # If existing value is a dict, we expect sub-items to also be present
                    for sub_item, sub_qty in qty.items():
                        if sub_item in existing_value:
                            existing_value[sub_item] += sub_qty  # Update nested quantity
                        else:
                            existing_value[sub_item] = sub_qty  # Add new sub-item
                else:
                    # If the existing value is not a dict, treat it as a direct quantity update
                    existing_data['items'][item] += qty
            else:
                existing_data['items'][item] = qty  # Add new item if it doesn't exist

        existing_data['name'] = data['name']  # Optionally update the name
        print(f"Updated document data: {existing_data}")
        doc_ref.set(existing_data, merge=True)
        print("Document updated successfully!")
    else:
        print("Document does not exist, creating new document.")
        doc_ref.set(data)
        print("Document created successfully!")


# Example usage:
if __name__ == "__main__":
    firebase_credentials_path = "path/to/serviceAccountKey"
    data = {
        'name': 'Kushal',
        'items': {
            '10mm DRILL': 5,
            '4.5mm x 9mm DRILL': 1
        }
    }

    # Add or update the document with modifications
    upsert_doc(collection_name='yourCollection', document_id='10101010', data=data, firebase_credentials_path=firebase_credentials_path)