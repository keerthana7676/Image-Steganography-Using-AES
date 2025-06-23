# Secure Image Steganography with AES Encryption

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![AES](https://img.shields.io/badge/AES-256-bit%20encryption-blue)
![Steganography](https://img.shields.io/badge/steganography-LSB%20embedding-green)

A secure web application that hides encrypted messages within images using AES-256 encryption and LSB steganography techniques.

## Features

- 🔒 **Military-grade encryption** using AES-256 in CBC mode
- 🖼️ **Image steganography** with LSB (Least Significant Bit) embedding
- 🔑 **Password protection** for all hidden messages
- 📊 **Usage statistics** tracking
- 🎨 **Image preview** before processing
- 📱 **Responsive design** works on all devices
- ✅ **Input validation** for files and messages

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/secure-steganography.git
   cd secure-steganography
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
3. **Create uploads folder**:
   ```bash
   mkdir -p static/uploads
4. **Run the application**:
   ```bash
   python main.py
5. **Access in your browser**:
   ```bash
   http://localhost:5001

## Usage
**Hiding a Message**
```
1. Upload an image (PNG, JPG, JPEG)
2. Enter your secret message
3. Set a strong password
4. Click "Hide Message"
5. Download the image with your hidden message
```
**Revealing a Message**
```
1. Upload an image with a hidden message
2. Enter the password used during encoding
3. Click "Reveal Message"
4. View your decrypted message
```
## Technical Details
**Encryption Process**
```
1. Password converted to 256-bit key using SHA-256
2. Random IV generated for each encryption
3. Message encrypted using AES-CBC mode
4. Encrypted data encoded in base64
```
**Steganography Process**
```
1. Encrypted message converted to binary
2. Binary data embedded in LSB of image pixels
3. End marker (1111111111111110) added
4. Image saved with hidden data
```
## Project Structure
```
secure-steganography/
├── main.py                # Main application logic
├── requirements.txt       # Dependencies
├── static/
│   ├── styles.css         # Styling
│   └── uploads/           # Temporary image storage
└── templates/
    └── index.html         # Web interface
```
## Screenshots
**Main application interface**
![image](https://github.com/user-attachments/assets/2646d13a-56e0-4ebd-ad1a-748ccf4bce5b)
**Message encoding process**
![image](https://github.com/user-attachments/assets/e6230f1d-d642-49f6-8aab-81b847401beb)
**Message decoding process**
![image](https://github.com/user-attachments/assets/62f895be-57aa-4ee4-b47a-b4b1c2d705c8)


