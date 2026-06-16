import random
from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)

# Secret Key
app.secret_key = "fraud_detection_secret_key"

# =========================
# MySQL Database Connection
# =========================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Supriya_indrani@08",
    database="fraud_detection"
)

# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template('index.html')


# =========================
# REGISTER PAGE
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor(buffered=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            cursor.close()

            return """
            <h2 style='text-align:center;
            color:red;
            margin-top:50px;'>
            User Already Exists
            </h2>
            """

        account_number = "ACC" + str(random.randint(10000, 99999))
        print("Generated Account Number:", account_number)
        cursor.execute(
        """
        INSERT INTO users
        (name,email,password,account_number,balance)
        VALUES(%s,%s,%s,%s,%s)
        """,
        (
            name,
            email,
            password,
            account_number,
            100000
        )
    )
        db.commit()

        cursor.close()

        return redirect('/login')

    return render_template('register.html')


# =========================
# LOGIN PAGE
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor(buffered=True)

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email=%s AND password=%s
            """,
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()

        if user:

            session['user'] = email

            return redirect('/dashboard')

        else:

            return """
            <h2 style='text-align:center;
            color:red;
            margin-top:50px;'>
            Invalid Email or Password
            </h2>
            """

    return render_template('login.html')


# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email=%s
        """,
        (session['user'],)
    )

    user = cursor.fetchone()

    cursor.close()

    return render_template(
        'dashboard.html',
        user=user
    )


# =========================
# FRAUD DETECTION
# =========================

@app.route('/detect', methods=['POST'])
def detect():

    if 'user' not in session:
        return redirect('/login')

    amount = float(request.form['amount'])
    receiver_account = request.form['receiver_account']
    location = request.form['location']
    transaction_time = request.form['time']
    

    location_time = location + " | " + transaction_time
    transaction_id = "TXN" + str(random.randint(100000, 999999))

    # =========================
    # FRAUD RISK SCORING
    # =========================

    risk_score = 0

    if amount > 100000:
     risk_score += 40

    elif amount > 50000:
        risk_score += 20

    elif amount > 20000:
     risk_score += 10

    suspicious_locations = [
        "Russia",
        "Unknown",
        "Fraud City",
        "Dark Web"
    ]

    if location in suspicious_locations:
        risk_score += 30

    suspicious_times = [
        "2AM",
        "3AM",
        "4AM"
    ]

    if transaction_time.upper() in suspicious_times:
        risk_score += 20

    if risk_score >= 60:

        fraud_status = "Fraud"
        risk_color = "red"

    elif risk_score >= 30:

        fraud_status = "Suspicious"
        risk_color = "orange"

    else:

        fraud_status = "Safe"
        risk_color = "green"

    # =========================
    # SAVE TRANSACTION
    # =========================

    cursor = db.cursor(buffered=True)

    sql = """
    INSERT INTO transactions
    (transaction_id, amount, location_time, fraud_status, user_email)
    VALUES(%s, %s, %s, %s, %s)
    """

    values = (
        transaction_id,
        amount,
        location_time,
        fraud_status,
        session['user']
    )

    cursor.execute(sql, values)

    db.commit()

    cursor.close()

    # =========================
    # RESULT PAGE
    # =========================

    return f"""

    <!DOCTYPE html>
    <html>

    <head>

        <title>Fraud Detection Result</title>

        <style>

            body{{
                font-family:Arial;
                background:#eef4ff;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
            }}

            .box{{
                background:white;
                padding:40px;
                border-radius:20px;
                width:500px;
                text-align:center;
                box-shadow:0px 10px 25px rgba(0,0,0,0.15);
            }}

            h1{{
                color:#1e3a8a;
            }}

            h2{{
                color:{risk_color};
            }}

            a{{
                display:inline-block;
                margin-top:20px;
                padding:12px 25px;
                background:#2563eb;
                color:white;
                text-decoration:none;
                border-radius:10px;
            }}

        </style>

    </head>

    <body>

        <div class="box">

            <h1>Fraud Detection Result</h1>

            <p><strong>Transaction ID:</strong> {transaction_id}</p>

            <p><strong>Amount:</strong> ₹{amount}</p>

            <p><strong>Location & Time:</strong> {location_time}</p>

            <p><strong>Risk Score:</strong> {risk_score}%</p>

            <h2>{fraud_status}</h2>

            <a href="/dashboard">
                Back To Dashboard
            </a>

        </div>

    </body>

    </html>

    """


# =========================
# HISTORY PAGE
# =========================

@app.route('/history')
def history():

    if 'user' not in session:
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM transactions
        WHERE user_email=%s
        ORDER BY id DESC
        """,
        (session['user'],)
    )

    transactions = cursor.fetchall()

    cursor.close()

    return render_template(
        'history.html',
        transactions=transactions
    )


# =========================
# RUN SERVER
# =========================

if __name__ == '__main__':
    app.run(debug=True)