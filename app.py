from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
from config import DB_CONFIG, SECRET_KEY  # Import DB_CONFIG and SECRET_KEY from config.py

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Database connection using the values from DB_CONFIG
conn = pyodbc.connect(
    f"DRIVER={DB_CONFIG['DRIVER']};"
    f"SERVER={DB_CONFIG['SERVER']};"
    f"DATABASE={DB_CONFIG['DATABASE']};"
    f"UID={DB_CONFIG['UID']};"
    f"PWD={DB_CONFIG['PWD']};"
)

# Route for the form to add a student
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        first = request.form['first_name'].strip().capitalize()
        last = request.form['last_name'].strip().capitalize()
        roll = request.form['roll_number'].strip()
        gender = request.form.get('gender')

        # Basic validation
        if not first.isalpha() or not last.isalpha():
            flash('First and Last names must contain only letters.', 'error')
        elif not roll.isdigit():
            flash('Roll number must be numeric.', 'error')
        elif gender not in ['Male', 'Female']:
            flash('Please select a valid gender.', 'error')
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Student WHERE RollNumber = ?", (roll,))
            if cursor.fetchone():
                flash('Roll number already exists.', 'error')
            else:
                cursor.execute("INSERT INTO Student (FirstName, LastName, RollNumber, Gender) VALUES (?, ?, ?, ?)",
                               (first, last, roll, gender))
                conn.commit()
                flash('Student added successfully!', 'success')

    # Fetch the list of students from the database
    cursor = conn.cursor()
    cursor.execute("SELECT FirstName, LastName, RollNumber, Gender FROM Student")
    students = cursor.fetchall()

    return render_template('form.html', students=students)

# Route for displaying the student list
@app.route('/students')
def student_list():
    cursor = conn.cursor()
    cursor.execute("SELECT FirstName, LastName, RollNumber, Gender FROM Student")
    students = cursor.fetchall()
    return render_template('student_list.html', students=students)

# Route for deleting a student by roll number
@app.route('/delete_student/<roll_number>', methods=['GET'])
def delete_student(roll_number):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Student WHERE RollNumber = ?", (roll_number,))
    conn.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('student_list'))

if __name__ == '__main__':
    app.run(debug=True)
