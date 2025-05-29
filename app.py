from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from config import db_config

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

# --- Admin Login ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

# --- Admin Dashboard ---
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', students=students)

# --- Add Student ---
@app.route('/admin/add_student', methods=['POST'])
def add_student():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    name = request.form['name']
    roll = request.form['roll']
    email = request.form['email']
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO students (name, roll, email) VALUES (%s, %s, %s)", (name, roll, email))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# --- Delete Student ---
@app.route('/admin/delete/<int:id>')
def delete_student(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# --- Edit Student Form ---
@app.route('/admin/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        email = request.form['email']
        cur.execute("UPDATE students SET name=%s, roll=%s, email=%s WHERE id=%s",
                    (name, roll, email, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        cur.execute("SELECT * FROM students WHERE id=%s", (id,))
        student = cur.fetchone()
        conn.close()
        return render_template('edit_student.html', student=student)

# --- Attendance Management Form ---
@app.route('/admin/attendance/<int:student_id>', methods=['GET', 'POST'])
def attendance(student_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        attendance_count = int(request.form['attendance'])
        total_classes = int(request.form['total_classes'])
        # Check if attendance record exists
        cur.execute("SELECT * FROM attendance WHERE student_id = %s", (student_id,))
        record = cur.fetchone()
        if record:
            cur.execute("UPDATE attendance SET attendance=%s, total_classes=%s WHERE student_id=%s",
                        (attendance_count, total_classes, student_id))
        else:
            cur.execute("INSERT INTO attendance (student_id, attendance, total_classes) VALUES (%s, %s, %s)",
                        (student_id, attendance_count, total_classes))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cur.fetchone()
        cur.execute("SELECT attendance, total_classes FROM attendance WHERE student_id = %s", (student_id,))
        attendance_data = cur.fetchone()
        conn.close()
        attendance_count = attendance_data[0] if attendance_data else 0
        total_classes = attendance_data[1] if attendance_data else 0
        return render_template('attendance.html', student=student, attendance=attendance_count, total_classes=total_classes)

# --- Results Management ---
@app.route('/admin/results/<int:student_id>', methods=['GET', 'POST'])
def results(student_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        subject = request.form['subject']
        marks = int(request.form['marks'])
        cur.execute("INSERT INTO results (student_id, subject, marks) VALUES (%s, %s, %s)",
                    (student_id, subject, marks))
        conn.commit()
        conn.close()
        return redirect(url_for('results', student_id=student_id))
    else:
        cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cur.fetchone()
        cur.execute("SELECT id, subject, marks FROM results WHERE student_id = %s", (student_id,))
        results = cur.fetchall()
        conn.close()
        return render_template('results.html', student=student, results=results)

# --- Delete Result ---
@app.route('/admin/delete_result/<int:result_id>/<int:student_id>')
def delete_result(result_id, student_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM results WHERE id = %s", (result_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('results', student_id=student_id))

# --- Student Login ---
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        roll = request.form['roll']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE roll = %s", (roll,))
        student = cur.fetchone()
        if student:
            session['student'] = student[0]
            return redirect(url_for('student_dashboard'))
        return render_template('student_login.html', error="Invalid Roll No")
    return render_template('student_login.html')

# --- Student Dashboard ---
@app.route('/student/dashboard')
def student_dashboard():
    if not session.get('student'):
        return redirect(url_for('student_login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE id = %s", (session['student'],))
    student = cur.fetchone()
    cur.execute("SELECT attendance, total_classes FROM attendance WHERE student_id = %s", (session['student'],))
    attendance = cur.fetchone()
    cur.execute("SELECT subject, marks FROM results WHERE student_id = %s", (session['student'],))
    results = cur.fetchall()
    conn.close()
    if attendance:
        percentage = round((attendance[0] / attendance[1]) * 100, 2) if attendance[1] > 0 else 0
    else:
        percentage = 0
    return render_template('student_dashboard.html', student=student, percentage=percentage, results=results)

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
