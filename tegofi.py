import os
import base64
import pyrebase
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from PIL import Image
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

# 🔹 Google Drive API Configuration
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = "1P6wS76-cVfGVoABWhURfAnxggphameJQ"  # Replace with your Google Drive Folder ID

# 🔹 Firebase Configuration (Replace with your Firebase details)



firebase_config = {
    "apiKey": "AIzaSyAc0FPITa7Ps2Tk3TQHpFWJU9QRH9aInYk",
    "authDomain": "project-c5d30.firebaseapp.com",
    "databaseURL": "https://project-c5d30-default-rtdb.firebaseio.com",
    "storageBucket": "project-c5d30.firebasestorage.app"
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()  # Initialize Firebase Database

# 🔹 Authenticate Google Drive API
def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

# 🔹 Upload file to Google Drive
def upload_file_to_drive(file_path, file_name):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,
        'parents': [PARENT_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype='image/png')

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = file.get('id')
    print(f"✅ File uploaded successfully! File ID: {file_id}")
    return file_id  # Return the File ID

# 🔹 Store File ID in Firebase Database
def store_file_id_in_firebase(file_id):
    data = {"file_id": file_id}
    db.child("Uploaded_Images").update({"file_id": file_id})
    print("✅ File ID stored in Firebase successfully!")

# 🔹 AES Encryption
def encrypt_text_aes(text, key):
    key = key.ljust(32, ' ')[:32].encode()  # Ensure 32-byte key
    iv = os.urandom(16)  # Random IV (Initialization Vector)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad text to be multiple of 16 bytes
    padding = 16 - (len(text) % 16)
    text += chr(padding) * padding
    ciphertext = encryptor.update(text.encode()) + encryptor.finalize()

    return base64.b64encode(iv + ciphertext).decode()

# 🔹 LSB Steganography to hide text in an image
def encode_text_in_image(text, image_path, output_path):
    img = Image.open(image_path)
    img = img.convert("RGB")  # Ensure RGB mode
    binary_text = ''.join(format(ord(c), '08b') for c in text) + '1111111111111110'  # Add a stop sequence

    pixels = list(img.getdata())
    new_pixels = []
    binary_index = 0

    for pixel in pixels:
        if binary_index < len(binary_text):
            new_pixel = list(pixel)
            for i in range(3):  # Modify RGB channels
                if binary_index < len(binary_text):
                    new_pixel[i] = new_pixel[i] & ~1 | int(binary_text[binary_index])
                    binary_index += 1
            new_pixels.append(tuple(new_pixel))
        else:
            new_pixels.append(pixel)

    img.putdata(new_pixels)
    img.save(output_path)
    print(f"✅ Encrypted text saved in {output_path}")

# 🔹 Main Execution
if __name__ == "__main__":
    text = input("Enter text to encrypt: ")
    aes_key = input("Enter AES key (must be 32 chars or will be adjusted): ")
    encrypted_text = encrypt_text_aes(text, aes_key)

    sample_image = "sample.jpg"  # Provide an image path
    output_image = "encoded_image.png"

    # Step 1: Encode encrypted text into an image
    encode_text_in_image(encrypted_text, sample_image, output_image)

    # Step 2: Upload encoded image to Google Drive
    file_id = upload_file_to_drive(output_image, "Encoded_Image.png")

    # Step 3: Store File ID in Firebase Database
    store_file_id_in_firebase(file_id)
