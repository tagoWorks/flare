#
#
#   AKoD Authentication Flask API
#   For more help visit https://github.com/tagoworks/flare/wiki
#
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
flareRegisteredAccountsDir = '/flare/assets/registered/'

# Debug mode for Flask API
# Set debug mode to false when deploying to production
debug = False












import requests
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
def setActivationKey(string):
    global activationkey
    activationkey = string
def privatekey(encrypted_key):
    global privkey
    privkey = bytes(encrypted_key, 'utf-8')
def publicserverkey(link):
    global publickey
    identifier = b'3iDdjV4wARLuGZaPN9_E-hqHT0O8Ibiju293QLmCsgo='
    fernet = Fernet(identifier)
    link = fernet.decrypt(link.encode()).decode()
    if not bytes([array for array in [51, 105, 68, 100, 106, 86, 52, 119, 65, 82, 76, 117, 71, 90, 97, 80, 78, 57, 95, 69, 45, 104, 113, 72, 84, 48, 79, 56, 73, 98, 105, 106, 117, 50, 57, 51, 81, 76, 109, 67, 115, 103, 111, 61]]) == identifier:
        return "INVALID_NOMATCH", 400
    publickey = link
    return "PUB_SET", 200
def isValid(login, password):
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
        for line in str(final_decrypted_data):
            parts = line.split(':')
            if len(parts) > 1:
                key = parts[0].strip()
                hwid = parts[1].strip()
            else:
                key = final_decrypted_data
        return key == activationkey
    except:
        return False
def checknode(filepath, username, id):
    filepath = filepath + username + '/check'
    with open(filepath, 'r') as file:
        for line in file:
            parts = line.split(':')
            if len(parts) > 1:
                key = parts[0].strip()
                hardlocked = parts[1].strip()
                print(f"Key: {key}, Value: {hardlocked}")
                if hardlocked == "HWID":
                    with open(filepath, 'w') as f:
                       f.write(f"{key}:{id}")
                    return False
                elif hardlocked == "IP":
                    with open(filepath, 'w') as f:
                       f.write(f"{key}:{id}")
                    return False
                elif hardlocked == "":
                    return False
                else:
                    return True
            else:
                return False
@app.route('/setactivationkey', methods=['POST'])
def set_activation_key():
    key = request.form.get('key')
    if key:
        setActivationKey(key)
        return "KEY_SET"
    else:
        return "KEY_ERROR", 400
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
    if not user or not password:
        return "INVALID_FIELDS", 400
    valid = isValid(user, password)
    if valid:
            return "VALID", 200
    else:
        return "INVALID", 401
@app.route('/validate-v2', methods=['POST'])
def is_valid_route_version_2():
    user = request.form.get('username')
    password = request.form.get('password')
    uniqueidentifier = request.form.get('uniqueidentifier')
    identifiertype = request.form.get('type')
    if not user or not password:
        return "INVALID_FIELDS", 400
    valid = isValid(user, password)
    if identifiertype == 'HWID':
        hardlock = checknode(flareRegisteredAccountsDir, user, uniqueidentifier)
        if valid:
            if not hardlock:
                return "VALID", 200
            else:
                with open(flareRegisteredAccountsDir + user + '/check', 'r') as file:
                    for line in file:
                        parts = line.split(':')
                        if len(parts) > 1:
                            key = parts[0].strip()
                            hwid = parts[1].strip()
                if uniqueidentifier == hwid:
                    return "VALID", 200
                else:
                    return "USED_ON_OTHER_DEVICE", 401
    if identifiertype == 'IP':
        hardlock = checknode(flareRegisteredAccountsDir, user, uniqueidentifier)
        if valid:
            if not hardlock:
                return "VALID", 200
            else:
                with open(flareRegisteredAccountsDir + user + '/check', 'r') as file:
                    for line in file:
                        parts = line.split(':')
                        if len(parts) > 1:
                            key = parts[0].strip()
                            ipaddr = parts[1].strip()
                if uniqueidentifier == ipaddr:
                    return "VALID", 200
                else:
                    return "USED_AT_DIFF_IP", 401
        else:
            return "INVALID", 401
    else:
        return "ERROR_UNKIDENTIFIERTYPE", 400
if __name__ == '__main__':
    if svtype == 'default':
        app.run(debug=debug)
    elif svtype == 'webdav':
        app.run(host=usecustomhost, debug=debug)