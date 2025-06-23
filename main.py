from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from PIL import Image
import io
import os
import base64
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.secret_key = 'your_secret_key_here'  # Needed for flash messages

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Counter for downloads
download_counter = 0

# AES Configuration
AES_KEY_SIZE = 32  # 256-bit key
AES_BLOCK_SIZE = 16  # 128-bit blocks


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_aes_key(password: str) -> bytes:
    """Generate AES key from password using SHA-256"""
    return hashlib.sha256(password.encode()).digest()


def encrypt_message(message: str, password: str) -> str:
    """Encrypt message using AES-CBC mode"""
    key = generate_aes_key(password)
    iv = get_random_bytes(AES_BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Pad the message and encrypt
    padded_message = pad(message.encode(), AES_BLOCK_SIZE)
    ciphertext = cipher.encrypt(padded_message)

    # Combine IV and ciphertext for storage
    encrypted_data = iv + ciphertext
    return base64.b64encode(encrypted_data).decode('utf-8')


def decrypt_message(encrypted_message: str, password: str) -> str:
    """Decrypt message using AES-CBC mode"""
    try:
        key = generate_aes_key(password)
        encrypted_data = base64.b64decode(encrypted_message)

        # Extract IV and ciphertext
        iv = encrypted_data[:AES_BLOCK_SIZE]
        ciphertext = encrypted_data[AES_BLOCK_SIZE:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext)
        return unpad(decrypted_padded, AES_BLOCK_SIZE).decode('utf-8')
    except Exception as e:
        raise ValueError("Decryption failed - wrong password or corrupted data")


@app.route('/')
def home():
    return render_template('index.html', counter=download_counter)


@app.route('/encode', methods=['POST'])
def encode():
    global download_counter

    # Check if image file was uploaded
    if 'image' not in request.files:
        flash('No image file selected!', 'error')
        return redirect(url_for('home'))

    image_file = request.files['image']
    message = request.form.get('message', '')
    password = request.form.get('password', '')

    # Validate inputs
    if not message:
        flash('Please enter a message to hide!', 'error')
        return redirect(url_for('home'))

    if not image_file or image_file.filename == '':
        flash('No image selected!', 'error')
        return redirect(url_for('home'))

    if not allowed_file(image_file.filename):
        flash('Only PNG, JPG, and JPEG files are allowed!', 'error')
        return redirect(url_for('home'))

    if not password:
        flash('Password is required for encryption!', 'error')
        return redirect(url_for('home'))

    try:
        # Secure filename and save temporarily
        filename = secure_filename(image_file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(temp_path)

        # Open the image
        img = Image.open(temp_path)

        # Encrypt the message
        encrypted_message = encrypt_message(message, password)

        # Convert encrypted message to binary
        binary_message = ''.join([format(ord(char), '08b') for char in encrypted_message])
        binary_message += '1111111111111110'  # End marker

        # Check if message fits
        if len(binary_message) > img.width * img.height * 3:
            flash('Message too long for this image! Try a shorter message or larger image.', 'error')
            os.remove(temp_path)
            return redirect(url_for('home'))

        # Hide message in image
        pixels = img.load()
        data_index = 0

        for i in range(img.width):
            for j in range(img.height):
                pixel = list(pixels[i, j])

                for color in range(3):  # R, G, B
                    if data_index < len(binary_message):
                        pixel[color] = pixel[color] & ~1 | int(binary_message[data_index])
                        data_index += 1

                pixels[i, j] = tuple(pixel)

        # Save and prepare for download
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Clean up
        os.remove(temp_path)
        download_counter += 1

        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='secret_message.png')

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('home'))


@app.route('/decode', methods=['POST'])
def decode():
    if 'image' not in request.files:
        flash('No image file selected!', 'error')
        return redirect(url_for('home'))

    image_file = request.files['image']
    password = request.form.get('password', '')

    if not image_file or image_file.filename == '':
        flash('No image selected!', 'error')
        return redirect(url_for('home'))

    if not password:
        flash('Password is required for decryption!', 'error')
        return redirect(url_for('home'))

    try:
        # Save temporarily
        filename = secure_filename(image_file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(temp_path)

        # Open image
        img = Image.open(temp_path)

        # Extract message
        binary_message = ''
        pixels = img.load()

        for i in range(img.width):
            for j in range(img.height):
                pixel = pixels[i, j]

                for color in range(3):  # R, G, B
                    binary_message += str(pixel[color] & 1)

        # Find end marker
        end_marker = '1111111111111110'
        if end_marker in binary_message:
            binary_message = binary_message[:binary_message.index(end_marker)]

        # Convert to text (this is the encrypted message)
        encrypted_message = ''
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i + 8]
            encrypted_message += chr(int(byte, 2))

        # Decrypt the message
        try:
            decrypted_message = decrypt_message(encrypted_message, password)
            flash(f'Success! Hidden message: {decrypted_message}', 'success')
        except ValueError as e:
            flash(str(e), 'error')

        os.remove(temp_path)
        return redirect(url_for('home'))

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('home'))


if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5001)