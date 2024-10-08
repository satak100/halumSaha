from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# Get the PostgreSQL URL from the environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Connect to the PostgreSQL database
def connect_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

# Create the table in the database (run only once)
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PTP_FORM (
            id SERIAL PRIMARY KEY,
            project TEXT,
            contractor TEXT,
            location TEXT,
            task TEXT,
            ptp_number TEXT,
            name_role TEXT,
            date DATE,
            steps TEXT[],
            hazards TEXT[],
            controls TEXT[],
            responsible_staff TEXT,
            crew_activity TEXT[],
            hazard TEXT[],
            action_plan TEXT[],
            coordinating_staff TEXT,
            checkbox_info TEXT[]  -- Store checked information
        )
    ''')
    conn.commit()
    conn.close()

# Home route to display the form
@app.route('/')
def index():
    return render_template('form.html')

# Handle form submissions and store them in the database
@app.route('/submit', methods=['POST'])
def submit_form():
    project = request.form['project']
    contractor = request.form['contractor']
    location = request.form['location']
    task = request.form['task']
    ptp_number = request.form['ptp-number']
    name_role = request.form['name-role']
    date = request.form['date']
    
    # Handle steps, hazards, and controls
    steps = [request.form.get(f'steps_{i}') for i in range(1, 5)]
    hazards = [request.form.get(f'hazards_{i}') for i in range(1, 5)]
    controls = [request.form.get(f'control_{i}') for i in range(1, 5)]

    responsible_staff = request.form['responsibleStaff']
    
    crew_activity = [request.form.get(f'crew_activity_{i}') for i in range(1, 4)]
    hazard = [request.form.get(f'Hazard_{i}') for i in range(1, 4)]
    action_plan = [request.form.get(f'action_plan_{i}') for i in range(1, 4)]


    coordinating_staff = request.form['coordinatingStaff']

    # Handle checkbox values
    checkbox_info = []
    for i in range(1, 10):
        cb = True if request.form.get(f'checkbox{i}') else False
        checkbox_info.append(cb)

    print(steps, checkbox_info)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO PTP_FORM (project, contractor, location, task, ptp_number, name_role, date, steps, hazards, controls, responsible_staff, crew_activity, hazard, action_plan, coordinating_staff, checkbox_info) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (project, contractor, location, task, ptp_number, name_role, date, steps, hazards, controls, responsible_staff, crew_activity, hazard, action_plan, coordinating_staff, checkbox_info))
    
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# View all form submissions
@app.route('/view')
def view_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PTP_FORM")
    rows = cursor.fetchall()
    conn.close()
    return render_template('view_data.html', rows=rows)

if __name__ == '__main__':
    create_table()  # Create the table when starting the app
    app.run(debug=True)
