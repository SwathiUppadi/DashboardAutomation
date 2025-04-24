-- HR Database Schema

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone_number TEXT,
    hire_date DATE NOT NULL,
    job_id INTEGER,
    salary NUMERIC(10, 2),
    commission_pct NUMERIC(4, 2),
    manager_id INTEGER,
    department_id INTEGER,
    gender TEXT,
    age INTEGER,
    education_level TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL,
    manager_id INTEGER,
    location_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    job_id INTEGER PRIMARY KEY,
    job_title TEXT NOT NULL,
    min_salary NUMERIC(10, 2),
    max_salary NUMERIC(10, 2)
);

-- Job history table
CREATE TABLE IF NOT EXISTS job_history (
    employee_id INTEGER,
    start_date DATE,
    end_date DATE,
    job_id INTEGER,
    department_id INTEGER,
    PRIMARY KEY (employee_id, start_date),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Locations table
CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY,
    street_address TEXT,
    postal_code TEXT,
    city TEXT NOT NULL,
    state_province TEXT,
    country_id INTEGER
);

-- Performance Reviews table
CREATE TABLE IF NOT EXISTS performance_reviews (
    review_id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    review_date DATE,
    reviewer_id INTEGER,
    performance_score NUMERIC(3, 2),  -- Scale of 1.00 to 5.00
    comments TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (reviewer_id) REFERENCES employees(employee_id)
);

-- Training Programs table
CREATE TABLE IF NOT EXISTS training_programs (
    program_id INTEGER PRIMARY KEY,
    program_name TEXT NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    cost NUMERIC(10, 2)
);

-- Employee Training table (junction table)
CREATE TABLE IF NOT EXISTS employee_training (
    employee_id INTEGER,
    program_id INTEGER,
    completion_date DATE,
    certification_received BOOLEAN,
    PRIMARY KEY (employee_id, program_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (program_id) REFERENCES training_programs(program_id)
);

-- Leave Requests table
CREATE TABLE IF NOT EXISTS leave_requests (
    request_id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    request_date DATE,
    start_date DATE,
    end_date DATE,
    leave_type TEXT,  -- e.g., 'Vacation', 'Sick', 'Personal', etc.
    status TEXT,      -- e.g., 'Pending', 'Approved', 'Rejected'
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    attendance_date DATE,
    clock_in TIME,
    clock_out TIME,
    status TEXT,  -- e.g., 'Present', 'Absent', 'Late'
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
