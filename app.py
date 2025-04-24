import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from nl_to_sql import convert_to_sql, execute_sql, get_visualization_recommendation
from sample_data import create_database

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
    .viz-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metrics-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        text-align: center;
        min-width: 150px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #616161;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'visualization_history' not in st.session_state:
        st.session_state.visualization_history = []
    if 'generated_sql' not in st.session_state:
        st.session_state.generated_sql = ""
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'openai_api_key_valid' not in st.session_state:
        st.session_state.openai_api_key_valid = False
    if 'db_path' not in st.session_state:
        # Create the database if it doesn't exist
        db_path = create_database()
        st.session_state.db_path = db_path

def check_api_key():
    """Check if OpenAI API key is set and valid."""
    api_key = st.session_state.get('openai_api_key', None)
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.session_state.openai_api_key_valid = True
        return True
    else:
        return False

def render_sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.markdown("## Settings")
        
        # API Key input
        openai_api_key = st.text_input("OpenAI API Key", type="password", key="openai_api_key")
        if st.button("Validate API Key"):
            if check_api_key():
                st.success("API Key is valid!")
            else:
                st.error("Please enter a valid API Key.")
        
        st.markdown("---")
        
        # Sample queries
        st.markdown("## Sample HR Queries")
        sample_queries = [
            "Show me department-wise employee count",
            "What's the average salary by job title?",
            "Which employees have the highest performance reviews?",
            "Show me the attendance trends for the past month",
            "What's the distribution of leave requests by type?",
            "Which departments have the highest training completion rates?",
            "Show me employees who are due for a promotion based on performance",
            "What's the gender diversity across departments?",
            "Which employees have been absent the most in the last 30 days?",
            "Show me the salary distribution by education level"
        ]
        
        for query in sample_queries:
            if st.button(query):
                st.session_state.user_query = query
                st.experimental_rerun()
        
        st.markdown("---")
        
        # Query history section
        st.markdown("## Recent Queries")
        for idx, query in enumerate(st.session_state.query_history[-5:]):
            if st.button(f"{query[:40]}...", key=f"history_{idx}"):
                st.session_state.user_query = query
                st.experimental_rerun()

