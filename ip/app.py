from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/prawn"
app.secret_key = os.getenv("SECRET_KEY", "your_default_secret_key")

mongo = PyMongo(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            message = "Passwords do not match!"
        elif mongo.db.login.find_one({"username": username}):
            message = "Username already exists!"
        elif mongo.db.login.find_one({"email": email}):
            message = "Email already exists!"
        else:
            hashed_password = generate_password_hash(password)
            mongo.db.login.insert_one({
                "username": username,
                "email": email,
                "password": hashed_password
            })
            message = "Registration successful! Please log in."
        
        return render_template('register.html', message=message)

    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = mongo.db.login.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            return redirect(url_for('search'))
        else:
            message = "Invalid email or password"
    
    return render_template('login.html', message=message)

@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('search-parking.html')

@app.route('/marina', methods=['GET', 'POST'])
def marina():
    if request.method == 'POST':
        slot = request.form.get('slot')
        # Debugging output to confirm slot selection
        print(f"Selected slot: {slot}")
        return redirect(url_for('confirm_payment', slot=slot))
    return render_template('marina-beach-parking.html')

@app.route('/confirm-payment', methods=['GET'])
def confirm_payment():
    slot = request.args.get('slot')
    if not slot:
        return "Error: Slot not specified", 400
    return render_template('confirm-payment.html', slot=slot)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
