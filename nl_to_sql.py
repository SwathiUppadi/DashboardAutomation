import os
import json
import sqlite3
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db_schema(db_path):
    """Extract database schema from SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_info = {}
    
    for table in tables:
        table_name = table[0]
        
        # Skip SQLite internal tables
        if table_name.startswith('sqlite_'):
            continue
            
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # Format column information
        column_info = []
        for col in columns:
            column_info.append({
                "name": col[1],
                "type": col[2],
                "primary_key": bool(col[5])
            })
        
        schema_info[table_name] = column_info
    
    conn.close()
    return schema_info

def get_foreign_keys(db_path):
    """Extract foreign key relationships from SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    foreign_keys = {}
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        
        # Skip SQLite internal tables
        if table_name.startswith('sqlite_'):
            continue
            
        # Get foreign key information
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        fkeys = cursor.fetchall()
        
        if fkeys:
            foreign_keys[table_name] = []
            for fk in fkeys:
                foreign_keys[table_name].append({
                    "id": fk[0],
                    "seq": fk[1],
                    "table": fk[2],
                    "from": fk[3],
                    "to": fk[4],
                })
    
    conn.close()
    return foreign_keys

def create_schema_description(schema_info, foreign_keys):
    """Create a human-readable description of the database schema."""
    description = "Database Schema:\n\n"
    
    for table_name, columns in schema_info.items():
        description += f"Table: {table_name}\n"
        description += "Columns:\n"
        
        for col in columns:
            pk_marker = " (Primary Key)" if col["primary_key"] else ""
            description += f"  - {col['name']}: {col['type']}{pk_marker}\n"
        
        # Add foreign key information if available
        if table_name in foreign_keys and foreign_keys[table_name]:
            description += "Foreign Keys:\n"
            for fk in foreign_keys[table_name]:
                description += f"  - {fk['from']} references {fk['table']}({fk['to']})\n"
        
        description += "\n"
    
    return description

def convert_to_sql(user_query, db_path):
    """Convert natural language query to SQL using OpenAI."""
    # Get database schema
    schema_info = get_db_schema(db_path)
    foreign_keys = get_foreign_keys(db_path)
    schema_description = create_schema_description(schema_info, foreign_keys)
    
    # Prepare the prompt for the API
    prompt = f"""
You are an expert SQL assistant for HR managers. 
Your task is to convert natural language questions into SQL queries.

The database schema is as follows:

{schema_description}

Please generate a SQL query to answer the following question from the HR manager:
"{user_query}"

Return only the SQL query without any explanation or commentary.
The SQL should be compatible with SQLite.
Include proper JOINs where needed based on the foreign key relationships.
Make sure to handle any aggregations, groupings, or calculations that might be required.
If the query is asking for a visualization recommendation, still provide the appropriate SQL query to fetch the data needed for that visualization.
"""

    # Call the OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert SQL assistant that translates natural language to SQL."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=500
        )
        
        # Extract and return the SQL query
        sql_query = response.choices[0].message.content.strip()
        return sql_query
    
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def execute_sql(sql_query, db_path):
    """Execute SQL query and return results."""
    try:
        conn = sqlite3.connect(db_path)
        import pandas as pd
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error executing SQL: {str(e)}"

def get_visualization_recommendation(query, data):
    """Get visualization recommendation based on query and data."""
    # Prepare the prompt
    data_sample = data.head(5).to_json(orient='records')
    data_info = f"Number of rows: {len(data)}, Number of columns: {len(data.columns)}"
    column_types = data.dtypes.astype(str).to_dict()
    
    prompt = f"""
You are an expert data visualization assistant for HR managers.
Based on the following query and dataset, recommend the best visualization type to use.

Query: "{query}"

Data Information:
{data_info}

Column Types:
{json.dumps(column_types, indent=2)}

Sample Data:
{data_sample}

Please provide:
1. The recommended visualization type (bar chart, line chart, scatter plot, pie chart, heatmap, etc.)
2. A brief explanation of why this visualization is appropriate for this data
3. Any key configuration suggestions (axis variables, grouping, etc.)

Response format:
{{
  "visualization_type": "type",
  "explanation": "explanation",
  "configuration": {{
    "x_axis": "column_name",
    "y_axis": "column_name",
    "group_by": "column_name" (if applicable),
    "additional_params": {{}}
  }}
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert data visualization assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        recommendation = json.loads(response.choices[0].message.content)
        return recommendation
    
    except Exception as e:
        return {"error": f"Error generating visualization recommendation: {str(e)}"}
