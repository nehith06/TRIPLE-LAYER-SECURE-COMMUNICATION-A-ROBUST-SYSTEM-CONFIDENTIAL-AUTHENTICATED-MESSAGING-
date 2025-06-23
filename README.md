
----------------------------------------------------------------------------------------------------------------

# TRIPLE-LAYER-SECURE-COMMUNICATION-A-ROBUST-SYSTEM-CONFIDENTIAL-AUTHENTICATED-MESSAGING-
A secure messaging system using AES-256 encryption, LSB steganography, and fingerprint authenticatin. Messages are hidden in images, sent via ESP32, and accessed only with verified biometric input. Integrated with Firebase and Google Drive for real-time, secure, and authenticated communication
<details>
  <summary><b>TRANSMITTER'S MESSAGE</b></summary>
<br>
  
  **Transmitter-Side Process**

- The transmitter module is responsible for initiating secure message communication by handling encryption, steganography, cloud integration, and transmission signaling.

- The user inputs a plaintext message using a Python-based interface executed on a PC or laptop.

- The message is encrypted using the AES-256 encryption algorithm, operating in CBC (Cipher Block Chaining) mode with a randomly generated Initialization Vector (IV).

- AES-256 ensures that the message is transformed into secure ciphertext, providing strong protection against brute-force and cryptographic attacks.

- The ciphertext is embedded into an image using Least Significant Bit (LSB) steganography, which subtly modifies pixel values to conceal data without affecting image quality.

- The resulting stego-image, containing the encrypted message, is uploaded to Google Drive using the Google Drive API.

- Upon upload, a unique file ID is generated to represent the stored stego-image on the cloud.

- This file ID, along with the AES encryption key, is stored securely in Firebase Realtime Database for synchronization and controlled access.

- Firebase also manages a `start` control flag which is used to signal the receiver when the transmission setup is complete.

- The ESP32 microcontroller maintains a persistent connection with Firebase to monitor the message state and coordinate communication.

- After all necessary data is stored and the stego-image is uploaded, the transmitter sets the `start` flag in Firebase to notify the receiver that the message is ready.

- This transmitter-side workflow ensures a layered approach to message confidentiality, combining encryption, steganography, and biometric-controlled access signaling.

![Image](https://github.com/user-attachments/assets/505610b9-f957-4bf1-b44f-b7e71dad2db3)

</details>


----------------------------------------------------------------------------------------------------------------

<details>
<summary><b>MESSAGE ENCRYPTION & EMBEDDING</b></summary>
<br>
  
**Message embedding in image and ID stored in firebase**

This phase serves as the secure, cloud-based coordination layer that bridges the transmitter and receiver modules. It ensures that encrypted data, decryption credentials, and access signals are reliably synchronized using **Firebase Realtime Database**, **Google Drive**, and the **ESP32 microcontroller**.

- After the transmitter generates the stego-image by embedding the AES-256 encrypted message into an image, it uploads this file to **Google Drive** using the Google Drive API.

- Upon successful upload, **Google Drive returns a unique file ID** which serves as a secure reference to the hidden message.

- The **file ID** and the corresponding **AES-256 encryption key** are then securely written into **Firebase Realtime Database** by the transmitter.

- Along with these, a **status control flag** (`start`) is also updated in Firebase. This flag acts as a signal to inform the receiver that the encrypted payload is now ready for retrieval.

- On the receiver side, the **ESP32 microcontroller** continuously polls Firebase, checking for changes in the `start` flag.

- Once the `start` flag is detected as set (`start = 1`), the ESP32 retrieves the **file ID** and **AES key** from Firebase in real-time.

- These credentials are used to **download the stego-image from Google Drive**, effectively retrieving the encrypted message for the next stage of biometric authentication and decryption.

- This cloud-mediated handoff approach separates encrypted content (Google Drive) from key material and control signals (Firebase), reducing risk and increasing security.

- The use of **Google Drive** for secure image storage, **Firebase** for key signaling, and **ESP32** for secure polling and communication ensures a **modular, decoupled, and authenticated message handoff pipeline**.

**Image updating in google drive**

![Image](https://github.com/user-attachments/assets/8bedaf8b-d05b-4462-ab2c-adbae24f1649)

**Image where message is getting embedded**

![Image](https://github.com/user-attachments/assets/40374e1a-2aee-47b0-9168-5aac1bb3a954)

**Fingerprint data getting updated in firebase**

![Image](https://github.com/user-attachments/assets/71140c57-4d7f-4c0f-8158-93b65e7e1ec1)

</details>


----------------------------------------------------------------------------------------------------------------

<details>

<summary><b>RECIEVER'S SIDE</b></summary>
<br>

**Receiver-Side Authentication and Decryption Process**

The receiver module finalizes the secure communication pipeline by validating user identity through fingerprint authentication, retrieving the encrypted data, and performing message decryption. This stage is critical for enforcing strict access control, ensuring that only authorized users can view the original message.

- The receiver continuously monitors the `start` flag in **Firebase Realtime Database** via the **ESP32 microcontroller**, which signals when an encrypted message is ready.

- Once `start = 1` is detected, the ESP32 retrieves the **AES-256 key** and **Google Drive file ID** from Firebase to prepare for data decryption.

- The stego-image is then downloaded from **Google Drive** using the file ID retrieved from Firebase.

- The system prompts the user to place their finger on the **fingerprint sensor** connected to the ESP32.

- The fingerprint sensor captures the fingerprint data and transmits it to the ESP32, which in turn compares it against the **pre-registered fingerprint template stored in Firebase**.

- If the fingerprint **does not match**, the system halts the process and denies access to the encrypted message.

- If the fingerprint **successfully matches**, the ESP32 updates the fingerprint authentication flag in Firebase (e.g., `auth = 1`), indicating a verified user.

- The ESP32 then extracts the **encrypted ciphertext** hidden within the image using **LSB (Least Significant Bit) decoding**.

- The extracted ciphertext is decrypted using the **AES-256 key**, converting it back into the original plaintext message.

- The final decrypted message is then displayed securely to the verified user, typically through an **OLED screen** or system terminal connected to the ESP32.

- This process ensures that only an authenticated fingerprint can unlock the message, effectively preventing unauthorized decryption.

**RECIEVER'S SIDE MESSAGE DECRYPTION**
![Image](https://github.com/user-attachments/assets/cc158e98-68fb-43d0-86d7-beb0dcca4ea0)

</details>

