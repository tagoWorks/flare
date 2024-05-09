#
#
#   AKoD Authentication Flask API
#   For more help visit https://github.com/tagoworks/flare/wiki
#   To view all the return codes visit https://github.com/tagoWorks/flare/wiki/API-Return-Codes
#


# Change the custom location of the database on the webserver
# Only the name of the directory is needed, no slashes
customloco = 'none'


# Database service type. Usually only change if your not using Netlify
# Since you're on Ubuntu or Linux and using Apache, set this to 'webdav'
svtype = 'webdav'


# Change the host IP of the Flask API when using webdav
# Recommended to not change this unless you know what you are doing
usecustomhost = '0.0.0.0'


# Database directory for the API to read and write to
# Mostly used if you are node locking licenses
flareRegisteredAccountsDir = '../assets/registered/'


# Debug mode for Flask API
# Set debug mode to false when deploying to production
debug = False












import requests, os, shutil, datetime
from flask import Flask, request
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
app = Flask(__name__)
key = b''
publickey = ''
activationkey = ''

def log_message(message):
    logtime = datetime.datetime.now().strftime('%H:%M:%S')
    with open('flare.log', 'a') as f:
        f.write(f"[AUTH-API-{logtime}] {message}\n")
if not os.path.exists('flare.log'):
    with open('flare.log', 'w') as f:
        f.write('')
        f.close()
def setActivationKey(string):
    global activationkey
    activationkey = string
def privatekey(encrypted_key):
    global privkey
    privkey = bytes(encrypted_key, 'utf-8')
def publicserverkey(link):
    global publickey
    try:
        identifier = b'3iDdjV4wARLuGZaPN9_E-hqHT0O8Ibiju293QLmCsgo='
        fernet = Fernet(identifier)
        link = fernet.decrypt(link.encode()).decode()
        if not bytes([array for array in [51, 105, 68, 100, 106, 86, 52, 119, 65, 82, 76, 117, 71, 90, 97, 80, 78, 57, 95, 69, 45, 104, 113, 72, 84, 48, 79, 56, 73, 98, 105, 106, 117, 50, 57, 51, 81, 76, 109, 67, 115, 103, 111, 61]]) == identifier:
            return "INVALID_NOMATCH", 400
        publickey = link
        if publickey == '/':
            return "NO_LINK_INPUT", 400
        else:
            return "PUB_SET", 200
    except:
        return "INVALID", 400
