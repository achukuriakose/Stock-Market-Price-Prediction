from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']
        users[email] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']
        if email in users and users[email] == password:
            session['user'] = email
            return redirect(url_for('predict'))
    return render_template('login.html')

@app.route('/predict')
def predict():
    if 'user' in session:
        return render_template('prediction.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
 
