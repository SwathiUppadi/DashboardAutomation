import sqlite3
import datetime
import random
import os

def create_database():
    # Create database file
    db_path = os.path.join(os.path.dirname(__file__), 'hr_database.db')
    
    # Remove if exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read schema from file
    with open(os.path.join(os.path.dirname(__file__), 'hr_schema.sql'), 'r') as schema_file:
        schema_script = schema_file.read()
    
    # Execute schema script by splitting on semicolons
    for statement in schema_script.split(';'):
        if statement.strip():
            cursor.execute(statement)
    
    # Insert sample data
    
    # Locations
    locations = [
        (1, '123 Main St', '12345', 'New York', 'NY', 1),
        (2, '456 Market St', '94103', 'San Francisco', 'CA', 1),
        (3, '789 King St', 'M5V 1M4', 'Toronto', 'ON', 2),
        (4, '101 Tech Park', '560001', 'Bangalore', 'Karnataka', 3),
        (5, '202 Business Ave', '100020', 'Shanghai', 'SH', 4)
    ]
    cursor.executemany('INSERT INTO locations VALUES (?, ?, ?, ?, ?, ?)', locations)
    
    # Departments
    departments = [
        (1, 'Executive', None, 1),
        (2, 'IT', None, 2),
        (3, 'HR', None, 1),
        (4, 'Marketing', None, 2),
        (5, 'Finance', None, 1),
        (6, 'Operations', None, 3),
        (7, 'Sales', None, 4),
        (8, 'Research', None, 5)
    ]
    cursor.executemany('INSERT INTO departments VALUES (?, ?, ?, ?)', departments)
    
    # Jobs
    jobs = [
        (1, 'CEO', 250000.00, 500000.00),
        (2, 'CTO', 180000.00, 300000.00),
        (3, 'HR Manager', 90000.00, 150000.00),
        (4, 'HR Specialist', 60000.00, 90000.00),
        (5, 'IT Manager', 100000.00, 170000.00),
        (6, 'Senior Developer', 90000.00, 140000.00),
        (7, 'Junior Developer', 60000.00, 85000.00),
        (8, 'Marketing Director', 110000.00, 180000.00),
        (9, 'Marketing Specialist', 55000.00, 85000.00),
        (10, 'Finance Manager', 100000.00, 160000.00),
        (11, 'Accountant', 65000.00, 95000.00),
        (12, 'Operations Manager', 90000.00, 150000.00),
        (13, 'Operations Analyst', 55000.00, 85000.00),
        (14, 'Sales Manager', 100000.00, 180000.00),
        (15, 'Sales Representative', 50000.00, 120000.00),
        (16, 'Research Director', 120000.00, 200000.00),
        (17, 'Research Scientist', 75000.00, 130000.00)
    ]
    cursor.executemany('INSERT INTO jobs VALUES (?, ?, ?, ?)', jobs)
    
    # Employees (first round for managers)
    now = datetime.datetime.now()
    education_levels = ['High School', 'Associate', 'Bachelor', 'Master', 'PhD']
    
    managers = [
        (1, 'John', 'Smith', 'john.smith@company.com', '555-123-4567', 
         (now - datetime.timedelta(days=365*10)).strftime('%Y-%m-%d'), 
         1, 350000.00, None, None, 1, 'Male', 45, 'Master'),
        (2, 'Jane', 'Doe', 'jane.doe@company.com', '555-234-5678', 
         (now - datetime.timedelta(days=365*8)).strftime('%Y-%m-%d'), 
         2, 220000.00, None, 1, 2, 'Female', 42, 'PhD'),
        (3, 'Michael', 'Wong', 'michael.wong@company.com', '555-345-6789', 
         (now - datetime.timedelta(days=365*7)).strftime('%Y-%m-%d'), 
         3, 120000.00, None, 1, 3, 'Male', 38, 'Master'),
        (4, 'Emily', 'Taylor', 'emily.taylor@company.com', '555-456-7890', 
         (now - datetime.timedelta(days=365*6)).strftime('%Y-%m-%d'), 
         8, 130000.00, None, 1, 4, 'Female', 37, 'Bachelor'),
        (5, 'David', 'Martinez', 'david.martinez@company.com', '555-567-8901', 
         (now - datetime.timedelta(days=365*7)).strftime('%Y-%m-%d'), 
         10, 125000.00, None, 1, 5, 'Male', 40, 'Master'),
        (6, 'Sara', 'Johnson', 'sara.johnson@company.com', '555-678-9012', 
         (now - datetime.timedelta(days=365*5)).strftime('%Y-%m-%d'), 
         12, 115000.00, None, 1, 6, 'Female', 36, 'Bachelor'),
        (7, 'Robert', 'Lee', 'robert.lee@company.com', '555-789-0123', 
         (now - datetime.timedelta(days=365*6)).strftime('%Y-%m-%d'), 
         14, 140000.00, 0.10, 1, 7, 'Male', 39, 'Master'),
        (8, 'Lisa', 'Kim', 'lisa.kim@company.com', '555-890-1234', 
         (now - datetime.timedelta(days=365*4)).strftime('%Y-%m-%d'), 
         16, 150000.00, None, 1, 8, 'Female', 41, 'PhD')
    ]
    cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', managers)
    
    # Update departments with managers
    for i in range(1, 9):
        cursor.execute('UPDATE departments SET manager_id = ? WHERE department_id = ?', (i, i))
    
    # Employees (regular employees)
    employees = []
    employee_id = 9
    for dept_id in range(1, 9):
        dept_size = random.randint(5, 15)
        manager_id = dept_id
        
        for _ in range(dept_size):
            job_id = random.randint(4, 17)
            job_cursor = conn.cursor()
            job_cursor.execute('SELECT min_salary, max_salary FROM jobs WHERE job_id = ?', (job_id,))
            min_salary, max_salary = job_cursor.fetchone()
            
            salary = round(random.uniform(min_salary, max_salary), 2)
            commission_pct = round(random.uniform(0.05, 0.20), 2) if dept_id == 7 else None  # Commission for sales only
            gender = random.choice(['Male', 'Female', 'Non-binary'])
            age = random.randint(22, 60)
            education = random.choice(education_levels)
            
            hire_years_ago = random.randint(1, 10)
            hire_date = (now - datetime.timedelta(days=365*hire_years_ago)).strftime('%Y-%m-%d')
            
            first_names = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda', 
                          'William', 'Elizabeth', 'David', 'Susan', 'Richard', 'Jessica', 'Joseph', 'Sarah',
                          'Thomas', 'Karen', 'Charles', 'Nancy', 'Christopher', 'Lisa', 'Daniel', 'Betty',
                          'Matthew', 'Dorothy', 'Anthony', 'Sandra', 'Mark', 'Ashley', 'Donald', 'Kimberly']
            
            last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson',
                         'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin',
                         'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee',
                         'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez']
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{employee_id}@company.com"
            phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            employees.append(
                (employee_id, first_name, last_name, email, phone, hire_date, job_id, 
                 salary, commission_pct, manager_id, dept_id, gender, age, education)
            )
            employee_id += 1
    
    cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', employees)
    
    # Training Programs
    training_programs = [
        (1, 'Leadership Development', 'Training for emerging leaders', 
         (now - datetime.timedelta(days=180)).strftime('%Y-%m-%d'), 
         (now - datetime.timedelta(days=170)).strftime('%Y-%m-%d'), 
         5000.00),
        (2, 'Technical Skills Workshop', 'Advanced programming techniques', 
         (now - datetime.timedelta(days=150)).strftime('%Y-%m-%d'), 
         (now - datetime.timedelta(days=145)).strftime('%Y-%m-%d'), 
         3000.00),
        (3, 'Communication Skills', 'Effective business communication', 
         (now - datetime.timedelta(days=120)).strftime('%Y-%m-%d'), 
         (now - datetime.timedelta(days=118)).strftime('%Y-%m-%d'), 
         1500.00),
        (4, 'Project Management', 'Agile project management certification', 
         (now - datetime.timedelta(days=90)).strftime('%Y-%m-%d'), 
         (now - datetime.timedelta(days=85)).strftime('%Y-%m-%d'), 
         4000.00),
        (5, 'Diversity and Inclusion', 'Creating inclusive workplace culture', 
         (now - datetime.timedelta(days=60)).strftime('%Y-%m-%d'), 
         (now - datetime.timedelta(days=59)).strftime('%Y-%m-%d'), 
         1000.00)
    ]
    cursor.executemany('INSERT INTO training_programs VALUES (?, ?, ?, ?, ?, ?)', training_programs)
    
    # Employee Training
    employee_training = []
    for program_id in range(1, 6):
        # Randomly select 15-30 employees for each program
        num_participants = random.randint(15, 30)
        participant_ids = random.sample(range(9, employee_id), num_participants)
        
        for emp_id in participant_ids:
            completion_date = (now - datetime.timedelta(days=random.randint(50, 170))).strftime('%Y-%m-%d')
            certification = random.choice([True, False])
            employee_training.append((emp_id, program_id, completion_date, certification))
    
    cursor.executemany('INSERT INTO employee_training VALUES (?, ?, ?, ?)', employee_training)
    
    # Performance Reviews
    performance_reviews = []
    review_id = 1
    
    # For each employee except CEO
    for emp_id in range(2, employee_id):
        # Get manager ID
        cursor.execute('SELECT manager_id FROM employees WHERE employee_id = ?', (emp_id,))
        manager_id = cursor.fetchone()[0]
        
        # Generate 1-3 performance reviews for each employee
        num_reviews = random.randint(1, 3)
        
        for i in range(num_reviews):
            review_date = (now - datetime.timedelta(days=365*i + random.randint(30, 180))).strftime('%Y-%m-%d')
            score = round(random.uniform(2.5, 5.0), 2)
            
            comments = [
                "Consistently meets or exceeds expectations.",
                "Strong performer with excellent communication skills.",
                "Demonstrates great teamwork and initiative.",
                "Needs improvement in meeting deadlines.",
                "Excellent technical skills but could improve leadership.",
                "Shows great potential for growth.",
                "Highly productive and efficient worker.",
                "Needs to work on collaboration skills.",
                "Outstanding contributor to team success.",
                "Requires more attention to detail in deliverables."
            ]
            
            performance_reviews.append((review_id, emp_id, review_date, manager_id, score, random.choice(comments)))
            review_id += 1
    
    cursor.executemany('INSERT INTO performance_reviews VALUES (?, ?, ?, ?, ?, ?)', performance_reviews)
    
    # Leave Requests
    leave_requests = []
    request_id = 1
    leave_types = ['Vacation', 'Sick', 'Personal', 'Family', 'Bereavement', 'Medical']
    statuses = ['Approved', 'Rejected', 'Pending']
    
    # For all employees
    for emp_id in range(1, employee_id):
        # Generate 1-5 leave requests per employee
        num_requests = random.randint(1, 5)
        
        for _ in range(num_requests):
            request_date = (now - datetime.timedelta(days=random.randint(10, 300))).strftime('%Y-%m-%d')
            start_date = (now - datetime.timedelta(days=random.randint(5, 60))).strftime('%Y-%m-%d')
            
            # Duration between 1-14 days
            duration = random.randint(1, 14)
            end_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d') + 
                       datetime.timedelta(days=duration)).strftime('%Y-%m-%d')
            
            leave_type = random.choice(leave_types)
            status = random.choice(statuses)
            
            leave_requests.append((request_id, emp_id, request_date, start_date, end_date, leave_type, status))
            request_id += 1
    
    cursor.executemany('INSERT INTO leave_requests VALUES (?, ?, ?, ?, ?, ?, ?)', leave_requests)
    
    # Attendance (last 30 days)
    attendance = []
    attendance_id = 1
    
    # For all employees
    for emp_id in range(1, employee_id):
        # Generate attendance for last 30 business days
        for day in range(30):
            # Skip weekends (simplified approach)
            if day % 7 in [5, 6]:
                continue
                
            attendance_date = (now - datetime.timedelta(days=day)).strftime('%Y-%m-%d')
            
            # Randomly determine status (mostly present, sometimes late/absent)
            status_prob = random.random()
            if status_prob < 0.1:
                status = 'Absent'
                clock_in = None
                clock_out = None
            elif status_prob < 0.2:
                status = 'Late'
                clock_in = f"{random.randint(9, 10)}:{random.randint(0, 59):02d}"
                clock_out = f"{random.randint(17, 19)}:{random.randint(0, 59):02d}"
            else:
                status = 'Present'
                clock_in = f"{random.randint(8, 9)}:{random.randint(0, 30):02d}"
                clock_out = f"{random.randint(17, 18)}:{random.randint(0, 59):02d}"
            
            attendance.append((attendance_id, emp_id, attendance_date, clock_in, clock_out, status))
            attendance_id += 1
    
    cursor.executemany('INSERT INTO attendance VALUES (?, ?, ?, ?, ?, ?)', attendance)
    
    # Job History
    job_history = []
    
    # For employees who have been at company for a while (20% chance of having previous positions)
    for emp_id in range(1, employee_id):
        cursor.execute('SELECT hire_date, job_id, department_id FROM employees WHERE employee_id = ?', (emp_id,))
        hire_date_str, current_job_id, current_dept_id = cursor.fetchone()
        hire_date = datetime.datetime.strptime(hire_date_str, '%Y-%m-%d')
        
        # Only add job history if employee has been at company for more than 3 years and passes random check
        years_at_company = (now - hire_date).days / 365
        if years_at_company > 3 and random.random() < 0.2:
            # Previous job 1
            prev_job_id = random.randint(4, 17)  # Pick a random job
            prev_dept_id = random.randint(1, 8)  # Pick a random department
            
            start_date = hire_date.strftime('%Y-%m-%d')
            end_date = (hire_date + datetime.timedelta(days=365*random.randint(1, 2))).strftime('%Y-%m-%d')
            
            job_history.append((emp_id, start_date, end_date, prev_job_id, prev_dept_id))
            
            # Current job is the second job
            start_date = end_date
            job_history.append((emp_id, start_date, None, current_job_id, current_dept_id))
    
    cursor.executemany('INSERT INTO job_history VALUES (?, ?, ?, ?, ?)', job_history)
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Database created at {db_path}")
    return db_path

if __name__ == "__main__":
    create_database()
