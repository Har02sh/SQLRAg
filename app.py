import ollama
import sqlite3  # or another DB connector like mysql-connector-python

# Database connection
def get_db_connection():
    conn = sqlite3.connect('sample_db.db')  # Replace with your actual DB
    conn.row_factory = sqlite3.Row
    return conn


def generate_sql_query(user_question):
    # Schema information to provide context to the LLM
    schema_context = """
    Table: Contacts
    Columns:
    - id (INT, PRIMARY KEY, AUTO_INCREMENT)
    - name (VARCHAR(100))
    - rank (VARCHAR(50))
    - phone_number (VARCHAR(15))
    - address (TEXT)
    """
    
    prompt = f"""Given the following database schema:
    {schema_context}
    
    Generate a SQL query to answer this question: "{user_question}"
    
    Important: Return ONLY the raw SQL query with NO markdown formatting, NO backticks, and NO explanations.
    """
    
    response = ollama.chat(model='mistral:7b', messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])
    
    # Extract just the SQL query from the response and clean it
    sql_query = response['message']['content'].strip()
    
    # Remove markdown code formatting if present
    if sql_query.startswith("```"):
        # Find the end of the first line to skip language identifier
        first_line_end = sql_query.find('\n')
        if first_line_end != -1:
            # Find the end of the code block
            code_end = sql_query.rfind("```")
            if code_end > first_line_end:
                # Extract just the code
                sql_query = sql_query[first_line_end+1:code_end].strip()
    
    # Additional cleanup - remove any remaining backticks
    sql_query = sql_query.replace('`', '')
    
    return sql_query


def answer_user_question(user_question):
    try:
        # Generate SQL query using LLM
        sql_query = generate_sql_query(user_question)
        print("THe sql_query is baby: ",sql_query)
        # For safety, you might want to validate the SQL query here
        # or implement restrictions to prevent harmful queries
        
        # Execute the query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        
        # Format results
        formatted_results = [dict(row) for row in results]
        
        return {
            "question": user_question,
            "sql_query": sql_query,
            "results": formatted_results
        }
    
    except Exception as e:
        return {
            "question": user_question,
            "error": str(e)
        }
    

def main():
    while True:
        user_question = input("\nAsk a question about your contacts (or 'exit' to quit): ")
        
        if user_question.lower() == 'exit':
            break
            
        response = answer_user_question(user_question)
        
        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            print(f"\nSQL Query: {response['sql_query']}")
            print("\nResults:")
            for item in response['results']:
                print(item)

if __name__ == "__main__":
    main()