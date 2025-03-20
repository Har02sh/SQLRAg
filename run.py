import ollama
import mysql.connector
from mysql.connector import Error

# Database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",         # Replace with your MySQL host
            user="root",     # Replace with your MySQL username
            password="Ha@020102", # Replace with your MySQL password
            database="sample_db"  # Replace with your database name
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    

def generate_sql_query(user_question):
    # Schema information to provide context to the LLM
    schema_context = """
    Table: Contacts
    Columns:
    - id (INT, PRIMARY KEY, AUTO_INCREMENT)
    - name (VARCHAR(100))
    - job_rank (VARCHAR(50))
    - phone_number (VARCHAR(15))
    - address (TEXT)
    """
    
    prompt = f"""Given the following MySQL database schema:
    {schema_context}
    
    Generate a SQL query to answer this question: "{user_question}"
    
    Return ONLY the SQL query without any explanations.
    """
    
    response = ollama.chat(model='mistral:7b', messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])
    
    # Extract just the SQL query from the response
    sql_query = response['message']['content'].strip()
    
    return sql_query


def answer_user_question(user_question):
    try:
        # Generate SQL query using LLM
        sql_query = generate_sql_query(user_question)
        
        # Execute the query
        conn = get_db_connection()
        if not conn:
            return {"question": user_question, "error": "Database connection failed"}
        
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "question": user_question,
            "sql_query": sql_query,
            "results": results
        }
    
    except Error as e:
        return {
            "question": user_question,
            "error": f"MySQL error: {str(e)}"
        }
    except Exception as e:
        return {
            "question": user_question,
            "error": str(e)
        }
    

def main():
    print("Contact Database Query System")
    print("Ask questions about your contacts in natural language")
    
    while True:
        user_question = input("\nYour question (or 'exit' to quit): ")
        
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