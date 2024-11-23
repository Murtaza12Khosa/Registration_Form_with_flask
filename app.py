from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re  # Import the 're' module for regular expressions

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'

# Function to initialize the database and create the users table if it doesn't exist
def initialize_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phonenumber TEXT NOT NULL,
            Age INTEGER,
            Address TEXT,
            password TEXT NOT NULL,
            Confirmpassword TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to check if a user exists
def user_exists(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result

# Function to add a new user
def add_user(Full_name, email, phonenumber, Age, Address, password, Confirmpassword):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (Full_name, email, phonenumber, Age, Address, password, Confirmpassword) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (Full_name, email, phonenumber, Age, Address, password, Confirmpassword)
    )
    conn.commit()
    conn.close()

# Function to validate email format
def is_valid_email(email):
    # Regular expression for basic email format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Function to validate phone number (must be exactly 11 digits)
def is_valid_phone_number(phonenumber):
    # Check if the phone number has exactly 11 digits and consists only of digits
    return len(phonenumber) == 11 and phonenumber.isdigit()

# Route for registration
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get user details from the form
        Full_name = request.form['Full_name']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        Age = request.form['Age']
        Address = request.form['Address']
        password = request.form['password']
        Confirmpassword = request.form['Confirmpassword']

        # Validate email format
        if not is_valid_email(email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for('home'))

        # Validate phone number (must be exactly 11 digits)
        if not is_valid_phone_number(phonenumber):
            flash("Phone number must be exactly 11 digits.", "danger")
            return redirect(url_for('home'))

        # Check if passwords match
        if password != Confirmpassword:
            flash("Passwords do not match. Please try again.", "danger")
            return redirect(url_for('home'))

        # Check if user already exists
        if user_exists(email):
            flash("You are already registered. Please log in.", "warning")
            return redirect(url_for('login'))

        # Add user to the database
        add_user(Full_name, email, phonenumber, Age, Address, password, Confirmpassword)
        flash("You have successfully registered!", "success")
        return redirect(url_for('login'))

    return render_template('registration.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if user exists and get user data (ID and password)
        user = user_exists(email)
        
        if user:
            stored_password = user[1]  # user[1] is the password field from the database
            
            if stored_password == password:
                flash("Login successful!", "success")
                return redirect(url_for('home'))  # Redirect to the homepage or dashboard
            else:
                flash("Invalid password. Please try again.", "danger")
        else:
            flash("Email not registered. Please register first.", "danger")

    return render_template('login.html')

if __name__ == "__main__":
    initialize_database()  # Initialize the database before starting the app
    app.run(debug=True)