def generate_visualization(data, recommendation, query):
    """Generate visualization based on recommendation."""
    try:
        viz_type = recommendation.get('visualization_type', '').lower()
        config = recommendation.get('configuration', {})
        
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        group_by = config.get('group_by')
        
        # If columns are not in the data, try to find suitable alternatives
        if x_col and x_col not in data.columns:
            x_col = data.columns[0] if len(data.columns) > 0 else None
        if y_col and y_col not in data.columns:
            # Try to find a numeric column
            numeric_cols = data.select_dtypes(include=['number']).columns
            y_col = numeric_cols[0] if len(numeric_cols) > 0 else data.columns[1] if len(data.columns) > 1 else None
        if group_by and group_by not in data.columns:
            group_by = None
        
        fig = None
        
        # Bar Chart
        if viz_type in ['bar chart', 'bar', 'barplot']:
            if group_by:
                fig = px.bar(
                    data, 
                    x=x_col, 
                    y=y_col, 
                    color=group_by,
                    title=f"{y_col} by {x_col} (grouped by {group_by})",
                    barmode='group'
                )
            else:
                fig = px.bar(
                    data, 
                    x=x_col, 
                    y=y_col,
                    title=f"{y_col} by {x_col}"
                )
        
        # Line Chart
        elif viz_type in ['line chart', 'line', 'lineplot']:
            if group_by:
                fig = px.line(
                    data, 
                    x=x_col, 
                    y=y_col, 
                    color=group_by,
                    title=f"{y_col} over {x_col} (by {group_by})"
                )
            else:
                fig = px.line(
                    data, 
                    x=x_col, 
                    y=y_col,
                    title=f"{y_col} over {x_col}"
                )
        
        # Pie Chart
        elif viz_type in ['pie chart', 'pie', 'donut', 'donut chart']:
            fig = px.pie(
                data, 
                names=x_col, 
                values=y_col,
                title=f"Distribution of {y_col} by {x_col}"
            )
        
        # Scatter Plot
        elif viz_type in ['scatter plot', 'scatter', 'scatterplot']:
            if group_by:
                fig = px.scatter(
                    data, 
                    x=x_col, 
                    y=y_col, 
                    color=group_by,
                    title=f"{y_col} vs {x_col} (colored by {group_by})"
                )
            else:
                fig = px.scatter(
                    data, 
                    x=x_col, 
                    y=y_col,
                    title=f"{y_col} vs {x_col}"
                )
        
        # Box Plot
        elif viz_type in ['box plot', 'box', 'boxplot']:
            if group_by:
                fig = px.box(
                    data, 
                    x=x_col, 
                    y=y_col, 
                    color=group_by,
                    title=f"Distribution of {y_col} by {x_col} (grouped by {group_by})"
                )
            else:
                fig = px.box(
                    data, 
                    x=x_col, 
                    y=y_col,
                    title=f"Distribution of {y_col} by {x_col}"
                )
        
        # Heatmap
        elif viz_type in ['heatmap', 'heat map']:
            pivot_data = data.pivot_table(
                values=y_col, 
                index=x_col, 
                columns=group_by if group_by else None,
                aggfunc='mean'
            )
            
            fig = px.imshow(
                pivot_data,
                title=f"Heatmap of {y_col} by {x_col}" + (f" and {group_by}" if group_by else "")
            )
        
        # Histogram
        elif viz_type in ['histogram', 'hist']:
            if group_by:
                fig = px.histogram(
                    data, 
                    x=x_col, 
                    color=group_by,
                    title=f"Distribution of {x_col} (grouped by {group_by})"
                )
            else:
                fig = px.histogram(
                    data, 
                    x=x_col,
                    title=f"Distribution of {x_col}"
                )
        
        # Default to a table if no suitable visualization is found
        if fig is None:
            st.markdown(f"### Data Table for: {query}")
            return data
        
        # Update layout
        fig.update_layout(
            template="plotly_white",
            height=500,
            margin=dict(l=20, r=20, t=50, b=20),
        )
        
        st.markdown(f"### {recommendation.get('visualization_type')} for: {query}")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        if 'explanation' in recommendation:
            with st.expander("Why this visualization?"):
                st.write(recommendation['explanation'])
        
        return fig
    
    except Exception as e:
        st.error(f"Error generating visualization: {str(e)}")
        st.markdown(f"### Data Table for: {query}")
        return data

def analyze_data(data, query):
    """Provide insights about the data."""
    # Add this function to provide additional insights about the data
    insights = []
    
    # Check if data is not empty
    if data is None or data.empty:
        return ["No data available to analyze."]
    
    # Get basic statistics for numeric columns
    numeric_cols = data.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        for col in numeric_cols:
            try:
                mean_val = data[col].mean()
                max_val = data[col].max()
                min_val = data[col].min()
                median_val = data[col].median()
                
                insights.append(f"**{col}**: Average: {mean_val:.2f}, Min: {min_val:.2f}, Max: {max_val:.2f}, Median: {median_val:.2f}")
            except:
                pass
    
    # Check for interesting patterns in categorical columns
    categorical_cols = data.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        for col in categorical_cols[:3]:  # Limit to avoid too many insights
            try:
                # Get value counts and top values
                value_counts = data[col].value_counts()
                top_value = value_counts.index[0]
                top_count = value_counts.iloc[0]
                total = len(data)
                
                insights.append(f"**{col}**: Most common value is '{top_value}' ({top_count} occurrences, {(top_count/total*100):.1f}% of data)")
            except:
                pass
    
    return insights

