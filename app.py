from flask import Flask, request, render_template, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import re
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super_secret_key_123')  # Set SECRET_KEY on Render

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Hardcoded user for simplicity (change password in production)
users = {
    'admin': {
        'password': generate_password_hash('admin_password')  # Change this to a strong password
    }
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# Load exams dynamically from 'data/' directory
def load_exams():
    exams = {}
    data_dir = 'data'
    if not os.path.exists(data_dir):
        return exams
    
    for file_name in os.listdir(data_dir):
        if file_name.endswith('.xlsx'):
            exam_name = os.path.splitext(file_name)[0]  # Filename without .xlsx
            file_path = os.path.join(data_dir, file_name)
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
                df['ID'] = df['ID'].astype(str)  # Ensure ID is string
                df.set_index('ID', inplace=True)
                # Use Total directly as percentage (no multiplication)
                exams[exam_name] = df[['Name', 'Section A', 'Section B', 'Total']].to_dict(orient='index')
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
    return exams

# Validate student ID format (assuming 9-digit IDs)
def is_valid_student_id(student_id):
    return bool(re.match(r'^\d{9}$', student_id))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and check_password_hash(users[username]['password'], password):
            user = User(username)
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    exams = load_exams()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        
        # Validate input
        if not student_id:
            flash('Student ID is required!', 'error')
            return redirect(url_for('index'))
        if not is_valid_student_id(student_id):
            flash('Invalid Student ID format. Must be a 9-digit number.', 'error')
            return redirect(url_for('index'))

        # Collect results from all exams
        results = {}
        for exam_name, exam_data in exams.items():
            if student_id in exam_data:
                result = exam_data[student_id]
                if result['Total'] > 0.0:  # Skip if incomplete
                    results[exam_name] = {
                        'Section A': result['Section A'],
                        'Section B': result['Section B'],
                        'Total': result['Total'],
                        'Percentage': result['Total']  # Use Total directly as percentage
                    }
        
        if not results:
            flash('No results found for this Student ID.', 'error')
            return redirect(url_for('index'))

        return render_template('results.html', results=results)

    return render_template('index.html', is_authenticated=current_user.is_authenticated)

# Admin view to see all results
@app.route('/admin')
@login_required
def admin():
    exams = load_exams()
    return render_template('admin.html', exams=exams)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)