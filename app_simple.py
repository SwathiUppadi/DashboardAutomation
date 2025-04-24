import os
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# Set page configuration
st.set_page_config(
    page_title="HR Insights Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #424242;
        margin-bottom: 1rem;
    }
    .info-text {
        font-size: 1rem;
        color: #616161;
    }
    .highlight {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def execute_query(query, db_path):
    """Execute SQL query and return results as DataFrame."""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return None

def main():
    st.markdown('<div class="main-header">HR Insights Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-text">Simplified version to explore HR data</div>', unsafe_allow_html=True)
    
    # Define database path
    db_path = os.path.join(os.path.dirname(__file__), 'hr_database.db')
    
    # Sidebar
    with st.sidebar:
        st.markdown("## Sample Queries")
        
        sample_queries = {
            "Employee count by department": """
                SELECT d.department_name, COUNT(e.employee_id) as employee_count
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                GROUP BY d.department_name
                ORDER BY employee_count DESC
            """,
            "Average salary by job title": """
                SELECT j.job_title, AVG(e.salary) as avg_salary
                FROM employees e
                JOIN jobs j ON e.job_id = j.job_id
                GROUP BY j.job_title
                ORDER BY avg_salary DESC
            """,
            "Top performers": """
                SELECT e.first_name || ' ' || e.last_name as employee_name, 
                       j.job_title, 
                       d.department_name, 
                       AVG(pr.performance_score) as avg_score
                FROM employees e
                JOIN jobs j ON e.job_id = j.job_id
                JOIN departments d ON e.department_id = d.department_id
                JOIN performance_reviews pr ON e.employee_id = pr.employee_id
                GROUP BY e.employee_id
                ORDER BY avg_score DESC
                LIMIT 10
            """,
            "Training program participation": """
                SELECT tp.program_name, 
                       COUNT(et.employee_id) as participants,
                       SUM(CASE WHEN et.certification_received = 1 THEN 1 ELSE 0 END) as certifications
                FROM training_programs tp
                LEFT JOIN employee_training et ON tp.program_id = et.program_id
                GROUP BY tp.program_name
                ORDER BY participants DESC
            """,
            "Leave requests by type": """
                SELECT leave_type, COUNT(*) as request_count
                FROM leave_requests
                GROUP BY leave_type
                ORDER BY request_count DESC
            """,
            "Gender diversity by department": """
                SELECT d.department_name, 
                       e.gender, 
                       COUNT(*) as employee_count
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                GROUP BY d.department_name, e.gender
                ORDER BY d.department_name, e.gender
            """,
            "Attendance status summary": """
                SELECT status, COUNT(*) as count
                FROM attendance
                GROUP BY status
                ORDER BY count DESC
            """,
            "Salary distribution by education": """
                SELECT education_level, 
                       AVG(salary) as avg_salary,
                       MIN(salary) as min_salary,
                       MAX(salary) as max_salary
                FROM employees
                GROUP BY education_level
                ORDER BY avg_salary DESC
            """
        }
        
        selected_query = st.selectbox("Select a sample query", list(sample_queries.keys()))
        
        if st.button("Run Query"):
            query = sample_queries[selected_query]
            st.session_state.current_query = query
            st.session_state.query_name = selected_query
    
    # Main content
    if 'current_query' in st.session_state:
        query = st.session_state.current_query
        query_name = st.session_state.query_name
        
        st.markdown(f"## {query_name}")
        with st.expander("View SQL Query"):
            st.code(query, language="sql")
        
        # Execute query
        df = execute_query(query, db_path)
        
        if df is not None and not df.empty:
            # Display results in tabs
            tab1, tab2 = st.tabs(["Visualization", "Data Table"])
            
            with tab1:
                # Automatic visualization based on query and data
                if "department" in query_name.lower() and "count" in query_name.lower():
                    fig = px.bar(df, x=df.columns[0], y=df.columns[1], 
                                title=f"{query_name}",
                                labels={df.columns[0]: "Department", df.columns[1]: "Count"})
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif "salary" in query_name.lower() and "job" in query_name.lower():
                    fig = px.bar(df, x=df.columns[0], y=df.columns[1], 
                                title=f"{query_name}",
                                labels={df.columns[0]: "Job Title", df.columns[1]: "Average Salary"})
                    st.plotly_chart(fig, use_container_width=True)
                
                elif "performance" in query_name.lower() or "performer" in query_name.lower():
                    fig = px.bar(df, x=df.columns[0], y=df.columns[3], 
                                color=df.columns[2],
                                title=f"{query_name}",
                                labels={df.columns[0]: "Employee", df.columns[3]: "Average Score"})
                    st.plotly_chart(fig, use_container_width=True)
                
                elif "training" in query_name.lower():
                    fig = px.bar(df, x=df.columns[0], y=[df.columns[1], df.columns[2]], 
                                barmode="group",
                                title=f"{query_name}",
                                labels={df.columns[0]: "Program", "value": "Count", "variable": "Type"})
                    st.plotly_chart(fig, use_container_width=True)
                
                elif "leave" in query_name.lower():
                    fig = px.pie(df, names=df.columns[0], values=df.columns[1], 
                                title=f"{query_name}")
                    st.plotly_chart(fig, use_container_width=True)
                
                elif "gender" in query_name.lower() and "diversity" in query_name.lower():
                    fig = px.bar(df, x=df.columns[0], y=df.columns[2], 
                                color=df.columns[1],
                                barmode="group",
                                title=f"{query_name}",
                                labels={df.columns[0]: "Department", df.columns[2]: "Count", df.columns[1]: "Gender"})
                    st.plotly_chart(fig, use_container_width=True)
                
                elif "attendance" in query_name.lower():
                    fig = px.pie(df, names=df.columns[0], values=df.columns[1], 
                                title=f"{query_name}")
                    st.plotly_chart(fig, use_container_width=True)
                
                elif "education" in query_name.lower():
                    # Create a bar chart with error bars
                    fig = px.bar(df, x=df.columns[0], y=df.columns[1],
                                error_y=df.columns[3]-df.columns[1],  # Max - Avg
                                error_y_minus=df.columns[1]-df.columns[2],  # Avg - Min
                                title=f"{query_name}",
                                labels={df.columns[0]: "Education Level", df.columns[1]: "Average Salary"})
                    st.plotly_chart(fig, use_container_width=True)
                
                else:
                    # Default to a bar chart for the first two columns
                    fig = px.bar(df, x=df.columns[0], y=df.columns[1], 
                                title=f"{query_name}")
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.dataframe(df, use_container_width=True)
                
                # Download button for CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"{query_name.lower().replace(' ', '_')}.csv",
                    mime="text/csv",
                )
    
    else:
        # Display dashboard overview
        st.markdown('<div class="highlight">', unsafe_allow_html=True)
        st.markdown("### 👋 Welcome to the HR Insights Dashboard")
        st.markdown("""
        This simplified dashboard allows HR managers and team leaders to get insights from their HR data using pre-defined queries.
        
        **How to use:**
        1. Select a sample query from the sidebar
        2. Click "Run Query" to execute it
        3. View the results as visualizations or tables
        4. Download results as CSV if needed
        
        Select a query from the sidebar to get started!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display some key metrics
        st.markdown('<div class="sub-header">HR Dashboard Overview</div>', unsafe_allow_html=True)
        
        # Get some basic metrics from the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Total Employees
        cursor.execute("SELECT COUNT(*) FROM employees")
        total_employees = cursor.fetchone()[0]
        
        # Departments Count
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        
        # Average Salary
        cursor.execute("SELECT AVG(salary) FROM employees")
        avg_salary = cursor.fetchone()[0]
        
        # Training Programs
        cursor.execute("SELECT COUNT(*) FROM training_programs")
        training_count = cursor.fetchone()[0]
        
        # Pending Leave Requests
        cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status = 'Pending'")
        pending_leaves = cursor.fetchone()[0]
        
        # Close connection
        conn.close()
        
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Employees", total_employees)
        
        with col2:
            st.metric("Departments", dept_count)
        
        with col3:
            st.metric("Avg. Salary", f"${avg_salary:,.2f}")
        
        with col4:
            st.metric("Training Programs", training_count)
        
        with col5:
            st.metric("Pending Leaves", pending_leaves)
        
        # Show some example charts
        st.markdown("### Sample Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Department employee counts
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("""
                SELECT d.department_name, COUNT(e.employee_id) as employee_count
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                GROUP BY d.department_name
                ORDER BY employee_count DESC
            """, conn)
            
            fig = px.bar(
                df, 
                x='department_name', 
                y='employee_count',
                title="Employees by Department",
                labels={'department_name': 'Department', 'employee_count': 'Number of Employees'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gender distribution
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("""
                SELECT gender, COUNT(*) as count
                FROM employees
                GROUP BY gender
            """, conn)
            conn.close()
            
            fig = px.pie(
                df, 
                names='gender', 
                values='count',
                title="Gender Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