def main():
    """Main function to run the Streamlit app."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">HR Insights Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-text">Ask questions about your HR data in natural language</div>', unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()
    
    # Main input area for natural language query
    user_query = st.text_input(
        "Ask a question about your HR data",
        key="user_query",
        placeholder="e.g., Show me department-wise employee count"
    )
    
    # Process the query
    if user_query:
        # Check API key before processing
        if not check_api_key():
            st.error("Please enter your OpenAI API key in the sidebar.")
            return
        
        # Add to query history if it's a new query
        if user_query not in st.session_state.query_history:
            st.session_state.query_history.append(user_query)
        
        with st.spinner("Processing your request..."):
            # Convert natural language to SQL
            sql_query = convert_to_sql(user_query, st.session_state.db_path)
            st.session_state.generated_sql = sql_query
            
            # Execute SQL and get results
            if not sql_query.startswith("Error"):
                result_data = execute_sql(sql_query, st.session_state.db_path)
                st.session_state.current_data = result_data
                
                # If we have data, display it
                if not isinstance(result_data, str):  # Not an error message
                    # Get visualization recommendation
                    viz_recommendation = get_visualization_recommendation(user_query, result_data)
                    
                    # Display results in tabs
                    tab1, tab2, tab3, tab4 = st.tabs(["Visualization", "Data Table", "SQL Query", "Insights"])
                    
                    with tab1:
                        if not isinstance(viz_recommendation, dict) or 'error' in viz_recommendation:
                            st.error("Could not generate visualization recommendation. Showing data table instead.")
                            st.dataframe(result_data, use_container_width=True)
                        else:
                            generate_visualization(result_data, viz_recommendation, user_query)
                    
                    with tab2:
                        st.markdown(f"### Data for: {user_query}")
                        st.dataframe(result_data, use_container_width=True)
                        
                        # Download button for CSV
                        csv = result_data.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name="hr_data_export.csv",
                            mime="text/csv",
                        )
                    
                    with tab3:
                        st.markdown("### Generated SQL Query")
                        st.code(sql_query, language="sql")
                    
                    with tab4:
                        st.markdown("### Data Insights")
                        insights = analyze_data(result_data, user_query)
                        for insight in insights:
                            st.markdown(insight)
                else:
                    st.error(result_data)
            else:
                st.error(sql_query)
    
    # Display a welcome message or dashboard overview when no query is active
    else:
        st.markdown('<div class="highlight">', unsafe_allow_html=True)
        st.markdown("### 👋 Welcome to the HR Insights Dashboard")
        st.markdown("""
        This interactive dashboard allows HR managers and team leaders to get insights from their HR data using simple natural language questions. No SQL knowledge required!
        
        **How to use:**
        1. Enter your OpenAI API key in the sidebar
        2. Type a question in the search bar above or select from sample queries
        3. View the results as visualizations, tables, or download as CSV
        
        **Example questions you can ask:**
        - "Which department has the highest turnover rate?"
        - "Show me the average salary by job title"
        - "Display attendance patterns across departments"
        - "Which employees are due for a performance review?"
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display some key metrics when no query is active
        st.markdown('<div class="sub-header">HR Dashboard Overview</div>', unsafe_allow_html=True)
        
        # Get some basic metrics from the database
        if st.session_state.get('db_path'):
            conn = sqlite3.connect(st.session_state.db_path)
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
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{total_employees}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Total Employees</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{dept_count}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Departments</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">${avg_salary:,.2f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Avg. Salary</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{training_count}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Training Programs</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col5:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{pending_leaves}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Pending Leaves</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Show some example charts
            st.markdown('<div class="sub-header">Sample Visualizations</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="viz-container">', unsafe_allow_html=True)
                conn = sqlite3.connect(st.session_state.db_path)
                df = pd.read_sql_query("""
                    SELECT d.department_name, COUNT(e.employee_id) as employee_count
                    FROM employees e
                    JOIN departments d ON e.department_id = d.department_id
                    GROUP BY d.department_name
                    ORDER BY employee_count DESC
                """, conn)
                conn.close()
                
                fig = px.bar(
                    df, 
                    x='department_name', 
                    y='employee_count',
                    title="Employees by Department",
                    labels={'department_name': 'Department', 'employee_count': 'Number of Employees'}
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="viz-container">', unsafe_allow_html=True)
                conn = sqlite3.connect(st.session_state.db_path)
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
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
