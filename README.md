# HR Insights Dashboard

A text-to-SQL interactive dashboard for HR managers and team leaders, allowing them to get actionable insights from HR data through natural language queries.

## Problem Statement

HR managers and team leaders often struggle to get actionable insights from static BI tool dashboards. They typically:
- Lack technical expertise to write SQL queries
- Have increased dependency on analysts
- May work at companies without dedicated data analysts
- Need quick answers to specific HR-related questions

This application solves these challenges by providing a user-friendly interface where users can ask questions in natural language and receive visualized answers.

## Features

- **Natural Language to SQL Conversion**: Ask questions in plain English
- **Interactive Data Visualization**: Automatically generates appropriate charts and graphs
- **Data Table View**: Browse the raw data behind the visualizations
- **SQL Query Transparency**: View the SQL queries generated from your questions
- **Insights Analysis**: Get automatically generated insights about your data
- **Sample Queries**: Pre-built questions to get started quickly
- **Query History**: Keep track of your previous questions
- **Data Export**: Download query results as CSV files

## Technical Architecture

The application consists of several components:

1. **Streamlit Frontend**: User interface for query input and data visualization
2. **Natural Language to SQL Converter**: Converts user questions to SQL using OpenAI's GPT models
3. **SQLite Database**: Sample HR database with realistic data
4. **Visualization Engine**: Automatically selects and generates the most appropriate visualization
5. **Insights Generator**: Analyzes results to provide additional context and takeaways

## Setup Instructions

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd DashboardAutomation
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key (either in the web interface or via environment variable):
```bash
export OPENAI_API_KEY=your_api_key_here
```

### Running the Application

1. Initialize the sample database (this happens automatically on first run):
```bash
python sample_data.py
```

2. Start the Streamlit server:
```bash
streamlit run app.py
```

3. Open your browser and navigate to `http://localhost:8501`

## Sample Queries

Here are some example questions you can ask:

- "Show me department-wise employee count"
- "What's the average salary by job title?"
- "Which employees have the highest performance reviews?"
- "Show me the attendance trends for the past month"
- "What's the distribution of leave requests by type?"
- "Which departments have the highest training completion rates?"
- "Show me employees who are due for a promotion based on performance"
- "What's the gender diversity across departments?"
- "Which employees have been absent the most in the last 30 days?"
- "Show me the salary distribution by education level"

## Database Schema

The application uses a sample HR database with the following tables:

- **employees**: Employee personal and job information
- **departments**: Department details
- **jobs**: Job titles and salary ranges
- **job_history**: Historical job assignments
- **locations**: Office locations
- **performance_reviews**: Employee performance evaluations
- **training_programs**: Available training courses
- **employee_training**: Employee training completion records
- **leave_requests**: Employee time-off requests
- **attendance**: Daily attendance records

## Customization

To connect to your own HR database:

1. Modify the `get_db_schema()` function in `nl_to_sql.py` to connect to your database
2. Update the database connection strings in `app.py`
3. Adjust the schema description to match your database structure

## License

[MIT License](LICENSE)

## Acknowledgements

- This project uses OpenAI's GPT models for natural language processing
- Visualization powered by Plotly and Matplotlib
- UI built with Streamlit