def isValid(login, password):
    global publickey, activationkey, privkey
    log_message(f"Attempting to validate {login} (V1)")
    if svtype == 'default':
        if customloco == 'none':
            url = publickey + login + '/check'
        else:
            url = publickey + '/' + customloco + '/' + login + '/check'
        response = requests.get(url)
    elif svtype == 'webdav':
        if customloco == 'none':
            url = publickey + 'accs/' + login + '/check'
        else:
            url = publickey + customloco + '/' + login + '/check'
        response = requests.post(url)
    if response.status_code == 404:
        return False
    try:
        encrypted_data = response.content
        iv = b'JMWUGHTG78TH78G1'
        final_encrypted_data = encrypted_data[len(iv):]
        password = password.encode()
        salt = b'352384758902754328957328905734895278954789'
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=100000,backend=default_backend())
        password_key = kdf.derive(password)
        cipher_password = Cipher(algorithms.AES(password_key), modes.CFB(iv), backend=default_backend())
        decryptor_password = cipher_password.decryptor()
        decrypted_data = decryptor_password.update(final_encrypted_data) + decryptor_password.finalize()
        cipher = Cipher(algorithms.AES(privkey), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        final_decrypted_data = decryptor.update(decrypted_data) + decryptor.finalize()
        final_decrypted_data = final_decrypted_data.decode()
        print(final_decrypted_data)
        log_message(f"{login} checked (V1)")
        return final_decrypted_data == activationkey
    except:
        return False
    
def isValidV2(login, password, id):
    global publickey, activationkey, privkey
    if svtype == 'default':
        if customloco == 'none':
            url = publickey + login + '/check'
        else:
            url = publickey + '/' + customloco + '/' + login + '/check'
        response = requests.get(url)
    elif svtype == 'webdav':
        if customloco == 'none':
            url = publickey + 'accs/' + login + '/check'
        else:
            url = publickey + customloco + '/' + login + '/check'
        response = requests.post(url)
    if response.status_code == 404:
        print ("NOT FOUND: " + url + " (MOST LIKELY NOT AN ACCOUNT)")
        return False
    try:
        log_message(f"Attempting to validate {login} (V2)")
        encrypted_data = response.content
        iv = b'JMWUGHTG78TH78G1'
        final_encrypted_data = encrypted_data[len(iv):]
        password = password.encode()
        salt = b'352384758902754328957328905734895278954789'
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=100000,backend=default_backend())
        password_key = kdf.derive(password)
        cipher_password = Cipher(algorithms.AES(password_key), modes.CFB(iv), backend=default_backend())
        decryptor_password = cipher_password.decryptor()
        decrypted_data = decryptor_password.update(final_encrypted_data) + decryptor_password.finalize()
        cipher = Cipher(algorithms.AES(privkey), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        final_decrypted_data = decryptor.update(decrypted_data) + decryptor.finalize()
        final_decrypted_data = final_decrypted_data.decode()
        parts = final_decrypted_data.partition(":")
        if len(parts) > 1:
            key = parts[0].strip()
            hardlocked = parts[2].strip()
            if key == activationkey:
                if hardlocked == "HWID" or hardlocked == "IP":
                    log_message(f"Key has a hardlock: {hardlocked}")
                    print(f"Key: {key}, Value: {hardlocked}")
                    with open(flareRegisteredAccountsDir + login + '/check', 'w') as f:
                        f.write(f"{key}:{id}")
                        f.close()
                    log_message(f"Locked licenses key {key} with unique identifier: {id}")
                    encrypt_file_pass(flareRegisteredAccountsDir + login + '/check')
                    log_message(f"{login} checked (V2)")
                    return "LOCKED"
                else:
                    if hardlocked == id:
                        print (f"STATIC: {hardlocked} INCOMING: {id}")
                        log_message(f"STATIC: {hardlocked} === INCOMING: {id}")
                        log_message(f"{login} checked (V2)")
                        return "FULLMATCH"
                    else:
                        print (f"STATIC: {hardlocked} INCOMING: {id}")
                        log_message(f"STATIC: {hardlocked} =/= INCOMING: {id}")
                        log_message(f"{login} checked (V2)")
                        return "MISMATCH"
            else:
                print (f"MATCH ERROR: Invalid license key!")
                log_message(f"KEY INVALID: {activationkey}")
                log_message(f"{login} checked (V2)")
                return "INVALIDKEY"
        else:
            print (f"NO CHARACTERS TO PARTITION MAYBE USE V1?")
            log_message(f"NO CHARACTERS TO PARTITION MAYBE USE V1?")
            log_message(f"{login} checked (V2)")
            return "INVALIDKEY"
    except UnicodeDecodeError as e:
        print (f"UNICODE ERROR: {e} (MOST LIKELY INVALID CREDENTIALS)")
        return "INVALIDKEY"
    except Exception as e:
        print (f"UNKNOWN ERROR: {e}")
        log_message(f"[!] Exception: {e}")
        return "INVALIDKEY"

def encrypt_file_pass(file_path):
    global privkey, password
    with open(file_path, 'rb') as f:
        data = f.read()
    iv = b'JMWUGHTG78TH78G1'
    username = os.path.dirname(file_path).split('/')[-1]
    password_file_path = os.path.join(os.path.dirname(file_path), 'password.txt')
    with open(password_file_path, 'r') as password_file:
        password = password_file.read().strip().encode()
    salt = b'352384758902754328957328905734895278954789'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    password_key = kdf.derive(password)
    cipher = Cipher(algorithms.AES(privkey), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    cipher_password = Cipher(algorithms.AES(password_key), modes.CFB(iv), backend=default_backend())
    encryptor_password = cipher_password.encryptor()
    final_encrypted_data = encryptor_password.update(encrypted_data) + encryptor_password.finalize()
    final_encrypted_data = iv + final_encrypted_data
    os.chdir('/')
    if customloco == 'none':
        path = './var/www/accs/' + username
        print (path)
        shutil.rmtree(path)
        os.mkdir('./var/www/accs/' + username)
    else:
        path = './var/www/' + customloco + '/' + username
        shutil.rmtree(path)
        os.mkdir('./var/www/' + customloco + '/' + username)
    with open(path + '/check', 'wb') as f:
        f.write(final_encrypted_data)
        f.close()

@app.route('/privatekey', methods=['POST'])
def set_private_key():
    key = request.form.get('key')
    if key:
        privatekey(key)
        return "PRIV_SET"
    else:
        return "PRIV_ERROR", 400
@app.route('/publickey', methods=['POST'])
def set_public_key():
    link = request.form.get('key')
    if link:
        response, status_code = publicserverkey(link)
        return response, status_code
    else:
        return "PUB-ERROR", 400
@app.route('/validate', methods=['POST'])
def is_valid_route():
    user = request.form.get('username')
    password = request.form.get('password')
    activationkey = request.form.get('key')
    if not user or not password or not activationkey:
        return "INVALID_FIELDS", 400
    setActivationKey(activationkey)
    valid = isValid(user, password)
    if valid:
            return "VALID", 200
    else:
        return "INVALID", 401
@app.route('/validate-v2', methods=['POST'])
def is_valid_route_version_2():
    user = request.form.get('username')
    password = request.form.get('password')
    activationkey = request.form.get('key')
    uniqueidentifier = request.form.get('uniqueidentifier')
    if not user or not password or not activationkey:
        if not uniqueidentifier:
            return "NO_IDENTIFIER_USE_V1", 400
        else:
            return "INVALID_FIELDS", 400
    setActivationKey(activationkey)
    valid = isValidV2(user, password, uniqueidentifier)
    if valid == 'FULLMATCH':
            return "VALID", 200
    elif valid == 'MISMATCH':
        return "USED_ON_OTHER_DEVICE", 401
    elif valid == 'LOCKED':
        return "VALID_LOCKED", 200
    else:
        return "INVALID", 401
    

if __name__ == '__main__':
    try:
        with open('api.lck', 'wb') as f:
            f.write(os.urandom(16))
        if svtype == 'default':
            app.run(debug=debug)
        elif svtype == 'webdav':
            app.run(host=usecustomhost, debug=debug)
    finally:
        if os.path.exists('api.lck'):
            os.remove('api.lck')