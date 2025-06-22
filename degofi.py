import os
import base64
import re
import io
import json
import pyrebase
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from PIL import Image
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import time  # Added for polling Firebase

# 🔥 Firebase Configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyC5Q-66lWOj5kZCl1q7KvYD9ZO9pecFHkw",
    "authDomain": "test-d3894.firebaseapp.com",
    "databaseURL": "https://test-d3894-default-rtdb.firebaseio.com",
    "storageBucket": "test-d3894.firebasestorage.app",
    "messagingSenderId": "154625590550",
    "appId": "1:154625590550:web:76b15b53cdcc1cac80fc37"
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
db = firebase.database()

# 🔍 Wait for Firebase 'start' to be 1
def wait_for_start():
    print("⏳ Waiting for 'start' to be 1 in Firebase...")
    while True:
        data = db.child("Uploaded_Images").get().val()
        start_value = data["start"]
        print(start_value)
        if start_value == "1":
            print("✅ 'start' is now 1! Beginning decryption process...")
            break
        time.sleep(5)  # Check every 5 seconds to avoid excessive API calls
def store_file_id_in_firebase(file_id):
    data = {"file_id": file_id}
    db.child("Uploaded_Images").update({"data": file_id})
    print("✅ File ID stored in Firebase successfully!")
    
def store_file_id_in_firebase2(file_id):
    data = {"file_id": file_id}
    db.child("Uploaded_Images").update({"start": file_id})
    print("✅ File ID stored in Firebase successfully!")
# 🔍 Fetch File ID & AES Key from Firebase
def get_firebase_data():
    try:
        data = db.child("Uploaded_Images").get().val()
        if data and "file_id" in data and "aes_key" in data:
            return data["file_id"], data["aes_key"]
        else:
            print("❌ Firebase Error: Missing 'file_id' or 'aes_key'.")
            return None, None
    except Exception as e:
        print(f"❌ Firebase Error: {e}")
        return None, None

# 🔐 Google Drive API Configuration
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
DOWNLOADED_IMAGE = "downloaded_encoded_image.png"

# 🔑 Authenticate Google Drive API
def authenticate_drive():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

# 📥 Download Image from Google Drive
def download_file_from_drive(file_id, output_path):
    creds = authenticate_drive()
    service = build('drive', 'v3', credentials=creds)

    try:
        request = service.files().get_media(fileId=file_id)
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloading... {int(status.progress() * 100)}% complete")

        with open(output_path, "wb") as f:
            f.write(file_io.getvalue())

        print(f"✅ File downloaded successfully: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Google Drive Error: {e}")
        return False

# 🔑 AES Decryption
def decrypt_text_aes(encrypted_text, key):
    key = str(key).ljust(32, ' ')[:32].encode()  # Ensure 32-byte key
    try:
        encrypted_data = base64.b64decode(encrypted_text)
    except Exception:
        print("❌ Error: Extracted text is not valid Base64. Possible extraction issue.")
        return None

    iv, ciphertext = encrypted_data[:16], encrypted_data[16:]

    try:
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_text = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        pad = decrypted_text[-1]
        return decrypted_text[:-pad].decode()
    except Exception as e:
        print(f"❌ AES Decryption Error: {e}")
        return None

# 🖼️ Extract Hidden Text via LSB Steganography
def decode_text_from_image(image_path):
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"❌ Image Error: {e}")
        return None

    pixels = list(img.getdata())
    binary_text = ""

    for pixel in pixels:
        for i in range(3):  # Extract from RGB channels
            binary_text += str(pixel[i] & 1)

    # Convert binary to text
    chars = [binary_text[i:i+8] for i in range(0, len(binary_text), 8)]
    extracted_text = ''.join(chr(int(char, 2)) for char in chars)

    # Stop extraction at a special marker (e.g., "#####")
    extracted_text = extracted_text.split("#####")[0]

    # Ensure valid Base64 format
    match = re.search(r"[A-Za-z0-9+/=]+", extracted_text)
    return match.group(0) if match else None

if __name__ == "__main__":
    # 🔍 Step 1: Wait for Firebase 'start' to be 1
    wait_for_start()

    # 🔍 Step 2: Get File ID & AES Key from Firebase
    file_id, aes_key = get_firebase_data()

    if not file_id or not aes_key:
        print("❌ Failed to retrieve data from Firebase.")
        exit()

    print(f"🔍 Retrieved File ID: {file_id}")
    print(f"🔍 Retrieved AES Key: {aes_key}")

    # 📥 Step 3: Download Image from Google Drive
    if not download_file_from_drive(file_id, DOWNLOADED_IMAGE):
        exit()  # Stop if download fails

    # 🔍 Step 4: Extract Hidden Encrypted Text from Image
    extracted_text = decode_text_from_image(DOWNLOADED_IMAGE)

    if extracted_text:
        print(f"🔍 Extracted Encrypted Text: {extracted_text}")

        # 🔓 Step 5: Decrypt Extracted Text
        decrypted_text = decrypt_text_aes(extracted_text, aes_key)

        if decrypted_text:
            print(f"✅ Decrypted Text: {decrypted_text}")
            store_file_id_in_firebase(decrypted_text)
            time.sleep(1)
            store_file_id_in_firebase2("2")
        else:
            store_file_id_in_firebase("Decryption failed")
            print("❌ Decryption failed. Check your AES key or image.")
            time.sleep(1)
            store_file_id_in_firebase2("2")
    else:
        print("❌ No valid encrypted text found in the image.")
