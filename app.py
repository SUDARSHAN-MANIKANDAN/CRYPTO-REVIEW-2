from flask import Flask, render_template, request, redirect, url_for, session, flash
from blockchain import Blockchain
from crypto_utils import load_keys, verify_signature, sha256_file
import os,json
from functools import wraps

app = Flask(__name__)
app.secret_key = "super-secret-key"

chain = Blockchain()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# ---------------- Decorator ----------------
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

# ---------------- Home (Admin Add + Verify Public Form) ----------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------- Add Certificate (Admin Only) ----------------
@app.route('/add_certificate', methods=['POST'])
@login_required
def add_certificate():
    student = request.form['student']
    degree = request.form['degree']
    year = request.form['year']
    file = request.files['file']

    if not file:
        flash("No file uploaded")
        return redirect(url_for('index'))

    file_bytes = file.read()
    file_hash = sha256_file(file_bytes)

    student_data = {
        "student": student,
        "degree": degree,
        "year": year,
        "file_hash": file_hash
    }

    chain.add_certificate(student_data)
    flash("Certificate added and saved successfully!")
    return redirect(url_for('chain_view'))

# ---------------- View Blockchain ----------------
@app.route('/chain')
def chain_view():
    return render_template('chain.html', chain=chain.chain)

# ---------------- Verify Certificate (Public) ----------------
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    result = None
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            flash("No file uploaded")
            return redirect(request.url)
        file_bytes = file.read()
        file_hash = sha256_file(file_bytes)

        _, pubkey = load_keys()
        found = False
        for block in chain.chain:
            for tx in block['transactions']:
                if tx.get("file_hash") == file_hash:
                    cert_data = tx.copy()
                    signature = cert_data.pop("signature", "")
                    cert_string = json.dumps(cert_data, sort_keys=True)
                    if verify_signature(cert_string, signature, pubkey):
                        result = f"✅ Verified: {cert_data}"
                    else:
                        result = "⚠️ Record found but signature invalid!"
                    found = True
                    break
            if found: break
        if not found:
            result = "❌ No matching record found."

    return render_template('verify.html', result=result)

# ---------------- Run Flask ----------------
if __name__ == "__main__":
    app.run(debug=True)
